"""Spatial statistics library (sstats)
"""
__author__ = "Juan C. Duque, Alejandro Betancourt"
__credits__ = "Copyright (c) 2009-11 Juan C. Duque"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"

from rimaps import rimap
from statistics import topoStatistics, noFrontiersW
from mrpolygons import mrpolygon, polarPolygon2cartesian

__all__ = ['rimap','topoStatistics','noFrontiersW','mrpolygon']

