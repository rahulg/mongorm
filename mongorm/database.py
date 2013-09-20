from pymongo import MongoClient

from mongorm.document import BaseDocument


class Database(object):
    '''
    Represent a MongoDB database, backed by pymongo's MongoClient
    '''

    def __init__(self, **kwargs):
        '''
        Initialise
        '''
        if 'uri' in kwargs:
            self._client = MongoClient(kwargs['uri'])
            if 'db' in kwargs:
                self._db = self._client[kwargs['db']]
            else:
                self._db = self._client.get_default_database()
        else:
            self._client = MongoClient(
                kwargs.get('host', 'localhost'),
                kwargs.get('port', 27017)
            )
            self._db = self._client[kwargs.get('db', 'test')]
        self.Document = type('Document', (BaseDocument,), {'_db': self._db})

    def drop(self):
        self._client.drop_database(self._db.name)

    def drop_collection(self, collection):
        if isinstance(collection, str):
            self._db.drop_collection(collection)
        elif issubclass(collection, BaseDocument):
            self._db.drop_collection(collection.__collection__)
        else:
            raise TypeError

    def get_collections(self, include_system_collections=False):
        return self._db.collection_names(include_system_collections)

    @property
    def host(self):
        return self._client.host

    @property
    def port(self):
        return self._client.port

    @property
    def name(self):
        return self._db.name
