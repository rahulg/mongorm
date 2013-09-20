class DotDict(dict):

    def __init__(self, *args, **kwargs):
        super(DotDict, self).__init__(*args, **kwargs)

    def __getattr__(self, key):
        return self.__getitem__(key)

    def __delattr__(self, key):
        del self[key]

    def __setattr__(self, key, value):
        self.__setitem__(key, value)
