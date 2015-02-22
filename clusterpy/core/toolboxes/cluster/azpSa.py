# encoding: latin2
"""AZP-SA
"""
__author__ = "Juan C. Duque"
__credits__ = "Copyright (c) 2009-11 Juan C. Duque"
__license__ = "New BSD License"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"

import numpy
import time as tm
from componentsAlg import AreaManager
from componentsAlg import RegionMaker

__all__ = ['execAZPSA']

def execAZPSA(y, w, pRegions, initialSolution=[], maxit=1):
    """Simulated Annealing variant of Automatic Zoning Procedure (AZP-SA) 

    
    AZP-SA aggregates N zones (areas) into M regions. "The M output regions
    should be formed of internally connected, contiguous, zones." ([Openshaw_Rao1995]_ pp 428).


    AZP-SA is a variant of the AZP algorithm that incorporates a seach
    process, called Simulated Annealing algorithm [Kirkpatrick_Gelatt_Vecchi1983]_.
    Simulated annealing algorithm "permits moves which result in a worse value
    of the objective function but with a probability that diminishes
    gradually, through iteration time" ([Openshaw_Rao1995]_ pp 431).
    
    
    In Openshaw and Rao (1995) the objective function is not defined because
    AZP-Tabu can be applied to any function, F(Z). "F(Z) can be any function
    defined on data for the M regions in Z, and Z is the allocation of each of
    N zones to one of M regions such that each zone is assigned to only one
    region" ([Openshaw_Rao1995]_ pp 428)." In clusterPy we Minimize F(Z),
    where Z is the within-cluster sum of squares from each area to the
    attribute centroid of its cluster.


    In order to make the cooling schedule robust the units of measure of the
    objective function, we set the Boltzmann's equation as: R(0,1) <
    exp((-(Candidate Solution - Current Solution) / Current Solution)/T(k)).
    The cooling schedule is T(k) = 0.85 T(k-1) ([Openshaw_Rao1995]_ pp
    431), with an initial temperature T(0)=1. 
    
    NOTE: The original algorithm proposes to start from a random initial
    feasible solution. Previous computational experience showed us that this
    approach leads to poor quality solutions. In clusterPy we started from an
    initial solution that starts with a initial set of seeds (as many seed as
    regions) selected using the K-means++ algorithm. From those seeds, other
    neighbouring areas are assigned to its closest (in attribute space)
    growing region. This strategy has proven better results. :: 

        layer.cluster('azpSa',vars,regions,<wType>,<std>,<initialSolution>,<maxit>,<dissolve>,<dataOperations>)

    :keyword vars: Area attribute(s) (e.g. ['SAR1','SAR2']) 
    :type vars: list
    :keyword regions: Number of regions 
    :type regions: integer
    :keyword wType: Type of first-order contiguity-based spatial matrix: 'rook' or 'queen'. Default value wType = 'rook'. 
    :type wType: string
    :keyword std: If = 1, then the variables will be standardized.
    :type std: binary
    :keyword initialSolution: List with a initial solution vector. It is useful when the user wants a solution that is not very different from a preexisting solution (e.g. municipalities,districts, etc.). Note that the number of regions will be the same as the number of regions in the initial feasible solution (regardless the value you assign to parameter "regions"). IMPORTANT: make sure you are entering a feasible solution and according to the W matrix you selected, otherwise the algorithm will not converge.
    :type initialSolution: list
    :keyword maxit: For a given temperature, perform SA maxit times (see Openshaw and Rao (1995) pp 431, Step b).  Default value maxit = 1.  NOTE: the parameter Ik, in Step d was fixed at 3.
    :type maxit: integer
    :keyword dissolve: If = 1, then you will get a "child" instance of the layer that contains the new regions. Default value = 0. Note:. Each child layer is saved in the attribute layer.results. The first algorithm that you run with dissolve=1 will have a child layer in layer.results[0]; the second algorithm that you run with dissolve=1 will be in layer.results[1], and so on. You can export a child as a shapefile with layer.result[<1,2,3..>].exportArcData('filename')
    :type dissolve: binary
    :keyword dataOperations: Dictionary which maps a variable to a list of operations to run on it. The dissolved layer will contains in it's data all the variables specified in this dictionary. Be sure to check the input layer's fieldNames before use this utility.
    :type dataOperations: dictionary

    The dictionary structure must be as showed bellow.

    >>> X = {}
    >>> X[variableName1] = [function1, function2,....]
    >>> X[variableName2] = [function1, function2,....]

    Where functions are strings wich represents the name of the 
    functions to be used on the given variableName. Functions 
    could be,'sum','mean','min','max','meanDesv','stdDesv','med',
    'mode','range','first','last','numberOfAreas. By deffault just
    ID variable is added to the dissolved map.

    """
    print "Running original AZP-SA algorithm (Openshaw and Rao, 1995)"
    print "Number of areas: ", len(y)
    if initialSolution != []:
        print "Number of regions: ", len(numpy.unique(initialSolution))
        pRegions = len(numpy.unique(initialSolution))
    else:
        print "Number of regions: ", pRegions
    print "Boltzmann's equation: "
    print "     R(0,1) < exp((-(Candidate Soution - Current Solution) / Current Solution)/T(k))"
    print "Cooling schedule: T(k) = 0.85 T(k-1)"
    if pRegions >= len(y):
        message = "\n WARNING: You are aggregating "+str(len(y))+" into"+\
        str(pRegions)+" regions!!. The number of regions must be an integer"+\
        " number lower than the number of areas being aggregated"
        raise Exception, message 
    
    distanceType = "EuclideanSquared" 
    distanceStat = "Centroid"
    objectiveFunctionType = "SS"
    selectionType = "Minimum"
    alpha = 0.85
    am = AreaManager(w, y, distanceType)
    start = tm.time()

    #  CONSTRUCTION

    rm = RegionMaker(am, pRegions,
                    initialSolution=initialSolution,
                    distanceType=distanceType,
                    distanceStat=distanceStat,
                    selectionType=selectionType,
                    objectiveFunctionType=objectiveFunctionType)
    print "initial solution: ", rm.returnRegions()
    print "initial O.F: ", rm.objInfo

    #  LOCAL SEARCH
    rm.AZPSA(alpha, maxit)

    time = tm.time() - start
    Sol = rm.returnRegions()
    Of = rm.objInfo
    print "FINAL SOLUTION: ", Sol
    print "FINAL OF: ", Of
    output = { "objectiveFunction": Of,
    "runningTime": time,
    "algorithm": "azpSa",
    "regions": len(Sol),
    "r2a": Sol,
    "distanceType": distanceType,
    "distanceStat": distanceStat,
    "selectionType": selectionType,
    "ObjectiveFuncionType": objectiveFunctionType}
    print "Done"
    return output
