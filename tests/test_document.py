import unittest

from mongorm import Database, Field
import pymongo


class DocumentTestCase(unittest.TestCase):

    sample_json = r'{"hello": "world"}'

    @classmethod
    def setUpClass(cls):
        cls.db = Database(uri='mongodb://localhost:27017/orm_test')

    @classmethod
    def tearDownClass(cls):
        cls.db.drop()

    def setUp(self):
        class SomeTestClass(self.db.Document):
            pass

        self.SomeTestClass = SomeTestClass

    def tearDown(self):
        self.db.drop_collection(self.SomeTestClass)

    def test_load_json(self):
        d = self.SomeTestClass()
        d.load_json(self.sample_json)

        self.assertIn('hello', d)
        self.assertEqual(d.hello, 'world')

    def test_dump_json(self):
        d = self.SomeTestClass()
        d.hello = 'world'

        test_json = d.dump_json()
        self.assertEquals(test_json, self.sample_json)

    def test_from_json(self):
        d = self.SomeTestClass.from_json(self.sample_json)
        self.assertEquals(d.dump_json(), self.sample_json)

    def test_type_match(self):
        tm = self.SomeTestClass._type_match
        self.assertTrue(tm('a', str))
        self.assertTrue(tm(1, int))
        self.assertFalse(tm('a', int))
        self.assertFalse(tm(1, str))

    def test_missing_required_field(self):
        self.SomeTestClass.__fields__ = {
            'hello': Field.required(str, None)
        }

        d = self.SomeTestClass()
        self.assertRaises(KeyError, d.save)

    def test_missing_optional_field(self):
        self.SomeTestClass.__fields__ = {
            'hello': Field.optional(str)
        }

        d = self.SomeTestClass()
        d.save()
        self.assertIn('_id', d)

    def test_validate_fields_type(self):
        self.SomeTestClass.__fields__ = {
            'hello': Field.optional(str)
        }

        d = self.SomeTestClass()
        d.hello = 3

        self.assertRaises(TypeError, d.save)

        d.hello = 'world'
        d.save()

    def test_validate_fields_default(self):
        self.SomeTestClass.__fields__ = {
            'hello': Field.required(str, 'world')
        }

        d = self.SomeTestClass()
        d.save()

        self.assertEqual(d.hello, 'world')

    def test_save(self):
        d = self.SomeTestClass()
        d.hello = 'world'
        d.save()

        self.assertIn('_id', d)

    def test_indices(self):
        class OtherTestClass(self.db.Document):
            __indices__ = [
                'hello',
                [('test', pymongo.ASCENDING)]
            ]

        d = OtherTestClass()
        self.assertEqual(len(d.index_information()), 3)

    def test_load_dump_objid(self):
        d = self.SomeTestClass()
        d.hello = 'world'
        d.save()

        e = self.SomeTestClass()
        e.load_json(d.dump_json())

        self.assertEquals(d._id, e._id)
