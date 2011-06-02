# encoding: latin2
"""Self Organizing Maps
"""
__author__ = "Juan C. Duque, Alejandro Betancourt"
__credits__ = "Copyright (c) 2009-10 Juan C. Duque"
__license__ = "GPL"
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
from componentsAlg import somManager

__all__ = ['originalSOM']

def originalSOM(y,w,
        nRows=10,
        nCols=10,
        iters=1000,
        alphaType='linear',
        initialDistribution='Uniform',
        wType='rook',
        fileName=None):
    """Self Organizing Map(SOM) 

    SOM is an unsupervised neural network proposed by [Kohonen1990]_ 
    which adjust its weights to represent, on a regular lattice, a data set
    distribution.

    In [Kohonen1990]_ the neighbourhood of the Best Matching Unit (BMU) is
    defined in a general form, but in this algorithm it could be any
    contiguity matrix available for a Layer object (rook, queen, custom).

    The original algorithm is commonly used with the output network layer
    represented by a regular hexagonal or rectangular lattice. In clusterPy we
    use a rectangular regular lattice. Finally, the adaptative parameter is
    taken from the scalar version suggested by [Kohonen1990].

    Additionaly In ClusterPy we use contiguity based neighbourhood for the
    weights updating process. For more information see [Kohonen2001]_. ::

        layer.cluster('som',vars,<nRows>,<nCols>,<wType>,<iters>,<alphaType>,<initialDistribution>,<wType>,<fileName>)

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

    :keyword alphaType: Name of the scalar-valued decreasing function which maps iterations onto (0,1) float values. This function is used to define how much modify the BMU neighborhood areas. In clusterPy we have to possible functions: 'linear' (linear decreasing function), or 'quadratic' (quadratic decreasing function). Default value alphaType = 'linear'.
    :type alphaType: string 

    :keyword initialDistribution: Data generator process to initialize the neural wights. Default value initialDistribution = 'uniform'.
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
    print "Original Self Organizing Maps"
    start = tm.time()
    print "---Generating SOM topology---" 
    oLayer = inputs.createGrid(nRows, nCols)
    manager = somManager(y,
                 iters,
                 oLayer,
                 alphaType,
                 initialDistribution,
                 wType)
    print "Done"
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
    "algorithm": "originalSOM",
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
