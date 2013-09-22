from pymongo import MongoClient

from mongorm.document import Document


class Database(object):

    '''
    Represent a MongoDB database, backed by pymongo's MongoClient
    '''

    def __init__(self, **kwargs):
        '''
        Initialise
        '''
        if 'uri' in kwargs:
            self.__client__ = MongoClient(kwargs['uri'])
            if 'db' in kwargs:
                self.__db__ = self.__client__[kwargs['db']]
            else:
                self.__db__ = self.__client__.get_default_database()
        else:
            self.__client__ = MongoClient(
                kwargs.get('host', 'localhost'),
                kwargs.get('port', 27017)
            )
            self.__db__ = self.__client__[kwargs.get('db', 'test')]
        self.Document = type('Document', (Document,), {'__db__': self.__db__})

    def authenticate(self, *args, **kwargs):
        self.__client__.authenticate(*args, **kwargs)

    def drop(self):
        self.__client__.drop_database(self.__db__.name)

    def drop_collection(self, collection):
        if isinstance(collection, str):
            self.__db__.drop_collection(collection)
        elif issubclass(collection, Document):
            self.__db__.drop_collection(collection.__collection__)
        else:
            raise TypeError

    def get_collections(self, include_system_collections=False):
        return self.__db__.collection_names(include_system_collections)

    @property
    def host(self):
        return self.__client__.host

    @property
    def port(self):
        return self.__client__.port

    @property
    def name(self):
        return self.__db__.name
