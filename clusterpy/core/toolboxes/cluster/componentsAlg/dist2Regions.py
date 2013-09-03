# encoding: latin2
"""
Distance functions from an area to a region
"""
__author__ = "Juan C. Duque"
__credits__ = "Copyright (c) 2009-11 Juan C. Duque"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"

import numpy
import distanceFunctions


def getDistance2RegionCentroid(areaManager, area, areaList, indexData=[]):
    """
    The distance from area "i" to the attribute centroid of region "k"
    """
    sumAttributes = numpy.zeros(len(area.data))
    if len(areaManager.areas[areaList[0]].data) - len(area.data) == 1:
        for aID in areaList:
            sumAttributes += numpy.array(areaManager.areas[aID].data[0: -1])
    else:
        for aID in areaList:
            sumAttributes += numpy.array(areaManager.areas[aID].data)
    centroidRegion = sumAttributes/len(areaList)
    regionDistance = sum((numpy.array(area.data) - centroidRegion) ** 2)
    return regionDistance

distanceStatDispatcher = {}
distanceStatDispatcher["Centroid"] = getDistance2RegionCentroid


