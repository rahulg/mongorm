try:
    import simplejson as json
except ImportError:
    import json

from inflection import (
    camelize as camelise,
    underscore
)


# classmethods need access to the db-related stuff
# Nothing a little metaprogramming can't handle.
class BaseDocumentMeta(type):

    INHERIT_FROM_COLLECTION = [
        'count',
        'create_index',
        'ensure_index',
        'drop_index',
        'drop_indexes',
        'index_information',
        'reindex',
        'group',
        'distinct',
        'write_concern',
        'find_and_modify'
    ]

    def __new__(cls, clsname, bases, dct):
        # Use a default collection name derived from class name
        # Children can override it by setting __collection__
        if '__collection__' not in dct:
            dct['__collection__'] = underscore(clsname)
        return super(BaseDocumentMeta, cls).__new__(cls, clsname, bases, dct)

    def __init__(self, clsname, bases, dct):
        super(BaseDocumentMeta, self).__init__(clsname, bases, dct)
        # Set the collection object if we need to
        try:
            self._coll = self._db[self.__collection__]

            for fn in self.INHERIT_FROM_COLLECTION:
                setattr(self, fn, getattr(self._coll, fn))

            if '__indices__' in self.__dict__:
                for v in self.__indices__:
                    self.ensure_index(v)

        except AttributeError:
            # Initial declaration, it won't have an injected _db
            pass


class BaseDocument(dict):

    __metaclass__ = BaseDocumentMeta

    def __init__(self):
        super(BaseDocument, self).__init__()

    def __getattr__(self, key):
        return self.__getitem__(key)

    def __delattr__(self, key):
        del self[key]

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def dump_json(self):
        rv = {}
        for key in self:
            rv[camelise(key, uppercase_first_letter=False)] = self[key]
        return json.dumps(rv, encoding='utf8')

    def load_json(self, s):
        d = json.loads(s, encoding='utf8')
        for key in d:
            self[key] = d[key]

    @classmethod
    def from_json(cls, s):
        rv = cls()
        rv.load_json(s)
        return rv

    def validate(self):
        pass

    @staticmethod
    def _type_match(field, typ):
        return type(field) == typ

    def validate_fields(self):
        if '__fields__' in self.__class__.__dict__:
            for k in self.__fields__:
                typ, default = self.__class__.__fields__[k]

                # Set default field
                if k not in self:
                    self[k] = default

                # Ensure types match
                if not self.__class__._type_match(self[k], typ):
                    raise TypeError

    def save(self):
        self.validate_fields()
        self.validate()
        self._id = self._coll.save(self)

    def delete(self):
        self._coll.remove(self._id)

    @classmethod
    def find(cls, *args, **kwargs):
        return cls._coll.find(*args, as_class=cls, **kwargs)

    @classmethod
    def find_one(cls, *args, **kwargs):
        return cls._coll.find_one(*args, as_class=cls, **kwargs)
