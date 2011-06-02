# encoding: latin2
"""Data generation modules utilities
"""
__author__ = "Juan C. Duque, Alejandro Betancourt"
__credits__ = "Copyright (c) 2010-11 Juan C. Duque"
__license__ = "New BSD License"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"
__all__ = ['wToMatrix']

import numpy

def wToMatrix(w): 
    """Obtain sparse matrix representation of contiguity dictionary (W)
    
    :param w: contiguity dictionary 
    :type w: dictionary
    :rtype: numpy.matrix (sparse contiguity matrix)
     """
    wMatrix = numpy.zeros((len(w), len(w)))
    for i in w.keys():
        weight = 1.0 / len(w[i])
        for j in w[i]:
            wMatrix[i, j] = weight
    return numpy.matrix(wMatrix)

