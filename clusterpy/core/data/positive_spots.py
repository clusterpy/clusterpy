# encoding: latin2
"""Positive spots data module 
"""
__author__ = "Juan C. Duque, Alejandro Betancourt, Jose L. Franco"
__credits__ = "Copyright (c) 2010-11 Juan C. Duque"
__license__ = "New BSD License"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"
__all__ = ['generateSpots']

import copy
import numpy

def generatePositiveSpots(w, nc=4, compact=0.9, Zalpha=2.32):
    """
    This function generates a set of data with simulated clusters of atypical possitive features. See more details on this process in: Duque JC, Aldstadt J, Velasquez E, Franco JL, Betancourt A (2010). A computationally efficient method for delineating irregularly shaped spatial clusters. I{Journal of Geographical Systems}, forthcoming. DOI: 10.1007/s10109-010-0137-1.
    
    :param w: contiguity matrix
    :type w: dictionary
    :param nc: number of clusters
    :type nc: integer
    :param compact: level of compactness
    :type compact: float
    :param Zalpha: Z value of the significance level
    :type Zalpha: float
    :rtype: dictionary (generated data)

    **Example** 

    Generating a float Spot process on China each with 4 clusters,
    and compactness level of 0.7 and an Zalpha value of 1.64

    >>> import clusterpy
    >>> china = clusterpy.importArcData("clusterpy/data_examples/china")
    >>> china.generateData("positive_spots", 'queen', 1, 4, 0.7, 1.64)

    Generating an integer Spot process on China each with 4 clusters,
    and compactness level of 0.7 and an alpha value of 1.64

    >>> import clusterpy
    >>> china = clusterpy.importArcData("clusterpy/data_examples/china")
    >>> china.generateData("positive_spots", 'queen', 1, 4, 0.7, 1.64, integer=1)
    """
    y = {}
    N = len(w.keys())
    posAreaNumber = 0
    avAreaNumber = 0
    negAreaNumber = 0
    PosAreas = []
    NegAreas = []
    avAreas = []
    for i  in xrange(10000): # this cycle creates and classifies the N random numbers
        num = abs(numpy.random.randn())
        if num > Zalpha:
            PosAreas.append(num)
            avAreas.append(num)
            posAreaNumber = posAreaNumber + 1
            avAreaNumber = avAreaNumber + 1
        else:
            avAreas.append(num)
            avAreaNumber = avAreaNumber + 1
    AN = numpy.zeros(nc)
    NoClusters = numpy.floor(1 * N)
    sum = 0
    spines = []
    for i in range(nc): # this cycle calculates the length of each cluster
        lenClus = (0.20 / nc) * N
        AN[i] = lenClus
        sum = sum + lenClus
        spines.append(lenClus * (1 - compact))
    NoClusters = N - sum
    allAddedAreas = set([])
    allAreas = set(w.keys())
    listOfClusterAreas = []
    savedAllAddedAreas = set([])
    LA =  numpy.array([])
    savedLA = numpy.array([])
    i = 0
    while i < nc: # This cycle creates the clusters without values
        savedAllAddedAreas = copy.deepcopy(allAddedAreas)
        copy.deepcopy(LA)
        try: #If creating the clusters is possible
            SA = numpy.random.permutation(list(allAreas - allAddedAreas))[0]
            LA = numpy.array([SA])
            c = 1
            neighbors = w[SA]
            discNeighbors = set([])
            lastC = 2
            while c < spines[i] and lastC <> c: # While the cluster is not yet
                lastC = c
                neighbors = list((set(neighbors) - allAddedAreas) - discNeighbors)
                neighbors = numpy.random.permutation(neighbors)
                if len(neighbors) == 0:
                    neighbors = [discNeighbors.pop()]
                addedAreas = [neighbors[0]]
                discNeighbors = discNeighbors | set(neighbors[1: len(neighbors) + 1])
                allAddedAreas = allAddedAreas | set(addedAreas)
                LA = numpy.concatenate((LA, addedAreas))
                neighbors = set(neighbors)
                for x in addedAreas:
                    neighbors = neighbors | set(w[x])
                neighbors = list(neighbors - set(LA))
                c = len(LA)

            discNeighbors = set([])
            neighbors = set([])
            for r in LA: #Neighbors
                neighbors = neighbors | set(w[r])
            while c < AN[i] and lastC <> c: # while cluster is not yet
                lastC = c
                neighbors = list(set(neighbors) - allAddedAreas)
                neighbors = numpy.random.permutation(neighbors)
                chosenNeighbors = min(round(AN[0] - c), len(neighbors))
                if chosenNeighbors == 0:
                    chosenNeighbors = 1
                addedAreas = neighbors[: chosenNeighbors]
                allAddedAreas = allAddedAreas | set(addedAreas)
                LA = numpy.concatenate((LA, addedAreas))
                neighbors = set(neighbors)
                for x in addedAreas:
                    neighbors = neighbors | set(w[x])
                neighbors = list(neighbors - set(LA))
                c = len(LA)
            listOfClusterAreas.append([LA])
            i = i + 1
        except: # If can not create the clusters repeat the process.
            allAddedAreas = copy.deepcopy(savedAllAddedAreas)
            LA = copy.deepcopy(savedLA)
    NPC = nc
    NPA = 0
    for i in range(nc): # Calculating the number of areas in each cluster
        NPA = NPA + len(listOfClusterAreas[i][0])
    posAreaCounter = 0
    negAreaCounter = 0
    avAreaCounter = 0
    for i in range(nc): # For all the clusters
        for x in listOfClusterAreas[i][0]:
            y[x] = [PosAreas[numpy.random.randint(0, posAreaNumber)]]
            posAreaCounter = posAreaCounter + 1
    for i in range(N): #if is an average cluster
        if i not in y:
            y[i] = [avAreas[numpy.random.randint(0, avAreaNumber)]]
        avAreaCounter = avAreaCounter + 1
    return y
