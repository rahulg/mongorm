import simplejson
from bson import ObjectId


class DotDict(dict):

    def __init__(self, *args, **kwargs):
        super(DotDict, self).__init__(*args, **kwargs)
        try:
            dict.__getattribute__(self, 'iteritems')
        except AttributeError:
            dict.__setattr__(
                self,
                'iteritems',
                dict.__getattribute__(self, 'items')
            )

    def __getattr__(self, name):
        if name[:2] == '__':
            return object.__getattribute__(self, name)
        else:
            return self.__getitem__(name)

    def __delattr__(self, name):
        if name[:2] == '__':
            object.__delattr__(self, name)
        else:
            self.__delitem__(name)

    def __setattr__(self, name, value):
        if name[:2] == '__':
            object.__setattr__(self, name, value)
        else:
            self.__setitem__(name, value)


class JSONEncoder(simplejson.JSONEncoder):

    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return simplejson.JSONEncoder.default(self, o)
