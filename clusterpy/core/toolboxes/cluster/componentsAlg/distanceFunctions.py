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

from numpy import add as npadd, array as nparray, subtract as npsubtract

def square_double(x):
    ans = 0.0
    for i in x:
        ans += i*i
    return ans

def distanceA2AEuclideanSquared(x, std=[], w=[]):
    """
    This function calcule the Euclidean Squared distance between
    two or more variables.
    """

    if std:
        x = nparray(x)
        x = stdobs(x)  #  standardize
        x = x.tolist()
    if w:
        x = nparray(x)
        w = w / float(npadd.reduce(w))
        x = x * w  #  weights
        x = x.tolist()

    numrows = len(x)
    distance = [0]*(numrows-1)

    for row in xrange(numrows - 1):
        npsublist = npsubtract(x[row], x[row + 1])
        sublist = npsublist.tolist()
        distance[row] = [square_double(sublist)]

    return distance

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
        XP = X + []
        i = 0
        j = 0
        k = 0
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

    lenX = 0
    lenY = 0
    minLen = 0
    maxLen = 0
    distance = 0

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

