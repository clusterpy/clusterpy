"""Spatial statistics library (sstats)
"""
__author__ = "Juan C. Duque, Alejandro Betancourt"
__credits__ = "Copyright (c) 2009-11 Juan C. Duque"
__license__ = "New BSD License"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"

from inequalityMultivar import inequalityMultivar
from gineqTest import globalInequalityChanges
from regionsTest import interregionalInequalityTest
from regionsDiffTest import interregionalInequalityDifferences

__all__ = ['inequalityMultivar','globalInequalityChanges',
           'interregionalInequalityTest',
           'interregionalInequalityDifferences']

