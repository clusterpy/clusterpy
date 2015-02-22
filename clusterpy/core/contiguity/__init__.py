# encoding: latin2
"""Data generator module
"""
__author__ = "Juan C. Duque, Alejandro Betancourt"
__credits__ = "Copyright (c) 2009-10 Juan C. Duque"
__license__ = "New BSD License"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"

from weightsFromAreas import weightsFromAreas
from intersections import fixIntersections
from transformations import dict2matrix
from transformations import dict2sparseMatrix
from output import dict2gal, dict2csv

