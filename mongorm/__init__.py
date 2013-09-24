# -*- coding: utf-8 -*-

from mongorm.database import Database
from mongorm.document import Field, Index
from mongorm.utils import DotDict

VERSION = (0, 5, 1)


class ValidationError(Exception):
    pass

__all__ = ['VERSION', 'Database', 'Field',
           'Index', 'DotDict', 'ValidationError']
