# -*- coding: utf-8 -*-

from mongorm.database import Database
from mongorm.document import Field, Index
from mongorm.utils import DotDict

VERSION = (0, 6, 0)


class ValidationError(Exception):
    pass

__all__ = ['VERSION', 'Database', 'Field',
           'Index', 'DotDict', 'ValidationError']
