# encoding: latin2
"""
Selection types
"""
__author__ = "Juan C. Duque"
__credits__ = "Copyright (c) 2009-11 Juan C. Duque"
__license__ = "New BSD License"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"

import numpy as np
from random import randint

def minimumSelection(RegionMaker):
    """
    Select and assign the nearest area to a region
    """
    nInd = 0
    minIndex = 0
    idx = 0
    it = 0 #iterator
    rid = 0
    aid = 0
    val = 0.0
    minVal = 0.0
    values = []
    indicesMin = []
    keys = RegionMaker.candidateInfo.keys()

    if keys:
        #values = [ RegionMaker.candidateInfo[i] for i in keys ]
        #minVal = min(values)
        # random selection for ties
        #indicesMin = [ l[0] for l in enumerate(values) if l[1] == minVal ]
        indicesMin = []
        minVal =  float('Inf')
        for it, key in enumerate(keys):
            val = RegionMaker.candidateInfo[key]
            if val < minVal:
                minVal = val
                indicesMin = [it]
                nInd = 1
            elif val == minVal:
                indicesMin.append(it)
                nInd += 1

        idx = randint(0, nInd - 1)
        minIndex = indicesMin[idx]
        aid = keys[minIndex][0]
        rid = keys[minIndex][1]

        for key in keys:
            if key[0] == aid:
                RegionMaker.candidateInfo.pop(key)
        RegionMaker.assignArea(aid, rid)

def fullRandom(RegionMaker):
    """
    Select and assign randomly an area
    """
    keys = RegionMaker.candidateInfo.keys()
    values = [ RegionMaker.candidateInfo[i] for i in keys ]
    if len(values) > 0:
        randomIndex = np.random.randint(0, len(values))
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
