from bson.objectid import ObjectId
from inflection import (
    camelize as camelise,
    underscore
)
import json

from mongorm.utils import DotDict, JSONEncoder


class Field(object):

    @staticmethod
    def required(typ, default=None):
        return (True, typ, default)

    @staticmethod
    def optional(typ):
        return (False, typ, None)

    @staticmethod
    def geo_point():
        return {
            'type': Field.required(basestring),
            'coordinates': [Field.optional(float)]
        }

    @staticmethod
    def geo_line_string():
        return {
            'type': Field.required(basestring),
            'coordinates': [[Field.optional(float)]]
        }

    @staticmethod
    def geo_polygon():
        return {
            'type': Field.required(basestring),
            'coordinates': [[[Field.optional(float)]]]
        }


class GeoJSON(object):

    @staticmethod
    def Position(lng, lat):
        return [float(lng), float(lat)]

    @staticmethod
    def Point(lng, lat):
        return {
            'type': 'Point',
            'coordinates': GeoJSON.Position(lng, lat)
        }

    @staticmethod
    def LineString(*args):
        return {
            'type': 'LineString',
            'coordinates': [pt for pt in args]
        }

    @staticmethod
    def Polygon(*args):
        return {
            'type': 'Polygon',
            'coordinates': [linstr for linstr in args]
        }


def Index(*args, **kwargs):
    return args, kwargs


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
                    varg, vkwarg = v
                    self.ensure_index(*varg, **vkwarg)

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

    @staticmethod
    def __dict_key_process(dct, f, *fargs, **fkwargs):
        if type(dct) is dict:
            for k in dct.keys():
                _k = f(k, *fargs, **fkwargs)
                dct[_k] = Document.__dict_key_process(
                    dct[k], f, *fargs, **fkwargs)
                if _k != k:
                    del dct[k]
            return dct
        elif type(dct) is list:
            for i, v in enumerate(dct):
                dct[i] = Document.__dict_key_process(
                    dct[i], f, *fargs, **fkwargs)
            return dct
        else:
            return dct if type(dct) is not ObjectId else str(dct)

    def dump_dict(self):
        rv = {}
        rv.update(self)
        Document.__dict_key_process(rv, camelise, uppercase_first_letter=False)
        return rv

    def dump_json(self):
        rv = self.dump_dict()
        return JSONEncoder().encode(rv)

    def load_dict(self, d):
        _d = {}
        _d.update(d)
        _d = Document.__dict_key_process(_d, underscore)
        self.update(_d)
        if '_id' in self:
            self._id = ObjectId(self._id)

    def load_json(self, s):
        d = json.loads(s)
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

    def pre_save(self):
        pass

    def post_save(self):
        pass

    @staticmethod
    def __field_verify(spec, dct, _k=''):

        if type(spec) is dict:

            if dct is None:
                return DotDict()

            try:
                f = spec.iteritems
            except AttributeError:
                f = spec.items

            for k, v in f():
                dct[k] = Document.__field_verify(
                    v,
                    dct.get(k, DotDict() if type(v) is dict else None),
                    _k + '.' + k
                )
                if dct[k] is None or dct[k] == {}:
                    del dct[k]

            return dct

        elif type(spec) is list:

            if dct is None:
                return []

            list_spec = spec[0]

            for i, v in enumerate(dct):
                dct[i] = Document.__field_verify(
                    list_spec,
                    v,
                    _k + '[' + str(i) + ']'
                )

            return dct

        elif type(spec) is tuple:

            req, typ, default = spec

            if req and dct is None:
                if default is None:
                    raise KeyError(_k)
                else:
                    dct = default

            if dct is not None:

                if not issubclass(type(dct), typ):
                    try:
                        return typ(dct)
                    except:
                        raise TypeError(_k)

            return dct

    def validate_fields_extra(self, spec):
        self.__class__.__field_verify(spec, self)

    def validate_fields(self):
        if '__fields__' in self.__class__.__dict__:
            self.__class__.__field_verify(
                self.__class__.__fields__,
                self
            )

    def save(self):
        self.pre_save()
        self.validate_fields()
        self.validate()
        self._id = self.__coll__.save(self)
        self.post_save()

    def delete(self):
        self.__coll__.remove(self._id)

    @classmethod
    def find(cls, *args, **kwargs):
        return cls.__coll__.find(*args, as_class=cls, **kwargs)

    @classmethod
    def find_one(cls, *args, **kwargs):
        return cls.__coll__.find_one(*args, as_class=cls, **kwargs)
