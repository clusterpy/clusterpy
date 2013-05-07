# encoding: latin2
"""Data generator module
"""
__author__ = "Juan C. Duque, Alejandro Betancourt"
__credits__ = "Copyright (c) 2009-10 Juan C. Duque"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"

from car import generateCAR
from createVariable import fieldOperation
from dissolvedata import dissolveData
from gBinomial import generateGBinomial
from lBinomial import generateLBinomial
from sar import generateSAR
from sma import generateSMA
from spots import generateSpots
from positive_spots import generatePositiveSpots
from uniform import generateUniform
from spatialLag import spatialLag
