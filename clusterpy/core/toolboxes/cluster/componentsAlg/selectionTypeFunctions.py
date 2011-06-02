# encoding: latin2
"""
Selection types
"""
__author__ = "Juan C. Duque"
__credits__ = "Copyright (c) 2009-11 Juan C. Duque"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"

import numpy

def minimumSelection(RegionMaker):
    """
    Select and assign the nearest area to a region
    """
    keys = RegionMaker.candidateInfo.keys()
    if len(keys) != 0:
        values = [ RegionMaker.candidateInfo[i] for i in keys ]
        minVal = min(values)
        # random selection for ties
        indicesMin = indexMultiple(values, minVal)
        nInd = len(indicesMin)
        idx=range(nInd)
        numpy.random.shuffle(idx)
        minIndex = indicesMin[idx[0]]
        aid,rid = keys[minIndex]
        [RegionMaker.candidateInfo.pop(key) for key in keys if key[0] == aid]
        RegionMaker.assignArea(aid, rid)

def fullRandom(RegionMaker):
    """
    Select and assign randomly an area
    """
    keys = RegionMaker.candidateInfo.keys() 
    values = [ RegionMaker.candidateInfo[i] for i in keys ]
    if len(values) > 0:
        randomIndex = numpy.random.randint(0, len(values))
        aid,rid = keys[randomIndex]
        [RegionMaker.candidateInfo.pop(key) for key in keys if key[0] == aid]
        RegionMaker.assignArea(aid, rid)

 
def indexMultiple(x,value):
    """
    Return indexes in x with multiple values.
    """
    return [ i[0] for i in enumerate(x) if i[1] == value ]



selectionTypeDispatcher = {}
selectionTypeDispatcher["Minimum"] = minimumSelection
selectionTypeDispatcher["FullRandom"] = fullRandom
