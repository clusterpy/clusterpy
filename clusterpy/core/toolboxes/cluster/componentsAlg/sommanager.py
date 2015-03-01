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

import numpy as np

class somManager():
    """SOM Manager object
    """
    def __init__(self, data, iters, outputLayer, alphaType, initialDistribution,
                 BMUContiguity):
        """This class control all the SOM neural network structure.

        It's the repository of the output layer and the solution
       generator

        @type data: dictionary
        @param data: Input layer data

        @type iters: integer
        @param iters: Number of iterations

        @type outputLayer: Layer
        @param outputLayer: Output Layer object

        @type alphaType: string
        @param alphaType: Type of learning rate

        @type initialDistribution: string
        @param initialDistribution: Neural units initial distribution

        @type BMUContiguity: string
        @param BMUContiguity: Contiguity criterion
        """
        self.alphaType = alphaType
        self.data = data
        nv = len(data[0])
        self.iters = iters
        self.outputLayer = outputLayer

        #  Initializing neural weights

        self.outputLayer.generateData(initialDistribution, 'rook', nv, 0, 1)
        dataNames = self.outputLayer.fieldNames[-1 * nv:]
        self.actualData = outputLayer.getVars(*dataNames)

        #  initializing empty clusters

        self.emptyClusters = {}
        for i in range(len(self.outputLayer.areas)):
            self.emptyClusters[i] = []

        #  initializing feasibles BMU

        self.feasibleBMU = {}
        for i in self.data.keys():
            self.feasibleBMU = outputLayer.Y.keys()

        #  initializing contiguities

        if BMUContiguity == 'rook':
            self.outputContiguity = self.outputLayer.Wrook
        elif BMUContiguity == 'queen':
            self.outputContiguity = self.outputLayer.Wqueen
        elif BMUContiguity == 'custom':
            self.outputContiguity = self.outputLayer.Wcustom
        elif BMUContiguity == 'all':
            for i in self.data.Y.keys():
                self.BMUContiguity[i] = self.data.Y.keys()
        else:
            raise NameError('Invalid contiguity Type')

        #  defining areas order

        self.order = self.data.keys()
        self.solutionsInput = {}

    def __alpha(self, value):
        """
        Decreasing scalar-valued function used to update
        the neural network weights on a specific itereations.
        """
        if self.alphaType == 'linear':
            return (1 - float(value) / self.iters)
        elif self.alphaType == 'quadratic':
            return -1 * (float(value) / self.iters) ** 2 + 1
        else:
            raise NameError('Invalid deacrising function type')

    def findBMU(self, areaId):
        """
        Find the most similar neural weight, usally called on the
        literature such as Best Matching Unit (BMU)
        """
        inputY = self.data[areaId]
        min = vectorDistance(inputY,
              self.actualData[self.feasibleBMU[0]])
        bmu = 0
        for i in self.feasibleBMU[1:]:
            dist = vectorDistance(inputY, self.actualData[i])
            if dist < min:
                min = dist
                bmu = i
        return bmu

    def modifyUnits(self, bmu, areaId, iter):
        """
        Updates the BMU neighborhod
        """
        inputY = self.data[areaId]
        for i in self.outputContiguity[bmu] + [bmu]:
            dist = np.array(inputY) - np.array(self.actualData[i])
            alph = self.__alpha(iter)
            self.actualData[i] = list(np.array(self.actualData[i]) + alph * dist)

    def addSolution(self, iter):
        """
        Manage the solutions of each iteration
        """
        solution = {}
        self.outputLayer.fieldNames += ['iter' + str(iter)]
        for i in self.clusters:
            self.outputLayer.Y[i] += [len(self.clusters[i])]
            for j in self.clusters[i]:
                if self.solutionsInput.has_key(j):
                    self.solutionsInput[j] += [i]
                else:
                    self.solutionsInput[j] = [i]
                solution[j] = i
        return solution.values()

    def compressSolution(self, solution):
        """
        Standarize the not sorted solution.
        """
        count = 0
        order = list(set(solution))
        order.sort()
        sol = [order.index(x) for x in solution]
        return sol


class geoSomManager(somManager):
    """Geo-SOM Manager object
    """
    def __init__(self, data, iters, outputLayer, alphaType, initialDistribution,
                 BMUContiguity, iCentroids, oCentroids):
        """
        This class control all the geoSOM neural network structure.
        Aditionally it's the repository of the output layer and the
        solution generator.

        @type data: dictionary
        @param data: Input layer data

        @type iters: integer
        @param iters: Number of iterations

        @type outputLayer: Layer
        @param outputLayer: Output Layer object

        @type alphaType: string
        @param alphaType: Type of learning rate

        @type initialDistribution: string
        @param initialDistribution: Neural units initial distribution

        @type BMUContiguity: string
        @param BMUContiguity: Contiguity criterion

        @type iCentroids: dictionary
        @param iCentroids: Centroid coordinates for the input Layer areas.

        @type oCentroids: dictionary
        @param oCentroids: Centroid coordinates for the output Layer areas.
        """
        somManager.__init__(self, data, iters, outputLayer, alphaType,
                 initialDistribution, BMUContiguity)
        self.iCentroids = iCentroids
        self.oCentroids = oCentroids
        self.geoWinner, self.feasibleBMU = self.defGeoWinnerAttributes()

    def defGeoWinnerAttributes(self):
        """
            This function define de geoWinners for all the input areas
        """
        geoWinner = {}
        feasibleBMU = {}
        for c in self.iCentroids:
            bestOIndex = 0
            minDistance = vectorDistance(self.iCentroids[c], self.oCentroids[0])
            outputContiguity = self.outputContiguity[0]
            for o in self.oCentroids:
                dis = vectorDistance(self.iCentroids[c], self.oCentroids[o])
                if dis < minDistance:
                    minDistance = dis
                    bestOIndex = o
                    outputContiguity = self.outputContiguity[o] + [o]
            geoWinner[c] = bestOIndex
            feasibleBMU[c] = outputContiguity
        return geoWinner, feasibleBMU

    def findBMU(self, areaId):
        """
        Finds the most similar neural network weight, usally called on the
        literature such as Best Matching Unit (BMU)
        """
        inputY = self.data[areaId]
        feasibleBMU = self.feasibleBMU[areaId]
        min = vectorDistance(inputY,
              self.actualData[feasibleBMU[0]])
        bmu = feasibleBMU[0]
        for i in feasibleBMU:
            dist = vectorDistance(inputY, self.actualData[i])
            if dist < min:
                min = dist
                bmu = i
        return bmu
