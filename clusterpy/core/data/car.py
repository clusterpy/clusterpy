# encoding: latin2
"""CAR data generation
"""
__author__ = "Juan C. Duque, Alejandro Betancourt"
__credits__ = "Copyright (c) 2010-11 Juan C. Duque"
__license__ = "New BSD License"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"
__all__ = ['generateCAR']

import numpy
from componentsData import wToMatrix

def generateCAR(w, n, rho):
    """
    This function generates n simulated CAR variables with the same parameters for all features.

    :param w: contiguity matrix
    :type w: dictionary
    :param n: number of variables to be simulated
    :type n: integer
    :param rho: autoregressive parameter for the process
    :type rho: float
    :rtype: dictionary (generated data).

    **Examples**

    Generating a float CAR variable for China with an autoregressive coefficient of 0.7 
    
    >>> import clusterpy
    >>> china = clusterpy.importArcData("clusterpy/data_examples/china")
    >>> china.generateData("CAR", 'queen', 1, 0.7)

    Generating an integer CAR variable for China with an autoregressive coefficient of 0.7 
    
    >>> import clusterpy
    >>> china = clusterpy.importArcData("clusterpy/data_examples/china")
    >>> china.generateData("CAR", 'queen', 1, 0.7, integer=1)
    """
    wMatrix = wToMatrix(w)
    dim = len(w)
    A = numpy.identity(dim) - rho * wMatrix
    VCV = A.I
    CVCV = numpy.linalg.cholesky(VCV)
    matData = numpy.dot(CVCV, numpy.random.randn(dim, n))
    y = {}
    for i in xrange(dim):
        y[i] = matData[i].tolist()[0]
    return y
