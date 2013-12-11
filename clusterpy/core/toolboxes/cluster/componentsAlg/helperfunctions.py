# encoding: latin2
"""Algorithm utilities
G{packagetree core}
"""
__author__ = "Juan C. Duque"
__credits__ = "Copyright (c) 2009-11 Juan C. Duque"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"

from numpy import argsort as npargsort, double as npdouble
from numpy import matrix as npmatrix, random as nprandom
from areacl import AreaCl

def indexMultiple(x,value):
    """
    Return indexes in x with multiple values.
    """
    return [ i[0] for i in enumerate(x) if i[1] == value ]

def calculateGetisG(keyList, dataMean, dataStd, dataDictionary, dataLength):
    """
    This function returns the local G statistic a given region.
    """
    sum = 0
    for i in keyList:
        sum = sum + npdouble((dataDictionary[i]))
    neighborNumber = len(keyList)
    numerator = sum - dataMean * neighborNumber
    denominator = dataStd * ((float(dataLength * neighborNumber - (neighborNumber ** 2)) / (dataLength - 1)) ** 0.5)

    #  denominator = (dataStd*((dataLength*neighborNumber-(neighborNumber**2))/(dataLength-1))**0.5)

    G = numerator / denominator
    return G

def quickSortIntersection(dataList, keyList, discardList):
    """
    quickSortIntersection recursively sorts the list of values usinga
    quick sort algorithm.
    """
    if len(keyList) <= 1:
        return keyList
    else:
        lessData = []
        lessKey = []
        moreData = []
        moreKey = []
        pivot = dataList[-1]
        kpivot = keyList[-1]
        for i in range(len(dataList) - 1):
            if keyList[i] not in discardList:
                if dataList[i] <= pivot:
                    lessData.append(dataList[i])
                    lessKey.append(keyList[i])
                else:
                    moreData.append(dataList[i])
                    moreKey.append(keyList[i])
        return quickSortIntersection(lessData, lessKey, discardList) + [kpivot] + quickSortIntersection(moreData, moreKey, discardList)

def quickSort2(keys, y):
    """
    quickSortIntersection recursively sorts the list of values using a
    quick sort algorithm.
    """
    if len(keys) <= 1:
        return keys
    else:
        lessData = []
        lessKey = []
        moreData = []
        moreKey = []
        pivot = y[keys[-1]]
        kpivot = keys[-1]
        keys=keys[0: -1]
        for i in keys:
            if y[i] <= pivot:
                lessKey.append(i)
            else:
                moreKey.append(i)
        return quickSort2(lessKey, y) + [kpivot] + quickSort2(moreKey, y)

def neighborSort(dictionary, discardList):
    """
    Returns the list of keys of a dictionary sorted by the
    values that are assigned by them.
    """
    dataList = dictionary.values()
    keyList = dictionary.keys()
    return quickSortIntersection(dataList, keyList, discardList)

def vectorDistance(v1, v2):
    """
    this function calculates de euclidean distance between two
    vectors.
    """
    sum = 0
    for i in range(len(v1)):
        sum += (v1[i] - v2[i]) ** 2
    return sum ** 0.5

#  INTERNOS

def calculateCentroid(areaList):
    """
    This function return the centroid of an area list
    """
    pg = 0.0
    pk = []
    centroid = AreaCl(0, [], [])
    for area in areaList:
        pg += area.data[0]
        pk = pk + [area.data[0]]
    pkPg = npmatrix(pk).T / pg
    data = [0.0] * len(area.data)
    var = npmatrix(areaList[0].var) * 0.0
    j = 0
    for area in areaList:
        var += area.var * pow(pkPg[j, 0], 2)
        for i in range(len(area.data)):
            data[i] += area.data[i] * pkPg[j, 0]
        j += 1
    centroid.data = data
    centroid.var = var
    return centroid


def factorial(n):
    """
    Returns the factorial of a number.
    """
    fact = 1.0
    if n > 1:
        fact = n * factorial(n - 1)
    return fact

def comb(n, m):
    """
    This function calculates the number of possible combinations of n items
    chosen by m.
    """
    return factorial(n) / (factorial(m) * factorial(n - m))

def recode(X):
    """
    Tranform a list with regions begining in x to a lis begining in 0.
    """
    XP = X + []
    i = 0
    lenX = len(X)
    r = 0

    assigned = {}

    for i in xrange(lenX):
        if X[i] not in assigned:
            assigned[X[i]] = r
            r += 1

    for i in xrange(lenX):
        XP[i] = assigned[XP[i]]

    return XP

def sortedKeys(d):
    """
    Return keys of the dictionary d sorted based on their values.
    """
    values = d.values()
    sortedIndices = npargsort(values)
    sortedKeys = [d.keys()[i] for i in sortedIndices]
    minVal = min(values)
    countMin = values.count(minVal)
    if countMin > 1:
        minIndices = sortedKeys[0: countMin]
        nInd = len(minIndices)
        idx = range(nInd)
        nprandom.shuffle(idx)
        permMins = idx
        c = 0
        for i in range(nInd):
            place = permMins[c]
            sortedKeys[c] = minIndices[place]
            c += 1
    return sortedKeys

def feasibleRegion(feasDict):
    """
    Return if a list of areas are connected
    """
    areas2Eval = []
    areas = {}
    for key in feasDict.keys():
        try:
            neighbours = feasDict[key]
        except:
            neighbours = {}
        a = AreaCl(key, neighbours, [])
        areas[key] = a
        areas2Eval = areas2Eval + [key]
    feasible = 1
    newRegion = set([])
    for area in areas2Eval:
        newRegion = newRegion | (set(areas[area].neighs) & set(areas2Eval))
    if set(areas2Eval) - newRegion != set([]):
        feasible = 0
    return feasible

