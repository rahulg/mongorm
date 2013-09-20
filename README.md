# mongorm

`mongorm` is an extremely thin ODM layer on top of `pymongo` that allows you to create classes that represent MongoDB documents.

It's designed to give you all the flexibility of `pymongo`, with a few convenience features, such as attribute-style (user.name) access to fields.

# Getting Started

The recommended way to install mongorm is to install via pip, `pip install mongorm`

`mongorm` only has a single class for you to import:

```
>>> from mongorm import Database
```

You can connect to a database either via a MongoDB URI:

```
>>> db = Database(uri='mongodb://localhost:27017/some_db')
```

or with a host-port-db combination:

```
>>> db = Database(host='localhost', port=27017, db='some_db')
```

If any of the keyword arguments aren't matched, or if the URI is missing a database name, the following are used as defaults:

* `host`: 'localhost'
* `port`: 27017
* `db`: 'test'

# Database Class

The `Database` class has the following methods:

* `drop`: drops a database
* `drop_collection`: drops a collection
* `get_collections`: gets a list of collections in the database

and the following (read-only) properties:

* `host`: MongoDB host
* `port`: MongoDB port
* `name`: database name

You can access the pymongo `MongoClient` with `db._client` and the `pymongo.database` instance with `db._db`. Eventually, common operations will be accessible from the `db` object itself.

# DotDict

The `DotDict` class is a wrapper around python's default dict that allows attribute-style access to dict key-value pairs. In other words, the following accesses are the same:

```
>>> d = DotDict({'hello': 'world'})
>>> print d['hello']
world
>>> print d.hello
world
```

`mongorm.Document`s inherit from it to gain this feature. If you'd like to be able to refer to your nested documents with an attribute-style access, declare them as `mongorm.DotDict`s instead of {}s.

# Defining Models

With a configured Database, as above, you can declare models as:

```
class SomeClass(db.Document):
    pass
```

These models will inherit the database connection from the `db` instance.

The following demonstrates some of the features of the `Document` class.

```
from mongorm import Field

class User(db.Model):
	# Override the collection name
	# Defaults to the underscored version of the class name
	__collection__ = 'auth_user'

	# Enforce validation on certain fields
	# All fields in this dict are considered required
	__fields__ = {

		# user.username is a required field of type str, without a default
		'username': Field.required(str),

		# user.age is a required field, with a default value
		'age': Field.required(int, 12)

		# user.name is an optional field
		'name': Field.optional(str),

		# Nested document
		'nested': {
			'key_a': Field.required(str),
			'key_b': Field.optional(int)
		}

	}

	# Specify indices
	# These are directly passed to pymongo's collection.ensure_index
	__indices__ = [

		# Normal index over name field
		'name',

		# Descending index over age
		[('age': pymongo.DESCENDING)],

		# Compound index
		[('age', pymongo.DESCENDING), ('name', pymongo.ASCENDING)]

	]

	# Override the validate function
	# This gets called before a save operation
	# Error conditions should throw exceptions
	def validate(self):
		if self.age < 18:
			raise CannotLegallyDrinkError
```

The `Document` class also has some useful/essential methods:

* `dump_json`: dumps `self` as JSON
* `load_json`: updates `self`'s fields from the input JSON
* `save`: saves the document
* `delete`: removes the document from the collection

and the following `@classmethod`s:

* `from_json`: returns a new instance of class constructed with the input JSON
* `find`: calls `pymongo.collection`'s `find`
* `find_one`: calls `pymongo.collection`'s `find_one`

In addition, the following methods are passed on to the `pymongo.collection` instance:

* `count`
* `create_index`
* `ensure_index`
* `drop_index`
* `drop_indexes`
* `index_information`
* `reindex`
* `group`
* `distinct`
* `write_concern`
* `find_and_modify`

Any arguments are passed verbatim to the `pymongo.collection` instance, so please refer to `pymongo`s documentation.

# Contributing

All development happens on [GitHub](https://github.com/rahulg/mongorm). Feel free to report any issues there.

If you wish to contribute code, please note the following:

* The project is BSD-licensed, and is not copyleft
* Please work off the `master` branch, and not any other published branches that might exist
* Make sure you're following conventions
* Github pull requests are fine, as are patches emailed to `r@hul.ag`
