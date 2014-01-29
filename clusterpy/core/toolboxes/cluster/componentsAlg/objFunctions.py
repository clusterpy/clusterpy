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

from distanceFunctions import distMethods
import numpy as np

def getObjectiveFunctionSumSquares(regionMaker,
                                   region2AreaDict,
                                   indexData=[]):
    """
    Sum of squares from each area to the region's centroid
    """
    objDict = {}
    for region in region2AreaDict.keys():
        objDict[region] = 0.0
        areasIdsIn = region2AreaDict[region]
        areasInNow = [regionMaker.areas[aID] for aID in areasIdsIn]
        dataAvg = regionMaker.am.getDataAverage(areasIdsIn, indexData)
        c = 1
        for area in areasInNow:
            areaData = []
            for index in indexData:
                areaData += [area.data[index]]
            data = [areaData] + [dataAvg]
            areaDistance = distMethods[regionMaker.distanceType](data)
            objDict[region] += areaDistance[0][0]
    return sum(objDict.values())

cachedObj = {}
def getObjectiveFunctionSumSquaresFast(regionMaker,
                                       region2AreaDict,
                                       modifiedRegions,
                                       indexData=[]):
    """
    Sum of squares from each area to the region's centroid
    """
    obj = 0.0
    r2aDictKeys = region2AreaDict.keys()
    for region in r2aDictKeys:
        if region in modifiedRegions:
            valRegion = 0.0
            areasIdsIn = region2AreaDict[region]
            key = areasIdsIn
            key.sort()
            key = tuple(key)
            if cachedObj.has_key(key):
                valRegion = cachedObj[key]
            else:
                areasInNow = [regionMaker.areas[_aid] for _aid in areasIdsIn]
                dataAvg = regionMaker.am.getDataAverage(areasIdsIn, indexData)

                for area in areasInNow:
                    areaData = []
                    areaDataList = area.data
                    for index in indexData:
                        areaData.append(areaDataList[index])
                    areaData = [areaData] + [dataAvg]
                    # Taking the first element from the dataDistance
                    dist = distMethods[regionMaker.distanceType](areaData)[0][0]
                    valRegion += dist

                cachedObj[key] = valRegion
            obj += valRegion
        else:
            obj += regionMaker.objDict[region]
    return obj

def getObjectiveFunctionClique(regionMaker, *args):
    """
    Objective function computed with the distance between all the areas
    in a region (Clique).
    """
    ofuncval = 0.0
    for region in regionMaker.region2Area.values():
        size = len(region)
        distmatrix = np.zeros((size, size))

        for iti in xrange(size):
            areaid = region[iti]
            areai = np.array(regionMaker.areas[areaid].data)
            for itj in xrange(size):
                if iti < itj:
                    areaid = region[itj]
                    areaj = np.array(regionMaker.areas[areaid].data)
                    distmatrix[iti][itj] = np.linalg.norm(areai - areaj) ** 2

        ofuncval += distmatrix.sum()
    return ofuncval

objectiveFunctionTypeDispatcher = {}
objectiveFunctionTypeDispatcher["SS"] = getObjectiveFunctionSumSquares
objectiveFunctionTypeDispatcher["SSf"] = getObjectiveFunctionSumSquaresFast
objectiveFunctionTypeDispatcher["complete"] = getObjectiveFunctionClique

def makeObjDict(regionMaker, indexData=[]):
    """
    constructs a dictionary with the objective function per region
    """
    objDict = {}
    if len(regionMaker.indexDataOF) == 0:
        indexData = range(len(regionMaker.areas[0].data))
    else:
        indexData = regionMaker.indexDataOF
    for region in regionMaker.region2Area.keys():
        objDict[region] = 0.0
        areasIdsIn = regionMaker.region2Area[region]
        areasInNow = [regionMaker.areas[aID] for aID in areasIdsIn]
        dataAvg = regionMaker.am.getDataAverage(areasIdsIn, indexData)
        c = 1
        for area in areasInNow:
            areaData = []
            for index in indexData:
                areaData += [area.data[index]]
            data = [areaData] + [dataAvg]
            areaDistance = distMethods[regionMaker.distanceType](data)
            dist = areaDistance[0][0]
            objDict[region] += dist
    return objDict
