# encoding: latin2
"""Global Binomial data module
"""
__author__ = "Juan C. Duque, Alejandro Betancourt"
__credits__ = "Copyright (c) 2010-11 Juan C. Duque"
__license__ = "New BSD License"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"
__all__ = ['generateGBinomial']

import numpy

def generateGBinomial(w, n, num, prob):
    """
    This function generates n simulated variables using a binomial
    distribution with the same parameters for all features.

    :param w: contiguity matrix
    :type w: dictionary
    :param n: number of variables to be simulated
    :type n: integer
    :param num: population of all the areas
    :type num: integer
    :param prob: probability of all the areas
    :type prob: float
    :rtype: dictionary (generated data)

    **Example** 

    Generating a Binomial process on China with the same parameters for all
    features

    >>> import clusterpy
    >>> china = clusterpy.importArcData("clusterpy/data_examples/china")
    >>> china.generateData("GBinomial", 'queen', 1, 10000, 0.5)
    """
    N = len(w.keys())
    y = {}
    for i in range(N):
        j = list(numpy.random.binomial(num, prob, n))
        y[i] = [float(k) for k in j]
    return y
