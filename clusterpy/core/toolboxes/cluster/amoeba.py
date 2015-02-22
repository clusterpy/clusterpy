# encoding: latin2
"""AMOEBA
"""
__author__ = "Juan C. Duque, Alejandro Betancourt, Jose L. Franco"
__credits__ = "Copyright (c) 2009-11 Juan C. Duque"
__license__ = "New BSD License"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"

import time as tm
import numpy
from componentsAlg import calculateGetisG,quickSort2,neighborSort 

__all__ = ['execAMOEBA']

def execAMOEBA(y, w, significance=0.01):
    """AMOEBA A Multidirectional Optimum Ecotope-Based Algorithm

    AMOEBA, devised by [Alstadt_Getis2006]_, embeds a local spatial
    autocorrelation statistic in an iterative procedure in order to
    identify spatial clusters (ecotopes) of related spatial units.


    This algorithm starts with an initial area to which neighboring areas are
    iteratively attached until the addition of any neighboring area fails to
    increase the magnitude of the local Getis statistic of [Getis_Ord1992]_
    and [Ord_Getis1995]_. The resulting region is considered an ecotope. This
    procedure is executed for all areas, and final ecotopes are defined after
    resolving overlaps and asserting non-randomness. 


    The algorithm implemented here is a new version of AMOEBA proposed by
    [Duque_Alstadt_Velasquez_Franco_Betancourt2010]_ that significantly
    reduces its computational complexity without losing optimality. ::

        layer.cluster('amoeba',vars,<wType>,<significance>)

    :keyword vars: Area attribute(s) 
    :type vars: sist
    :keyword wType: Type of first-order contiguity-based spatial matrix: 'rook' or 'queen'. Default value wType = 'rook'. 
    :type wType: string
    :keyword significance: Level of statistical significance. Default value
    :type significance: float (significance=0.01)

    IMPORTANT NOTE: 
    
    Since AMEOBA is a non-exhausive algorithm, clusterPy does not provide the
    dissolve option. to obtain the solution vector you will need to export the
    layer with the command "Layer.exportArcData". The exported shape file will
    have an additional variable with the solution vector, where areas with
    positive values belongs to high value clusters; areas with negative values
    belongs to low value clusters; and areas with value zero are those outside
    the clusters.
    """
    start = tm.time()
    print "Running computationally efficient AMOEBA (Duque et al., 2010)"
    print "Number of areas: ", len(y)
    NumberOfClusters = 0
    areaKeys = y.keys() 
    dataMean = numpy.mean(numpy.double(y.values()))
    dataStd = numpy.std(numpy.double(y.values()))
    dataLength = len(y)
    generatedClusters = dict()
    clusterGValues = dict()
    clusterGValuesAbs = dict()
    print "Starting iterative process"
    for s in areaKeys:
        discNeighbor = []
        if s in w:
            neighbors = w[s]
        itAreaList = [s]
        currentG = calculateGetisG([s], dataMean, dataStd, y, dataLength)
        previousG = currentG - 1
        sortedNeighbors = []
        while currentG != previousG:
            sortedNeighbors = quickSort2(neighbors, y)
            neighbors = []
            previousG = currentG
            AuxItAreaList = []
            AuxDiscNeighbor = []
            AreasBase = itAreaList
            NoSorted = len(sortedNeighbors)
            if currentG <= 0:
                for a in range(NoSorted):
                    newG = calculateGetisG(itAreaList + sortedNeighbors[0: a + 1],dataMean, dataStd, y, dataLength)
                    if newG < currentG:
                        currentG = newG
                        AuxItAreaList = sortedNeighbors[0: a + 1]
                        AuxDiscNeighbor = sortedNeighbors[a + 1: NoSorted]
            else:
                for a in range(NoSorted):
                    newG = calculateGetisG( itAreaList + sortedNeighbors[-a -1: NoSorted], dataMean, dataStd, y, dataLength)
                    if newG > currentG:
                        currentG = newG
                        AuxItAreaList = sortedNeighbors[-a -1: NoSorted]
                        AuxDiscNeighbor = sortedNeighbors[0: -a -1]
            discNeighbor = discNeighbor + AuxDiscNeighbor
            itAreaList = itAreaList + AuxItAreaList
            for x in AuxItAreaList:
                neighbors = neighbors + list(set(w[x]) - set(sortedNeighbors) - set(itAreaList) - set(discNeighbor) - set(neighbors))
        generatedClusters[s] = itAreaList
        clusterGValues[s] = currentG
        clusterGValuesAbs[s] = numpy.abs(currentG)
    prioritaryClusters = reversed(neighborSort(clusterGValuesAbs, []))
    tnclusterCounter = 1
    output = {}
    clusterMap = {}
    mapCounter = 0
    areaRange = range(dataLength)    
    randomKeyList = []
    clusterCounter = 0
    print "Testing clusters significance"
    for i in range(1000):
        randomKeyListInstance = []
        randomList = numpy.random.permutation(areaRange)
        for j in randomList:
            randomKeyListInstance.append(areaKeys[j])
        randomKeyList.append(randomKeyListInstance)
    for i in areaKeys:
        output[i] = 0
        clusterMap[i] = mapCounter
        mapCounter = mapCounter + 1
    negClusterCounter = -1
    posClusterCounter = 1
    for x in prioritaryClusters: #  Permutation and overlapping tests
        validCluster = 1
        for h in generatedClusters[x]: #  Validates if the cluster overlaps with a previously accepted one
            if output[h] != 0:
                validCluster = 0
                break
        if validCluster == 1:
            betterClusters = 0
            for j in range(1000): #  Monte Carlo permutation test
                permKey = []
                for e in generatedClusters[x]:
                    permKey.append((randomKeyList[j])[clusterMap[e]])
                randomG = calculateGetisG(permKey, dataMean, dataStd, y, dataLength)
                if clusterGValues[x] >= 0:
                    if clusterGValues[x] < randomG:
                        betterClusters = betterClusters + 1
                else:
                    if clusterGValues[x] > randomG:
                        betterClusters = betterClusters + 1
            pValue = (betterClusters) / 1000.00
            if  pValue <= significance:
                NumberOfClusters = NumberOfClusters + 1
                clustId = 0
                if numpy.double(clusterGValues[x]) > 0:
                    clustId = posClusterCounter
                    posClusterCounter = posClusterCounter + 1
                else:
                    clustId = negClusterCounter
                    negClusterCounter = negClusterCounter - 1
                for h in generatedClusters[x]:
                    if clusterGValues[x] < 0:
                        output[h] = clustId
                    else:
                        output[h] = clustId
                clusterCounter=clusterCounter + 1
    Sol = output.values()
    Of = 0
    time = tm.time() - start
    output = { "objectiveFunction": Of,
    "runningTime": time,
    "algorithm": "amoeba",
    "regions": len(Sol),
    "r2a": Sol,
    "distanceType": None,
    "distanceStat": None,
    "selectionType": None,
    "ObjectiveFuncionType": None} 
    print "FINAL SOLUTION: " + str(Sol)
    print ">= 1  : cluster of high values"
    print "== 0  : outside of cluster"
    print "<= -1 : cluster of low values"
    print "Done"
    return output
