# -*- coding: utf-8 -*-

from mongorm.database import Database
from mongorm.document import Field, Index, GeoJSON
from mongorm.utils import DotDict, JSONEncoder


class ValidationError(Exception):
    pass

__all__ = [
    'ValidationError',
    'Database',
    'Field',
    'Index',
    'GeoJSON',
    'DotDict',
    'JSONEncoder'
]
