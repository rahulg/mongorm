try:
    import simplejson as json
except ImportError:
    import json

from inflection import (
    camelize as camelise,
    underscore
)
from bson.objectid import ObjectId

from mongorm.utils import DotDict


class Field(object):

    @staticmethod
    def required(typ, default=None):
        return (True, typ, default)

    @staticmethod
    def optional(typ):
        return (False, typ, None)


class BaseDocumentMeta(type):

    '''
    classmethods need access to the db-related stuff
    Nothing a little metaprogramming can't handle.
    '''

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

    def __init__(self, clsname, bases, dct):
        super(BaseDocumentMeta, self).__init__(clsname, bases, dct)
        if '__collection__' not in dct:
            self.__collection__ = underscore(clsname)
        # Set the collection object if we need to
        try:
            self.__coll__ = self.__db__[self.__collection__]

            for fn in self.INHERIT_FROM_COLLECTION:
                setattr(self, fn, getattr(self.__coll__, fn))
            if '__indices__' in self.__dict__:
                for v in self.__indices__:
                    self.ensure_index(v)

        except AttributeError:
            # Initial declaration, it won't have an injected __db__
            pass


# This is the only metaclass definition that works with both python3 and python2
BaseDocument = BaseDocumentMeta('BaseDocument', (DotDict, ), {})


class Document(BaseDocument):

    def __init__(self):
        super(Document, self).__init__()

    def dump_json(self):
        rv = {}
        for k in self:
            if k == '_id':
                # Handle ObjectID
                rv[k] = str(self[k])
            else:
                rv[camelise(k, uppercase_first_letter=False)] = self[k]
        return json.dumps(rv, encoding='utf8')

    def load_json(self, s):
        d = json.loads(s, encoding='utf8')
        for k in d:
            new_k = underscore(k)
            self[new_k] = d[k] if k != '_id' else ObjectId(d[k])

    @classmethod
    def from_json(cls, s):
        rv = cls()
        rv.load_json(s)
        if '_id' in rv:
            del rv['_id']
        return rv

    def validate(self):
        pass

    @staticmethod
    def _typecheck(spec, dct):
        for k in spec:

            # Nested document
            if type(spec[k]) == dict:

                new_dict = False
                if not k in dct:
                    # Create the nested doc
                    dct[k] = DotDict()
                    new_dict = True

                Document._typecheck(spec[k], dct[k])

                if new_dict and len(dct[k]) == 0:
                    # All the fields were optional
                    del dct[k]

            # Simple field
            else:

                req, typ, default = spec[k]

                if req and k not in dct:
                    if default is None:
                        raise KeyError
                    # Set default
                    dct[k] = default

                if req or ((not req) and k in dct):
                    # Ensure types match
                    if not type(dct[k]) == typ:
                        raise TypeError

    def validate_fields(self):
        if '__fields__' in self.__class__.__dict__:
            self.__class__._typecheck(self.__class__.__fields__, self)

    def save(self):
        self.validate_fields()
        self.validate()
        self._id = self.__coll__.save(self)

    def delete(self):
        self.__coll__.remove(self._id)

    @classmethod
    def find(cls, *args, **kwargs):
        return cls.__coll__.find(*args, as_class=cls, **kwargs)

    @classmethod
    def find_one(cls, *args, **kwargs):
        return cls.__coll__.find_one(*args, as_class=cls, **kwargs)
