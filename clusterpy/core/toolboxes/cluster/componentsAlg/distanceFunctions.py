# encoding: latin2
"""
Distance functions 
"""
__author__ = "Juan C. Duque"
__credits__ = "Copyright (c) 2009-11 Juan C. Duque"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"

import numpy

def distanceA2AEuclideanSquared(x, std=[], w=[]):
    """
    This function calcule the Euclidean Squared distance between
    two or more variables.
    """
    if std:
        x = stdobs(x)  #  standardize
    if w:
        w= w / float(add.reduce(w))
        x = x * w  #  weights
    distance=[]
    numrows=numpy.shape(x)[0]
    for row in xrange(numrows - 1):
        #d = numpy.power(numpy.subtract(x[row], x[(row + 1):numrows]), 2)
        d = map(lambda x: x**2, numpy.subtract(x[row], x[(row + 1):numrows]))
        try:
            d = numpy.add.reduce(d, 1)
        except:
            d = d
        distance.append(d)
    return distance


distMethods = {}
distMethods['EuclideanSquared'] = distanceA2AEuclideanSquared

