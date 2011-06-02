# encoding: latin2
"""Uniform data module
"""
__author__ = "Juan C. Duque, Alejandro Betancourt"
__credits__ = "Copyright (c) 2010-11 Juan C. Duque"
__license__ = "New BSD License"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"
__all__ = ['generateUniform']

import numpy

def generateUniform(w, n, min, max):
    """
    This function generates n simulated variables for a map according
    to a uniform distribution.
    
    :param w: W similarity matrix
    :type w: dictionary
    :param n: number of variables to be simulated
    :type n: integer
    :param min: minimum of the uniform distribution
    :type min: float
    :param max: maximum of the uniform distribution
    :type max: float
    :rtype: dictionary (generated data)

    **Example**

    Generating a float Uniform process between 1 and 10

    >>> import clusterpy
    >>> china = clusterpy.importArcData("clusterpy/data_examples/china")
    >>> china.generateData("Uniform", 'queen', 1, 1, 10)

    Generating an integer Uniform process between 1 and 10

    >>> import clusterpy
    >>> china = clusterpy.importArcData("clusterpy/data_examples/china")
    >>> china.generateData("Uniform", 'queen', 1, 1, 10, integer=1)
    """
    N = len(w.keys())
    y = {}
    for i in range(N):
        j = list(numpy.random.uniform(min, max, n))
        y[i] = [float(k) for k in j]
    return y

