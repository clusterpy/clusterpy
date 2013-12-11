# encoding: latin2
""" Transforming contiguity matrix
"""
__author__ = "Juan C. Duque, Alejandro Betancourt"
__credits__ = "Copyright (c) 2010-11 Juan C. Duque"
__license__ = "New BSD License"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"
__all__ = ['dict2matrix']

import struct
import numpy
from os import path
from scipy.sparse import lil_matrix
# WfromPolig

def dict2matrix(wDict,std=0,diag=0):
    """Transform the contiguity dictionary to a matrix

    :param wDict: Contiguity dictionary 
    :type wDict: dictionary
    :param std: 1 to get the standarized matrix 
    :type std: dictionary
    
    **Example 1** ::
    
    >>> import clusterpy
    >>> lay = clusterpy.importArcData("clusterpy/data_examples/china")
    >>> wmatrix = clusterpy.contiguity.dict2matrix(lay.Wrook)

    :rtype: list, List of lists representing the contiguity matrix
    """
    data = []
    nAreas = len(wDict.keys())
    for i in wDict:
        data.append([0]*nAreas)
        data[i][i] = diag
        ne = len(wDict[i])+ diag
        for j in wDict[i]:
            if std:
                data[i][j] = 1 / float(ne)
            else:
                data[i][j] = 1
    return data

def dict2sparseMatrix(wDict,std=0,diag=0):
    """Transform the contiguity dictionary to a matrix

    :param wDict: Contiguity dictionary 
    :type wDict: dictionary
    :param std: 1 to get the standarized matrix 
    :type std: dictionary
    
    **Example 1** ::
    
    >>> import clusterpy
    >>> lay = clusterpy.importArcData("clusterpy/data_examples/china")
    >>> wmatrix = clusterpy.contiguity.dict2matrix(lay.Wrook)

    :rtype: list, List of lists representing the contiguity matrix
    """
    data = lil_matrix((len(wDict.keys()),len(wDict.keys())))
    nAreas = len(wDict.keys())
    for i in wDict:
        data[i,i] = diag
        ne = len(wDict[i])+ diag
        for j in wDict[i]:
            if std:
                data[i,j] = 1 / float(ne)
            else:
                data[i,j] = 1
    return data
