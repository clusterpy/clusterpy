# encoding: latin2
"""Redistribution Coefficient
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

__all__ = ['redistributionCoef']

def redistributionCoef(*args):
    """Redistribution Coefficient
    This function creates a dictionary with the redistribution
    coefficient of the variable list.
    
    the redistribution coefficient cualify with a number between
    0 and 1 the simlitarity between two time periods of a variable.

    I{Parameters shown below are modified to explain how to calculate the 
    redistribution coeficient for a list of variables two variables
    of a layer object.
    As example:}
    
    @type algorithm: string
    @keyword algorithm: "RDC" 

    @type variables: names tuple
    @keyword variables: Two variables names to use. 

    @rtype: tuple
    @return: (coefficients dictionary,coeficients list of lists)

    Examples:

    >>> import clusterpy
    >>> new = clusterpy.createGrid(10,10)
    >>> new.generateData("SAR",'rook',1,0.9)
    >>> new.generateData("SAR",'rook',1,0.9)
    >>> rdc = new.esda("RDC","SAR1","SAR2")
    """
    i = 0
    varList = args[1:]
    layer = args[0]
    rdc = {}
    rdcw = [list(numpy.zeros(len(varList))) for k in range(len(varList))]
    while i < len(varList):
        j = i + 1
        v1 = varList[i]
        rdc[(v1, v1)] = 0
        rdcw[i][i] = 0
        while j < len(varList):
            v2 = varList[j]
            var1 = [x[0] for x in layer.getVars(v1).values()]
            var2 = [x[0] for x in layer.getVars(v2).values()]
            rdc[(v1, v2)] = absDifference(var1,var2)
            rdc[(v2, v1)] = rdc[(v1, v2)]
            rdcw[i][j] = rdc[(v1, v2)]
            rdcw[j][i] = rdc[(v1, v2)]
            j = j + 1
        i = i + 1
    print "rdc has been succesfuly calculed"
    return rdc, rdcw

