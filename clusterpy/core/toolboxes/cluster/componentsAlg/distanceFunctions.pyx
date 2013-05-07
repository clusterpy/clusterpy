# encoding: latin2
"""
Distance functions 
"""
__author__ = "Juan C. Duque"
__credits__ = "Copyright (c) 2009-11 Juan C. Duque"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"

import numpy
cimport numpy

cdef double square_double(list x):
    cdef double i, ans = 0.0
    for i in x:
        ans += i*i
    return ans

def distanceA2AEuclideanSquared(list x, std=[],w=[]):
    """
    This function calcule the Euclidean Squared distance between
    two or more variables.
    """
    cdef list distance, d, sublist
    cdef double d2
    cdef unsigned int numrows, row
    cdef numpy.ndarray npsublist

    if std:
        x = numpy.array(x)
        x = numpy.stdobs(x)  #  standardize
        x = x.tolist()
    if w:
        x = numpy.array(x)
        w = w / float(numpy.add.reduce(w))
        x = x * w  #  weights
        x = x.tolist()
        
    numrows = len(x)
#    numrows = numpy.shape(x)[0]
    distance = [0]*(numrows-1)

    for row in xrange(numrows - 1):
        npsublist = numpy.subtract(x[row], x[(row + 1):numrows])
        sublist = npsublist.tolist()
        d2 = square_double(sublist[0])

        distance[row] = [d2]
    return distance




# Distances between solutions

def getHammingDistance(X, Y):
    """
    CLUSTERPY
    getDistanceHamming(X, Y, distanceType):
    Description of the function:
    Return the hamming distance (similarity) of two solutions.
    Parameters
    X: Solution 1
    Y: Solution 2
    Outputs:
    distance: Similarity between the solution (Range [0 - 1])
    Examples:    
    >>> X = [3, 1, 1, 0, 3, 0, 1, 0, 2, 0, 0, 3, 2, 2, 3, 3]
    >>> Y = [0, 0, 0, 3, 0, 3, 3, 3, 2, 3, 3, 1, 2, 2, 1, 1]
    >>> getHammingDistance(X, Y)
    0.1875
    """

    def recode(list X):
        """
        CLUSTERPY
        recode(n, m):
        Description of the function:
        Recodify a array of numbers, putting the number according to the
        position of the variable
        Parameters
        X: Array to recodify
        Outputs:
        XP: Array recodified
        Examples:
        >>> recode([3, 1, 1, 0, 3, 0, 1, 0, 2, 0, 0, 3, 2, 2, 3, 3])
        [0, 1, 1, 2, 0, 2, 1, 2, 3, 2, 2, 0, 3, 3, 0, 0]
        """
        cdef list XP, assigned
        cdef unsigned int i, j, k, lenX
        cdef int r

        XP = X + []
        assigned = []
        r = 0
        lenX = len(X)

        for i in range(lenX):
            if (i not in assigned):
                XP[i] = r
                for j in range(lenX - i - 1):
                    k = i + j + 1
                    if (k not in assigned):
                        if X[k] == X[i]:
                            XP[k] = r
                            assigned.append(k)
                r = r + 1
        return XP

    cdef int lenX, lenY, minLen, maxLen, distance

    lenX = len(X)
    lenY = len(Y)
    if lenX < lenY:
        minLen = lenX
        maxLen = lenY
    else:
        minLen = lenY
        maxLen = lenX
    distance = maxLen - minLen
    XP = recode(X)
    YP = recode(Y)
    for i in range(minLen):
        if XP[i] != YP[i]:
            distance += 1
    return (maxLen - distance + 0.0)/maxLen


def distanceA2AHausdorff(x, y):
    """
    This function calcule the Hausdorff distance between two 
    or more variables.
    """
    distances = []
    for i in range(len(x)):
        distances = distances + [max(abs(y[i][1] - x[i][0]), abs(x[i][1] - y[i][0]))]
    distance = max(distances) 
    return distance



distMethods = {}
distMethods['EuclideanSquared'] = distanceA2AEuclideanSquared
distMethods['Hamming'] = getHammingDistance
distMethods['Hausdorff'] = distanceA2AHausdorff

