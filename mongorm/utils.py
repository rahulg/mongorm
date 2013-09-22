class DotDict(dict):

    def __init__(self, *args, **kwargs):
        super(DotDict, self).__init__(*args, **kwargs)

    def __getattr__(self, name):
        if name[0] == '__':
            return object.__getattribute__(self, name)
        else:
            return self.__getitem__(name)

    def __delattr__(self, name):
        if name[0] == '__':
            object.__delattr__(self, name)
        else:
            self.__delitem__(name)

    def __setattr__(self, name, value):
        if name[0] == '__':
            object.__setattr__(self, name, value)
        else:
            self.__setitem__(name, value)
