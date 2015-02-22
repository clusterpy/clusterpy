# encoding: latin2
"""Self Organizing Maps
"""
__author__ = "Juan C. Duque, Alejandro Betancourt"
__credits__ = "Copyright (c) 2009-10 Juan C. Duque"
__license__ = "New BSD License"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"

import sys
import os
path = os.path.split(__file__)[0]
path = os.path.split(path)[0]
path = os.path.split(path)[0]
sys.path += [path]
import copy
import inputs
import time as tm
from componentsAlg import geoSomManager
from componentsAlg import somManager

__all__ = ['geoSom']

def geoSom(iLayer,iVariables,
        nRows=10,
        nCols=10,
        iters = 1000,
        wType = 'rook',
        alphaType = 'linear',
        initialDistribution = 'Uniform',
        fileName = None):
    """Geo Self Organizing Map(geoSOM) 

    GeoSOM is an unsupervised neural network proposed by [Bacao_Lobo_Painho2004]_
    , which adjust his weights to represent, on a regular lattice, a data
    set distribution. The difference between the algorithm suggested by
    [Bacao_Lobo_Painho2004]_ and the suggested by [Kohonen1990] is that the first one
    uses the geographical location of the output network layer to organize
    the values given in the input Layer. :: 

        layer.cluster('geoSom',vars,nRows,nCols,<wType>,<iters>,<alphaType>,<initialDistribution>,<wType>,<fileName>)

    :keyword vars: Area attribute(s) 
    :type vars: list
    
    :keyword nRows: Number of rows in the lattice 
    :type nRows: list

    :keyword nCols: Number of columns in the lattice
    :type nCols: list

    :keyword wType: Type of first-order contiguity-based spatial matrix: 'rook' or 'queen'. Default value wType = 'rook'. 
    :type wType: string

    :keyword iters: Number of iterations for the SOM algorithm. Default value iters = 1000.
    :type iters: integer

    :keyword alphaType: Name of the scalar-valued decreasing function which maps iterations onto (0,1) float values. This function is used to define how much modify the BMU neighborhood areas. In clusterPy we have to possible functions: 'linear' (linear decreasing function), or 'quadratic'(quadratic decreasing function). Default value alphaType = 'linear'.
    :type alphaType: string 

    :keyword initialDistribution: Data generator process to be used used to initialized the neural wights. Default value initialDistribution = 'uniform'.
    :type initialDistribution: string

    :keyword fileName: Parameter used to export neural output layer topology as a shapefile. Default value fileName = None.
    :type fileName: string

    IMPORTANT NOTE: 
    
    Since this algorithm does not guarantee spatial contiguity of the
    resulting regions, clusterPy does not provide the dissolve option. to
    obtain the solution vector you will need to export the layer with the
    command "Layer.exportArcData". The exported shape file will have an
    additional variable with the solution vector (i.e., ID of the region to
    which the area has been assigned).
    """
    print "Geo-Som"
    start = tm.time()
    print "---Generating geo SOM topology---" 
    bbox = iLayer.bbox
    oLayer = inputs.createGrid(nRows,nCols,
                               (bbox[0],bbox[1]),
                               (bbox[2],bbox[3]))
    oCentroids = oLayer.getCentroids()
    iCentroids = iLayer.getCentroids()
    y = iLayer.getVars(*iVariables)
    manager = geoSomManager(y,
                 iters,
                 oLayer,
                 alphaType,
                 initialDistribution,
                 wType,
                 iCentroids,
                 oCentroids)
    for iter in range(iters):
        manager.clusters = copy.deepcopy(manager.emptyClusters)
        for areaId in manager.order:
            bmu = manager.findBMU(areaId)
            manager.clusters[bmu] += [areaId]
            manager.modifyUnits(bmu, areaId, iter)
        solution = manager.addSolution(iter)
    time = tm.time() - start
    Sol = manager.compressSolution(solution)
    Of = 0
    print "FINAL SOLUTION: ", Sol
    print "FINAL O.F.: ", Of
    output = { "objectiveFunction": Of,
    "runningTime": time,
    "algorithm": "geoSOM",
    "regions": len(Sol),
    "r2a": Sol,
    "distanceType": None,
    "distanceStat": None,
    "selectionType": None,
    "ObjectiveFuncionType": None,
    "SOMOutputLayer": manager.outputLayer}
    print "Done"
    if fileName <> None:
        manager.outputLayer.exportArcData(fileName)
    return output
