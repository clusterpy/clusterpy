"""Spatial statistics library (sstats)
"""
__author__ = "Juan C. Duque, Alejandro Betancourt"
__credits__ = "Copyright (c) 2009-11 Juan C. Duque"
__license__ = "GPL"
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
from indexes import areaChangeIndex
from indexes import translationLocalIndex
from indexes import translationGlobalIndex

__all__ = ['geoAssociationCoef', 'redistributionCoef',
           'similarityCoef','inequalityMultivar','globalInequalityChanges',
           'interregionalInequalityTest', 'interregionalInequalityDifferences',
           'areaChangeIndex', 'translationLocalIndex', 'translationGlobalIndex']

