# encoding: latin2
"""Geographical Association Coefficient
G{packagetree core}
"""
__author__ = "Juan C. Duque, Alejandro Betancourt"
__credits__ = "Copyright (c) 2009-10 Juan C. Duque"
__license__ = "New BSD License"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"

import numpy
import time as tm
from componentsESDA import absDifference

__all__ = ['geoAssociationCoef']

def geoAssociationCoef(*args):
    """Geographical Association Coefficient
    This function creates a dictionary with the geographical
    association coefficient of the variable list.
    
    the geographical association coefficient cualify with a 
    number between 0 and 1 the simlitarity two variables distributions.
    
    I{Parameters shown below are modified to explain how to calculate the 
    geographical Association coeficient for two variables of
    a layer object.
    As example:}
    
    @type algorithm: string
    @keyword algorithm: "GAC" 

    @type variables: names tuple
    @keyword variables: Two variables names to be used  

    @rtype: tuple
    @return: (coefficients dictionary,coeficients list of lists)

    Examples:

    >>> import clusterpy
    >>> new = clusterpy.createGrid(10,10)
    >>> new.generateData("SAR",'rook',1,0.9)
    >>> new.generateData("SAR",'rook',1,0.9)
    >>> gac = new.esda("GAC","SAR1","SAR2")
    """
    i = 0
    varList = args[1:]
    layer = args[0]
    gac = {}
    gacw = [list(numpy.zeros(len(varList))) for k in range(len(varList))]
    while i < len(varList):
        j = i + 1
        v1 = varList[i]
        gac[(v1,v1)] = 0
        gacw[i][i] = 0
        while j < len(varList):
            v2 = varList[j]
            var1 = [x[0] for x in layer.getVars(v1).values()]
            var2 = [x[0] for x in layer.getVars(v2).values()]
            gac[(v1, v2)] = absDifference(var1, var2)
            gac[(v2, v1)] = gac[(v1, v2)]
            gacw[i][j] = gac[(v1, v2)]
            gacw[j][i] = gac[(v1, v2)]
            j = j + 1
        i = i + 1
    print "GAC has been succesfuly calculed"
    return gac, gacw

