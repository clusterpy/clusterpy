# encoding: latin2
"""
Objective functions
"""
__author__ = "Juan C. Duque"
__credits__ = "Copyright (c) 2009-11 Juan C. Duque"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"

import numpy
import distanceFunctions


def getObjectiveFunctionSumSquares(RegionMaker, region2AreaDict, indexData=[]):
    """
    Sum of squares from each area to the region's centroid
    """
    dist = 0.0
    objDict = {}
    for region in region2AreaDict.keys():
        objDict[region] = 0.0
        areasIdsIn = region2AreaDict[region]
        areasInNow = [RegionMaker.areas[aID] for aID in areasIdsIn]
        dataAvg = RegionMaker.am.getDataAverage(areasIdsIn, indexData)
        c = 1
        for area in areasInNow:
            areaData = []
            for index in indexData:
                areaData += [area.data[index]]
            data = numpy.concatenate(([areaData], [dataAvg]))
            areaDistance = distanceFunctions.distMethods[RegionMaker.distanceType](data)
            dist = areaDistance[0][0]
            objDict[region] += dist
    obj = sum(objDict.values())
    return obj

def getObjectiveFunctionSumSquaresFast(RegionMaker, region2AreaDict, modifiedRegions, indexData=[]):
    """
    Sum of squares from each area to the region's centroid
    """
    obj = 0.0
    for region in region2AreaDict.keys():
        if region in modifiedRegions:
            valRegion = 0.0
            areasIdsIn = region2AreaDict[region]
            areasInNow = [RegionMaker.areas[aID] for aID in areasIdsIn]
            dataAvg = RegionMaker.am.getDataAverage(areasIdsIn, indexData)
            for area in areasInNow:
                areaData = []
                for index in indexData:
                    areaData += [area.data[index]]
                data = numpy.concatenate(([areaData], [dataAvg]))
                areaDistance = distanceFunctions.distMethods[RegionMaker.distanceType](data)
                dist = areaDistance[0][0]
                valRegion += dist
            obj += valRegion
        else:
            obj += RegionMaker.objDict[region]
    return obj


objectiveFunctionTypeDispatcher = {}
objectiveFunctionTypeDispatcher["SS"] = getObjectiveFunctionSumSquares
objectiveFunctionTypeDispatcher["SSf"] = getObjectiveFunctionSumSquaresFast

def makeObjDict(RegionMaker, indexData=[]):
    """
    constructs a dictionary with the objective function per region
    """
    objDict = {}
    if len(RegionMaker.indexDataOF) == 0:
        indexData = range(len(RegionMaker.areas[0].data))
    else:
        indexData = RegionMaker.indexDataOF
    for region in RegionMaker.region2Area.keys():
        objDict[region] = 0.0
        areasIdsIn = RegionMaker.region2Area[region]
        areasInNow = [RegionMaker.areas[aID] for aID in areasIdsIn]
        dataAvg = RegionMaker.am.getDataAverage(areasIdsIn, indexData)
        c = 1
        for area in areasInNow:
            areaData = []
            for index in indexData:
                areaData += [area.data[index]]
            data = numpy.concatenate(([areaData], [dataAvg]))
            areaDistance = distanceFunctions.distMethods[RegionMaker.distanceType](data)
            dist = areaDistance[0][0]
            objDict[region] += dist
    return objDict


