"""Spatial statistics library (sstats)
"""
__author__ = "Juan C. Duque, Alejandro Betancourt"
__credits__ = "Copyright (c) 2009-11 Juan C. Duque"
__license__ = "New BSD License"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"

from basic import geoAssociationCoef
from basic import redistributionCoef
from basic import similarityCoef
from inequality import inequalityMultivar
from inequality import globalInequalityChanges
from inequality import interregionalInequalityTest
from inequality import interregionalInequalityDifferences

__all__ = ['geoAssociationCoef', 'redistributionCoef',
           'similarityCoef','inequalityMultivar','globalInequalityChanges',
           'interregionalInequalityTest',
           'interregionalInequalityDifferences']

