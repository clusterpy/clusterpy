# encoding: latin2
"""ESDA components
G{packagetree core}
"""
__author__ = "Juan C. Duque, Alejandro Betancourt"
__credits__ = "Copyright (c) 2009-10 Juan C. Duque"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"

import time as tm

__all__ = ['absDifference']

def absDifference(variable1, variable2):
    """abs difference coeficient
    This coefficient cualify with a number between 0 and 1 the
    similarity between two variables.
    
    @type variable1: string  
    @param variable1: First variabldae

    @type variable2: string
    @param variable2: Second variable
    
    @rtype: float
    @return: Redistribution coefficient
    """
    global1 = sum(variable1)
    global2 = sum(variable2)
    absDiff = sum([abs(variable1[i] / float((global1 + 1)) - variable2[i] / float((global2 + 1))) for i in range(len(variable1))]) / float(2)
    return absDiff
