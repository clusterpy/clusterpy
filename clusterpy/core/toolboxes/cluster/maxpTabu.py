# encoding: latin2
"""Max-P-regions
"""
__author__ = "Juan C. Duque"
__credits__ = "Copyright (c) 2009-11 Juan C. Duque"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"

import copy
import numpy
import time as tm
from componentsAlg import AreaManager
from componentsAlg import BasicMemory
from componentsAlg import RegionMaker

__all__ = ['execMaxpTabu']

def execMaxpTabu(y, w, threshold=100.0, maxit=2, tabuLength=5, typeTabu="exact"):
    """Max-p-regions model (Tabu) 

    The max-p-regions model, devised by [Duque_Anselin_Rey2010]_ ,
    clusters a set of geographic areas into the maximum number of homogeneous
    regions such that the value of a spatially extensive regional attribute is
    above a predefined threshold value. In clusterPy we measure heterogeneity as
    the within-cluster sum of squares from each area to the attribute centroid
    of its cluster.

    The max-p-regions algorithm is composed of two main blocks: 
    
    - construction of a initial feasible solution. 
    - local improvement.
    
    There are three methods for local improvement: Greedy (execMaxpGreedy),
    Tabu (execMaxpTabu), and Simulated Annealing (execMaxpSa). A detailed
    explanation of each method can be found in Duque, Anselin and Rey (2010) [Duque_Anselin_Rey2010]_.

    For this version, the tabu search algorithm will stop after
    max(10,N/maxP) nonimproving moves. ::

        layer.cluster('maxpTabu',vars,<threshold>,<wType>,<std>,<maxit>,<tabuLength>,<typeTabu>,<dissolve>,<dataOperations>)

    :keyword vars: Area attribute(s). Important: the last variable in vars correspond to the spatially extensive attribute that will be constrained to be above the predefined threshold value (e.g. ['SAR1','SAR2','POP'])  
    :type vars: list
    :keyword threshold: Minimum value of the constrained variable at regional level. Default value threshold = 100.
    :type threshold: integer
    :keyword wType: Type of first-order contiguity-based spatial matrix: 'rook' or 'queen'. Default value wType = 'rook'. 
    :type wType: string
    :keyword std: If = 1, then the variables will be standardized.
    :type std: binary
    :keyword maxit: Number of times that the construction phase is repeated. The larger the value the higher the possibility of getting a large number of regions. Default value maxit = 2.
    :type maxit: integer
    :keyword tabuLength: Number of times a reverse move is prohibited. Default value tabuLength = 85. 
    :type tabuLength: integer
    :keyword typeTabu: Type of tabu search: (a) exact: chooses the best neighbouring solution for evaluation (it implies the enumeration of all the neighbouring solution at each iteration); (b) "random": evaluates a neighbouring solution selected at random and (See Ricca, F.  and Simeone (2008) for more on the difference between exact and random tabu). Default value typeTabu = "exact". 
    :type typeTabu: string 
    :keyword dissolve: If = 1, then you will get a "child" instance of the layer that contains the new regions. Default value = 0. Note: Each child layer is saved in the attribute layer.results. The first algorithm that you run with dissolve=1 will have a child layer in layer.results[0]; the second algorithm that you run with dissolve=1 will be in layer.results[1], and so on. You can export a child as a shapefile with layer.result[<1,2,3..>].exportArcData('filename')
    :type dissolve: binary
    :keyword dataOperations: Dictionary which maps a variable to a list of operations to run on it. The dissolved layer will contains in it's data all the variables specified in this dictionary. Be sure to check the input layer's fieldNames before use this utility.
    :type dataOperations: dictionary

    The dictionary structure must be as showed bellow.

    >>> X = {}
    >>> X[variableName1] = [function1, function2,....]
    >>> X[variableName2] = [function1, function2,....]

    Where functions are strings which represents the name of the 
    functions to be used on the given variableName. Functions 
    could be,'sum','mean','min','max','meanDesv','stdDesv','med',
    'mode','range','first','last','numberOfAreas. By deffault just
    ID variable is added to the dissolved map.
    """
    print "Running max-p-regions model (Duque, Anselin and Rey, 2010)"
    print "Local search method: Tabu Search"
    print "Number of areas: ", len(y)
    print "threshold value: ", threshold
    distanceType = "EuclideanSquared"
    distanceStat = "Centroid";
    objectiveFunctionType = "SS";
    selectionType = "Minimum";
    numRegionsType = "EndogenousThreshold";
    
    #  CONSTRUCTION PHASE 1: GROWING FEASIBLE REGIONS

    start = tm.time()

    #  print w
    #  print y

    am = AreaManager(w, y, distanceType)
    maxP = 0
    bestCandidates = {}
    for i in range(maxit):

        #  print "**** Iteration %d of %d ..."%(i+1,maxit)

        rm = RegionMaker(am,
                        distanceType = distanceType,
                        distanceStat = distanceStat,
                        selectionType = selectionType,
                        objectiveFunctionType = objectiveFunctionType,
                        numRegionsType = numRegionsType,
                        threshold = threshold)
        numRegions = len(rm.feasibleRegions)
        rm.getObj()

        #  print "rm.feasibleRegions",rm.feasibleRegions
        #  print "obj",rm.getObj()

        if numRegions > maxP:
            bestCandidates = {}
            maxP = numRegions
            obj = rm.objInfo
            bestCandidates[obj] = rm.feasibleRegions
        if numRegions == maxP: 
            obj = rm.objInfo
            if obj in bestCandidates:
                pass
            else:
                bestCandidates[obj] = rm.feasibleRegions
        else:
            pass

    #   print "bestCandidates", bestCandidates
    
    ofValues = bestCandidates.keys()
    basicMemory = BasicMemory()
    while len(ofValues) >= 1:

        #  RECREATE SOLUTION

        rm.resetNow()
        minOfValue = min(ofValues)
        ofValues.remove(minOfValue)
        partialSolution = bestCandidates[minOfValue]

        #  print "ASSIGNING ENCLAVES"
        #  print partialSolution

        regionId = 0
        for growReg in partialSolution:
            seedGrowReg = partialSolution[growReg][0]
            rm.assignSeeds(seedGrowReg, regionId) 
            partialSolution[growReg].remove(seedGrowReg)
            if len(partialSolution[growReg]) >= 1:
                for areaInGrow in partialSolution[growReg]:
                    rm.assignArea(areaInGrow, regionId)
            regionId += 1
            
        # CONSTRUCTION PHASE 2: ENCLAVES ASSIGNATION

        rm.feasibleRegions = copy.deepcopy(rm.region2Area)
        rm.getIntraBorderingAreas()
        rm.newExternal = set(rm.unassignedAreas)
        if len(rm.unassignedAreas) != 0:
            rm.constructionStage = "enclaves"
            while len(rm.unassignedAreas) != 0:
                rm.constructRegions()
        rm.objInfo = rm.getObjective(rm.region2Area)
        rm.feasibleRegions = copy.deepcopy(rm.region2Area)
        rm.getIntraBorderingAreas()

        #  print "ASSIGNED SOLUTION"
        #  print "OBJ: ", rm.getObjective(rm.region2Area), rm.returnRegions()
        
        rm.calculateRegionValueThreshold()

        #  LOCAL SEARCH

        rm.calcObj()
        convTabu = max(10,len(y)/maxP)  #   convTabu=230*numpy.sqrt(maxP)
        
        #  print "###ENTERING TABU",rm.objInfo,rm.returnRegions()

        rm.tabuMove(tabuLength, convTabu = convTabu, typeTabu=typeTabu)
        rm.calcObj()

        #  print "***** AFTER TABU",rm.objInfo,rm.returnRegions()
        #  EVALUATE SOLUTION

        if rm.objInfo < basicMemory.objInfo:
            basicMemory.updateBasicMemory(rm)
    time = tm.time() - start
    Sol = basicMemory.regions
    Of = basicMemory.objInfo
    print "FINAL SOLUTION: ", Sol
    print "FINAL OF: ", Of
    output = { "objectiveFunction": Of,
        "runningTime": time,
        "algorithm": "maxpTabu",
        "regions": len(Sol),
        "r2a": Sol,
        "distanceType": distanceType,
        "distanceStat": distanceStat,
        "selectionType": selectionType,
        "ObjectiveFuncionType": objectiveFunctionType} 
    print "Done"
    return output


