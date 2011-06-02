# encoding: latin2
"""Local Binomial data module
"""
__author__ = "Juan C. Duque, Alejandro Betancourt"
__credits__ = "Copyright (c) 2010-11 Juan C. Duque"
__license__ = "New BSD License"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"
__all__ = ['generateLBinomial']

import numpy
 
def generateLBinomial(n, y_pob, y_pro):
    """
    This function generates n simulated variables using a binomial
    distribution using individual parameters.

    :param n: number of variables to be simulated
    :type n: integer
    :param y_pob: list of populations, one for each area
    :type y_pob: list
    :param y_pro: list of probabilities, one for each area
    :type y_pro: float
    :rtype: dictionariy (generated data)

    **Examples** 

    Generating a local binomial process on China with Y1998 as the population
    level and simulated uniform probability (Uniform31) as risk level.

    >>> import clusterpy
    >>> china = clusterpy.importArcData("clusterpy/data_examples/china")
    >>> china.generateData("Uniform", 'queen', 1, 0, 1)
    >>> china.fieldNames
    >>> china.generateData("LBinomial", 'rook', 1, 'Y1998', 'Uniform31')
    """
    y = {}
    for i in y_pob:
        j = list(numpy.random.binomial(y_pob[i][0], y_pro[i][0],n))
        y[i] = j
    return y
