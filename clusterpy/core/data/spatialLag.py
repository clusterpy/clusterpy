# encoding: latin1
"""spatial lag of a variable
"""
__author__ = "Juan C. Duque, Alejandro Betancourt"
__credits__ = "Copyright (c) 2010-11 Juan C. Duque"
__license__ = "New BSD License"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"
__all__ = ['spatialLag']

import numpy

def spatialLag(data,w):
    """
    This method recives a dictionary of variables an
    return a copy of the dictionary with variables
    spatially lagged.

    :param data: data dictionary to be lagged
    :type data: dictionary
    :rtype: dictionary (Y dictionary with the lag of vars)
    """  
    data = [data[x] for x in data]
    data = numpy.matrix(data)
    data = data.transpose()
    w = numpy.matrix(w)
    data = data*w
    data = data.transpose()
    y = {}
    for nd, d in enumerate(data):
        y[nd] = d.tolist()[0]
    return y

