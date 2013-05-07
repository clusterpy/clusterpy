# encoding: latin2
"""similarity Coefficient
G{packagetree core}
"""
__author__ = "Juan C. Duque, Alejandro Betancourt"
__credits__ = "Copyright (c) 2009-10 Juan C. Duque"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"

import numpy
import time as tm
from componentsESDA import absDifference

__all__ = ['similarityCoef']

def similarityCoef(*args):
    """Similarity Coefficient
    This function creates a dictionary with the similarity coefficient
    of layer.
    
    the similarity coefficient cualify with a number between 0 and 1 
    the simulitude between layers areas.
    
    I{Parameters shown below are modified to explain how to calculate the 
    similarity coeficient for a layer object.
    As example:}
    
    @type algorithm: string
    @keyword algorithm: "SIMC" 

    @type variables: names tuple
    @keyword variables: Variables names used to calculate de differences 

    @rtype: tuple
    @return: (coefficients dictionary,coeficients list of lists)

    Examples:

    >>> import clusterpy
    >>> new = clusterPy.createGrid(10,10)
    >>> new.generateData("SAR",'rook',1,0.9)
    >>> new.generateData("SAR",'rook',1,0.9)
    >>> SIMC = new.esda("SIMC","SAR1","SAR2")
    """
    i = 0
    varList = args[1:]
    layer = args[0]
    data = layer.getVars(*varList)
    nAreas = len(data)
    simc = {}
    simcw = [list(numpy.zeros(nAreas)) for k in range(nAreas)]
    while i < nAreas:
        j = i + 1
        simc[(i, i)] = 0
        simcw[i][i] = 0
        while j < nAreas:
            var1 = data[i] 
            var2 = data[j]
            simc[(i, j)] = absDifference(var1, var2)
            simc[(j, i)] = simc[(i, j)]
            simcw[i][j] = simc[(i, j)]
            simcw[j][i] = simc[(i, j)]
            j = j + 1
        i = i + 1
    print "SIMC has been succesfuly calculed"
    return simc, simcw

