from bson.objectid import ObjectId
from inflection import (
    camelize as camelise,
    underscore
)
import simplejson as json

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
        'aggregate',
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


# This is the only metaclass definition that works with both python3 and
# python2
BaseDocument = BaseDocumentMeta('BaseDocument', (DotDict, ), {})


class Document(BaseDocument):

    def __init__(self, *args, **kwargs):
        super(Document, self).__init__()
        d = dict(*args, **kwargs)
        self.load_dict(d)

    def dump_dict(self):
        rv = {}
        for k, v in self.iteritems():
            new_k = camelise(k, uppercase_first_letter=False)
            rv[new_k] = v if type(v) != ObjectId else str(v)
        return rv

    def dump_json(self):
        rv = self.dump_dict()
        return json.dumps(rv, encoding='utf8')

    def load_dict(self, d):
        d = DotDict(d)
        for k, v in d.iteritems():
            new_k = underscore(k)
            self[new_k] = v if k != '_id' else ObjectId(v)

    def load_json(self, s):
        d = json.loads(s, encoding='utf8')
        self.load_dict(d)

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

        if type(spec) == list:

            lspec = spec[0]
            for i in dct:
                Document._typecheck(lspec, i)

        elif type(spec) == tuple:

            req, typ, default = spec

            if not type(dct) == typ:
                raise TypeError

        elif type(spec) == dict:

            for k in spec:

                # Nested document
                if type(spec[k]) == dict:

                    new_dict = False
                    if k not in dct:
                        # Create the nested doc
                        dct[k] = DotDict()
                        new_dict = True

                    Document._typecheck(spec[k], dct[k])

                    if new_dict and len(dct[k]) == 0:
                        # All the fields were optional
                        del dct[k]

                # List
                elif type(spec[k]) == list:

                    new_list = False
                    if k not in dct:
                        # Create the list
                        dct[k] = []
                        new_list = True

                    Document._typecheck(spec[k], dct[k])

                    if new_list and len(dct[k]) == 0:
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

    def validate_fields_extra(self, spec):
        self.__class__._typecheck(spec, self)

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
