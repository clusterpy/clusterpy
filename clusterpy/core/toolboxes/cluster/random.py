# encoding: latin2
"""Random regions
"""
__author__ = "Juan C. Duque"
__credits__ = "Copyright (c) 2009-11 Juan C. Duque"
__license__ = "New BSD License"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"

import time as tm
from componentsAlg import AreaManager
from componentsAlg import RegionMaker

__all__ = ['execRandom']

def execRandom(y, w, regions):
    """Generate random regions
    
    This algorithm aggregates, at random, a set of areas into a predefined
    number of spatially contiguous regions. ::

        layer.cluster('random',vars,regions,<wType>,<dissolve>,<dataOperations>)

    :keyword vars: Area attribute(s) (e.g. ['SAR1','SAR2']) 
    :type vars: list
    :keyword regions: Number of regions 
    :type regions: integer
    :keyword wType: Type of first-order contiguity-based spatial matrix: 'rook' or 'queen'. Default value wType = 'rook'. 
    :type wType: string
    :keyword dissolve: If = 1, then you will get a "child" instance of the layer that contains the new regions. Default value = 0. Note:. Each child layer is saved in the attribute layer.results. The first algorithm that you run with dissolve=1 will have a child layer in layer.results[0]; the second algorithm that you run with dissolve=1 will be in layer.results[1], and so on. You can export a child as a shapefile with layer.result[<1,2,3..>].exportArcData('filename')
    :type dissolve: binary
    :keyword dataOperations: Dictionary which maps a variable to a list of operations to run on it. The dissolved layer will contains in it's data all the variables specified in this dictionary. Be sure to check the input layer's fieldNames before use this utility.
    :type dataOperations: dictionary

    The dictionary structure must be as showed bellow.

    >>> X = {}
    >>> X[variableName1] = [function1, function2,....]
    >>> X[variableName2] = [function1, function2,....]

    Where functions are strings which represents the name of the 
    functions to be used on the given variableName. Functions 
    could be,'sum','mean','min','max','meanDesv','stdDesv','med',
    'mode','range','first','last','numberOfAreas. By default just
    ID variable is added to the dissolved map.
      
    """
    if regions >= len(y):
        message = "\n WARNING: You are aggregating "+str(len(y))+" into"+\
        str(regions)+" regions!!. The number of regions must be an integer"+\
        " number lower than the number of areas being aggregated"
        raise Exception, message 

    distanceType = "EuclideanSquared" 
    distanceStat = "Centroid"
    objectiveFunctionType = "SS"
    selectionType = "FullRandom"
    am = AreaManager(w, y, distanceType)
    start = tm.time()

    #  CONSTRUCTION

    rm = RegionMaker(am, regions, 
                    distanceType = distanceType,
                    distanceStat = distanceStat,
                    selectionType = selectionType,
                    objectiveFunctionType = objectiveFunctionType)
    time = tm.time() - start
    Sol = rm.returnRegions()
    Of = rm.objInfo
    print "FINAL SOLUTION: ", Sol
    print "FINAL OF: ", Of
    output = { "objectiveFunction": Of,
    "runningTime": time,
    "algorithm": "random",
    "regions": len(Sol),
    "r2a": Sol,
    "distanceType": distanceType,
    "distanceStat": distanceStat,
    "selectionType": selectionType,
    "ObjectiveFuncionType": objectiveFunctionType} 
    print "Done"
    return output

