from bson import ObjectId
import json


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
        for k, v in self.iteritems():
            self[k] = DotDict.__dotify(v)

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
            value = DotDict.__dotify(value)
            super(DotDict, self).__setitem__(name, value)

    def __setitem__(self, name, value):

        if issubclass(type(value), dict) or issubclass(type(value), list):
            value = DotDict.__dotify(value)

        super(DotDict, self).__setitem__(name, value)

    def update(self, dct):
        try:
            f = dct.iteritems
        except AttributeError:
            f = dct.items

        for k, v in f():
            dct[k] = DotDict.__dotify(v)
        super(DotDict, self).update(dct)

    @staticmethod
    def __dotify(dct):

        if issubclass(type(dct), dict):

            for k, v in DotDict(dct).iteritems():
                dct[k] = DotDict.__dotify(v)

            return DotDict(dct)

        elif issubclass(type(dct), list):

            for i, v in enumerate(dct):
                dct[i] = DotDict.__dotify(v)

            return dct

        else:

            return dct


class JSONEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)
