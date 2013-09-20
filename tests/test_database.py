import unittest

from mongorm import Database


class DatabaseTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db = Database(uri='mongodb://localhost:27017/orm_test')
        cls.db2 = Database(host='localhost', port=27017, db='orm_test2')

    @classmethod
    def tearDownClass(cls):
        cls.db.drop()
        cls.db2.drop()

    def test_init_with_uri(self):
        self.assertEquals(self.db.host, 'localhost')
        self.assertEquals(self.db.port, 27017)

    def test_init_with_hostport(self):
        self.assertEquals(self.db2.host, 'localhost')
        self.assertEquals(self.db2.port, 27017)

    def test_default_db(self):
        self.assertEquals(self.db.name, 'orm_test')
        self.assertEquals(self.db2.name, 'orm_test2')

    def test_default_connection(self):
        db = Database()
        self.assertEquals(db.host, 'localhost')
        self.assertEquals(db.port, 27017)
        self.assertEquals(db.name, 'test')

    def test_drop_collection_from_str(self):
        class SomeTestClass(self.db.Document):
            pass

        t = SomeTestClass()
        t.test_val = 44
        t.save()

        colls = self.db.get_collections()
        self.assertIn('some_test_class', colls)

        self.db.drop_collection('some_test_class')
        colls = self.db.get_collections()
        self.assertNotIn('some_test_class', colls)

    def test_drop_collection_from_obj(self):
        class SomeTestClass(self.db.Document):
            pass

        t = SomeTestClass()
        t.test_val = 44
        t.save()

        colls = self.db.get_collections()
        self.assertIn('some_test_class', colls)

        self.db.drop_collection(SomeTestClass)
        colls = self.db.get_collections()
        self.assertNotIn('some_test_class', colls)

    def test_drop_collection_typeerror(self):
        self.assertRaises(
            TypeError,
            self.db.drop_collection,
            5
        )
