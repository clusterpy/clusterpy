# encoding: latin2
"""ARiSeL
"""
__author__ = "Juan C. Duque and Richard L. Church"
__credits__ = "Copyright (c) 2009-11 Juan C. Duque"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"

import numpy
import time as tm
from componentsAlg import AreaManager
from componentsAlg import ExtendedMemory
from componentsAlg import RegionMaker
from multiprocessing import Process, Queue, Pool

__all__ = ['execArisel']

def constructPossible(am, pRegions, initialSolution, distanceType, distanceStat,
                      selectionType, objectiveFunctionType):
    """Create one instance of a region maker"""
    rm = RegionMaker(am, pRegions,
                     initialSolution = initialSolution,
                     distanceType = distanceType,
                     distanceStat = distanceStat,
                     selectionType = selectionType,
                     objectiveFunctionType = objectiveFunctionType)
    return rm
#    par_queue.put(rm)


def execArisel(y, w, pRegions, inits=3, initialSolution=[],
               convTabu=0, tabuLength=10):
    """Automatic Rationalization with Initial Seed Location

    ARiSeL, proposed by [Duque_Church2004]_ , aggregates N areas into P
    spatially contiguous regions while minimizing intra-regional heterogeneity
    (measured as the within-cluster sum of squares from each area to the
    attribute centroid of its cluster). This algorithm is a modification of
    Openshaw's AZP-tabu [Openshaw_Rao1995]_. In ARISeL the construction of a
    initial feasible solution is repeated several times (inits) before
    running Tabu Search algorithm [Glover1977]_.


    Duque and Church argue that:


        - constructing and initial feasible solution is computationally less
        expensive than performing local search.


        - local search by moving bordering areas between region do not allow
        an extensive search in the solution space and it is computationally
        expensive.


    Based on those two ideas, the authors propose to generate as many
    different initial feasible solutions and run Tabu search on the best
    initial solution obtained so far.


    The initial solution follows a "growing regions" strategy. It starts with
    a initial set of seeds (as many seed as regions) selected using the
    K-means++ algorithm. From those seeds, other neighbouring areas are
    assigned to its closest (in attribute space) growing region. This strategy
    has proven better results. ::

        Layer.cluster('arisel', vars, regions, <wType>, <std>, <inits>,
        <initialSolution>, <convTabu>, <tabuLength>,
        <dissolve>, <dataOperations>)

    :keyword vars: Area attribute(s) (e.g. ['SAR1','SAR2'])
    :type vars: list
    :keyword regions: Number of regions
    :type regions: integer
    :keyword wType: Type of first-order contiguity-based spatial matrix: 'rook'
    or 'queen'. Default value wType = 'rook'.
    :type wType: string
    :keyword std: If = 1, then the variables will be standardized.
    :type std: binary
    :keyword inits: number of initial feasible solutions to be constructed
    before applying Tabu Search.
    :type inits: integer. Default value inits = 5.
    :keyword initialSolution: List with a initial solution vector. It is useful
    when the user wants a solution that is not very different from a preexisting
    solution (e.g. municipalities,districts, etc.). Note that the number of
    regions will be the same as the number of regions in the initial feasible
    solution (regardless the value you assign to parameter "regions").
    IMPORTANT: make sure you are entering a feasible solution and according to
    the W matrix you selected, otherwise the algorithm will not converge.
    :type initialSolution: list
    :keyword convTabu: Stop the search after convTabu nonimproving moves
    (nonimproving moves are those moves that do not improve the current
    solution.
    Note that "improving moves" are different to "aspirational moves").
    If convTabu=0 the algorithm will stop after Int(M/N) nonimproving moves.
    Default value convTabu = 0.
    :type convTabu: integer
    :keyword tabuLength: Number of times a reverse move is prohibited. Default
    value *tabuLength = 10*.
    :type tabuLength: integer
    :keyword dissolve: If = 1, then you will get a "child" instance of the layer
    that contains the new regions. Default value *dissolve = 0*.  **Note:**.
    Each child layer is saved in the attribute *layer.results*.  The first
    algorithm that you run with *dissolve=1* will have a child layer in
    *layer.results[0]*; the second algorithm that you run with *dissolve=1* will
    be in *layer.results[1]*, and so on. You can export a child as a shapefile
    with *layer.result[<1,2,3..>].exportArcData('filename')*
    :type dissolve: binary
    :keyword dataOperations: Dictionary which maps a variable to a list of
    operations to run on it. The dissolved layer will contains in it's data all
    the variables specified in this dictionary. Be sure to check the input
    layer's fieldNames before use this utility.
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
    lenY = len(y)
    i = 0
    start = 0.0
    time1 = 0.0
    time2 = 0.0
    extendedMemoryObjInfo = 0.0
    rmObjInfo = 0.0

    print "Running original Arisel algorithm"
    print "Number of areas: ", lenY
    if initialSolution:
        print "Number of regions: ", len(numpy.unique(initialSolution))
        pRegions = len(set(initialSolution))
    else:
        print "Number of regions: ", pRegions
    if pRegions >= lenY:
        message = "\n WARNING: You are aggregating "+str(lenY)+" into"+\
        str(pRegions)+" regions!!. The number of regions must be an integer"+\
        " number lower than the number of areas being aggregated"
        raise Exception(message)

    if convTabu <= 0:
        convTabu = lenY/pRegions  #   convTabu = 230*numpy.sqrt(pRegions)
    distanceType = "EuclideanSquared"
    distanceStat = "Centroid"
    objectiveFunctionType = "SS"
    selectionType = "Minimum"
    am = AreaManager(w, y, distanceType)
    extendedMemory = ExtendedMemory()

    pool = Pool(processes = 16)
    procs = []

    start = tm.time()
    for dummy in xrange(inits):
        ans = pool.apply_async(constructPossible, [am, pRegions,
                                                   initialSolution,
                                                   distanceType,
                                                   distanceStat,
                                                   selectionType,
                                                   objectiveFunctionType])
        procs.append(ans)


    results = []
    for p in procs:
        results.append(p.get())

    tmp_ans = extendedMemory
    for rm in results:
        if rm.objInfo < tmp_ans.objInfo:
            tmp_ans = rm
    rm = tmp_ans
    extendedMemory.updateExtendedMemory(rm)

    rm.recoverFromExtendedMemory(extendedMemory)
    print "initial Solution: ", rm.returnRegions()
    print "initial O.F: ", rm.objInfo
    rm.tabuMove(tabuLength=tabuLength, convTabu=convTabu)
    time2 = tm.time() - start
    Sol = rm.regions
    Of = rm.objInfo
    print "FINAL SOLUTION: ", Sol
    print "FINAL OF: ", Of
    output = { "objectiveFunction": Of,
    "runningTime": time2,
    "algorithm": "arisel",
    "regions": len(Sol),
    "r2a": Sol,
    "distanceType": distanceType,
    "distanceStat": distanceStat,
    "selectionType": selectionType,
    "ObjectiveFuncionType": objectiveFunctionType}
    print "Done"
    return output
