# -*- coding: utf-8 -*-

from mongorm.database import Database
from mongorm.document import Field, Index
from mongorm.utils import DotDict, JSONEncoder

VERSION = (0, 6, 3)


class ValidationError(Exception):
    pass

__all__ = [
    'VERSION',
    'ValidationError',
    'Database',
    'Field',
    'Index',
    'DotDict',
    'JSONEncoder'
]
