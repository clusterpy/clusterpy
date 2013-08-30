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

import cython
import numpy
cimport numpy

@cython.cfunc
@cython.returns(cython.double)
@cython.locals(x=cython.list, ans=cython.double, i=cython.double)
def square_double(x):
    ans = 0.0
    for i in x:
        ans += i*i
    return ans

@cython.locals(x=cython.list)
def distanceA2AEuclideanSquared(x, std=[],w=[]):
    """
    This function calcule the Euclidean Squared distance between
    two or more variables.
    """
    distance = cython.declare(cython.list)
    d = cython.declare(cython.list)
    sublist = cython.declare(cython.list)
    d2 = cython.declare(cython.double)
    numrows = cython.declare(cython.int)
    row = cython.declare(cython.uint)
    npsublist = cython.declare(numpy.ndarray)

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
    distance = [0]*(numrows-1)

    for row in xrange(numrows - 1):
        npsublist = numpy.subtract(x[row], x[(row + 1):numrows])
        sublist = npsublist.tolist()
        d2 = square_double(sublist[0])

        distance[row] = [d2]
    return distance

@cython.locals(X=cython.list, Y=cython.list)
def getHammingDistance(X, Y):
    """
    CLUSTERPY
    getDistanceHamming(X, Y, distanceType):
    Description of the function:
    Return the Hamming distance (similarity) of two solutions.
    Parameters:
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
    @cython.locals(X=cython.list)
    def recode(X):
        """
        CLUSTERPY
        recode(n, m):
        Description of the function:
        Rename the values of the array according to the order of appearance.
        First value is changed by zero and replaced all occurences, second by
        1 and so on.
        Parameters
        X: Array to re-arrange
        Outputs:
        XP: Array
        Examples:
        >>> recode([3, 1, 1, 0, 3, 0, 1, 0, 2, 0, 0, 3, 2, 2, 3, 3])
        [0, 1, 1, 2, 0, 2, 1, 2, 3, 2, 2, 0, 3, 3, 0, 0]
        """
        XP = cython.declare(cython.list, X + [])
        i = cython.declare(cython.uint)
        j = cython.declare(cython.uint)
        k = cython.declare(cython.uint)
        lenX = cython.declare(cython.uint, len(X))
        r = cython.declare(cython.int, 0)

        assigned = {}

        for i in xrange(lenX):
            if X[i] not in assigned:
                assigned[X[i]] = r
                r += 1

        for i in xrange(lenX):
            XP[i] = assigned[XP[i]]

        return XP

    lenX = cython.declare(cython.int, 0)
    lenY = cython.declare(cython.int, 0)
    minLen = cython.declare(cython.int, 0)
    maxLen = cython.declare(cython.int, 0)
    distance = cython.declare(cython.int, 0)

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
