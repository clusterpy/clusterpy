# encoding: latin2
"""Inequality index for multiple variables
"""
__author__ = "Juan C. Duque, Alejandro Betancourt"
__credits__ = "Copyright (c) 2009-11 Juan C. Duque"
__license__ = "New BSD License"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"

__all__ = ['inequalityMultivar']

from theilIndex import theil 

import numpy

def inequalityMultivar(Y, area2region, index = 'theil'):
    """Inequality index for multiple variables

    This function calculates a given inequality index for multiple variables::

        Layer.inequality('inequalityMultivar',vars, cluster, <index>)

    :keyword vars: List with variables to be analyzed; e.g: ['Y1978', 'Y1979', 'Y1980', 'Y1981'] 
    :type vars: list
    :keyword cluster: variable in Layer containing regionalization solution; e.g.: 'BELS'
    :type cluster: string
    :keyword index: inequality index to be applied. Default value index = 'theil'. 
    :type index: string

    :rtype: Tuple
    :return: index, index between groups, index within groups, index whitin groups over index 


    **Example 1** ::

        import clusterpy
        instance = clusterpy.importArcData("clusterpy/data_examples/china")
        result = instance.inequality('inequality',['Y1978', 'Y1979', 'Y1980', 'Y1981'], 'BELS', index = 'theil')

    """
    matrix = numpy.matrix(Y.values()).transpose()
    periods = [x.tolist()[0] for x in matrix]
    areas = Y.keys()
    t = []
    tb = []
    tw = []
    tw_t = []
    for var in periods:
        var = [[x] for x in var]
        dictionary = dict(zip(areas,var))
        if index == 'theil':
            t2,tb2,tw2 = theil(dictionary,area2region)
            tw_t2 = tw2/float(t2)
        else:
            raise NameError("index is not available in clusterpy")
        t.append(t2)
        tb.append(tb2)
        tw.append(tw2)
        tw_t.append(tw_t2)
    return t,tb,tw,tw_t    
        

