# -*- coding: utf-8 -*-

from mongorm.database import Database
from mongorm.document import Field
from mongorm.utils import DotDict

VERSION = (0, 4, 3)


class ValidationError(Exception):
    pass

__all__ = ['VERSION', 'Database', 'Field', 'DotDict', 'ValidationError']
