# encoding: latin2
# cython: profile=True
"""Algorithm utilities
G{packagetree core}
"""
__author__ = "Juan C. Duque"
__credits__ = "Copyright (c) 2009-11 Juan C. Duque"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"

import copy
import numpy
import dist2Regions
import objFunctions
import distanceFunctions
import selectionTypeFunctions
from os import getpid

class AreaManager:
    """
    This class contains operations at areal level, including the generation of
    instances of areas, a wide range of area2area and area2region distance
    functions.  
    """
    def __init__(self, w, y, distanceType="EuclideanSquared", variance="false"):
        """
        @type w: dictionary
        @param w: With B{key} = area Id, and B{value} = list with Ids of neighbours of
        each area. 
        
        @type y: dictionary
        @param y: With B{key} = area Id, and B{value} = list with attribute
        values. 

        @type distanceType: string
        @keyword distanceType: Function to calculate the distance between areas. Default value I{distanceType = 'EuclideanSquared'}.

        @type variance: boolean
        @keyword variance: Boolean indicating if the data have variance matrix. Default value I{variance = 'false'}.
        """
        self.y = y
        self.areas = {}
        self.noNeighs = set([])
        self.variance = variance
        self.distanceType = distanceType
        self.createAreas(w, y)
        self.distanceStatDispatcher = dist2Regions.distanceStatDispatcher

    def createAreas(self, w, y):
        """ 
        Creates instances of areas based on a sparse weights matrix (w) and a
        data array (y).
        """
        n = len(self.y)
        self.distances = {}
        noNeighs = []
        for key in range(n):
            data = y[key]
            try:
                neighbours = w[key]
            except:
                neighbours = {}
                w[key] = {}
            if len(w[key]) == 0:
                self.noNeighs = self.noNeighs | set([key])
            a = AreaCl(key, neighbours, data, self.variance)
            self.areas[key] = a
        if len(self.noNeighs) > 0:
            print "Disconnected areas neighs: ", list(self.noNeighs)

    def returnDistance2Area(self, area, otherArea):
        """
        Returns the distance between two areas
        """
        i = 0
        j = 0
        dist = 0.0
        i = area.id
        j = otherArea.id
        
        if i < j:
            dist = self.distances[(i, j)]
        elif i == j:
            dist = 0.0
        else:
            dist = self.distances[(j, i)]
        return dist

    def getDataAverage(self, areaList, dataIndex):
        """
        Returns the attribute centroid of a set of areas 
        """
        dataAvg = len(dataIndex) * [0.0]
        for aID in areaList:
            i = 0
            for index in dataIndex:
                dataAvg[i] += self.areas[aID].data[index] /len(areaList)
                i += 1
        return dataAvg

    def getDistance2Region(self, area, areaList, distanceStat="Centroid", weights=[], indexData=[]):
        """
        Returns the distance from an area to a region (defined as a list of
        area IDs)
        """
        if isinstance(distanceStat, str):
            if len(indexData) == 0:
                indexData = range(len(area.data))
            return self.distanceStatDispatcher[distanceStat](self, area, areaList, indexData)
        else:
            distance = 0.0
            i = 0
            for dS in distanceStat:
                if len(indexData) == 0:
                    indexDataDS = range(len(area.data))
                else:
                    indexDataDS = indexData[i]
                if len(weights) > 0:
                    distance += weights[i]
                    self.distanceStatDispatcher[dS](self, area, areaList, indexDataDS)
                else:
                    distance += self.distanceStatDispatcher[dS](self, area, areaList, indexDataDS)
                i += 1
            return distance
   
    def getDistance2AreaMin(self, area, areaList):
        """
        Return the ID of the area whitin a region that is closest to an area
        outside the region
        """
        areaMin = -1;
        distanceMin = 1e300
        for aID in areaList:
            if self.distances[area.id, aID] < distanceMin:
                areaMin = aID
                distanceMin = self.distances[area.id, aID]
        return areaMin

    def checkFeasibility(self, solution):
        """
        Checks feasibility of a candidate solution
        """
        n = len(solution)
        regions = {}
        for i in range(n):
            try:
                regions[solution[i]] = regions[solution[i]] + [i]
            except:
                regions[solution[i]] = [i]
        feasible = 1
        r = len(regions)
        for i in range(r):
            if len(regions[i]) > 0:
                newRegion = set([regions[i][0]])
                areas2Eval = set([regions[i][0]])

                while(len(areas2Eval) > 0):
                    area = areas2Eval.pop()
                    areaNeighs = (set(self.areas[area].neighs) & set(regions[i]))
                    areas2Eval = areas2Eval | (areaNeighs - newRegion)
                    newRegion = newRegion | areaNeighs
                if set(regions[i]) -newRegion != set([]):
                    feasible = 0
                    break
        return feasible

class BasicMemory:
    """
    Keeps the minimum amount of information about a given solution. It keeps the
    Objective function value (self.objInfo) and the region each area has been assigned to
    (self.regions)
    """
    def __init__(self, objInfo=99999999E10, regions={}):
        """
        @type objInfo: float 
        @keyword objInfo: Objective function value. 
        
        @type regions: list
        @keyword regions: list of Region´s IDs
        values. 
        """
        self.objInfo = objInfo
        self.regions = regions

    def updateBasicMemory(self, rm):
        """
        Updates BasicMemory when a solution is modified.
        """
        self.objInfo = rm.objInfo
        self.regions = rm.returnRegions()


class ExtendedMemory(BasicMemory):
    """
    This memory is designed to allow the algorithm to go back to a given solution
    (different from the current solution). It gives to RegionManager all the information that must be
    available in order to continue an iteration process. 
    """
    def __init__(self, objInfo=99999999E10, area2Region={}, region2Area={}, 
            intraBorderingAreas={}):
        """     
        @type objInfo: float
        @keyword objInfo: Objective function value
        
        @type area2region: dictionairy
        @keyword area2region: Region to which the area is in.

        @type region2area: dictionary
        @keyword region2area: areas within the region.
        
        @type intraBorderingAreas: dictionary
        @keyword intraBorderingAreas: areas in the border of the region. 
        """
        BasicMemory.__init__(self, objInfo, {})
        self.area2Region = area2Region
        self.region2Area = region2Area
        self.intraBorderingAreas = intraBorderingAreas

    def updateExtendedMemory(self, rm):
        """
        Updates ExtendedMemory when a solution is modified.
        """
        BasicMemory.updateBasicMemory(self, rm)
        self.area2Region = rm.area2Region
        self.region2Area = rm.region2Area
        self.intraBorderingAreas = rm.intraBorderingAreas

cachedObj = {}
cachedFeasible = {}
class RegionMaker:
    """
    This class deals with a large amount of methods required during both the
    construction and local search phases. This class takes the area instances and
    coordinate them during the solution process. It also send information to
    Memory when needed.
    """
    def __init__(self, am, pRegions=2, initialSolution=[], 
                 seedSelection = "kmeans",
                 distanceType = "EuclideanSquared", 
                 distanceStat = "Centroid",
                 selectionType = "Minimum",
                 alpha = 0.2,
                 numRegionsType = "Exogenous",
                 objectiveFunctionType = "SS",
                 threshold = 0.0,
                 weightsDistanceStat = [],
                 weightsObjectiveFunctionType = [],
                 indexDataStat = [],
                 indexDataOF = []):
        """
        @type am: AreaManager
        @param am: Area manager object.

        @type pRegions: integer
        @keyword pRegions: Number of regions in scheme

        @type seeds: list
        @keyword seeds: List of area IDs for initial seeds.

        @type distanceType: string
        @keyword distanceType: Type of distance to be used, by default "EuclideanSquared"

        @type distanceStat: string
        @keyword distanceStat: Type of conversion used for summarizing distance, by defaults "Average"

        @type selectionType: string
        @keyword selectionType: Type of selection criterion for construction phase, by defaults "Minimum"
        
        @type alpha: float.
        @keyword alpha: float equal or between the interval [0,1]; for GRASP selection only.
        
        @type numRegionsType: strigng
        @keyword numRegionsType: Type of constructive method (Exogenous, EndogenousThreshold,
        EndogenousRange), by default "Exogenous"

        @type objectiveFunctionType: string
        @keyword objectiveFunctionType: Methosd to calculate the objective function, by default "Total"

        @type threshold: float
        @keyword threshold: Minimum population threshold to be satisfied for each region

        # FIXME: estos atributos no se que son y lee porfa las funciones de esta clase que no estan muy completas las descripciones pues no sabia bien que hacian algunas.
        @type weightsDistanceStat: list
        @keyword weightsDistanceStat: 

        @type weightsObjectiveFunctionStat: list
        @keyword weightsObjectiveFunctionStat:  

        @type indexDataStat = list
        @keyword indexDataStat:

        @type indexDataOf = list
        @keyword indexDataOf:
        """
        self.am = am
        self.areas = copy.deepcopy(am.areas)
        self.distanceType = distanceType
        self.distanceStat = distanceStat
        self.weightsDistanceStat = weightsDistanceStat
        self.indexDataStat = indexDataStat
        self.weightsObjectiveFunctionType = weightsObjectiveFunctionType
        self.indexDataOF = indexDataOF
        self.selectionType = selectionType
        self.objectiveFunctionType = objectiveFunctionType
        self.n = len(self.areas)
        self.unassignedAreas = self.areas.keys() 
        self.assignedAreas = []
        self.area2Region = {}
        self.region2Area = {}
        self.potentialRegions4Area = {}
        self.intraBorderingAreas = {}
        self.candidateInfo = {}
        self.externalNeighs = set([])
        self.alpha = alpha
        self.numRegionsType = numRegionsType
        self.objectiveFunctionTypeDispatcher = objFunctions.objectiveFunctionTypeDispatcher
        self.selectionTypeDispatcher = selectionTypeFunctions.selectionTypeDispatcher
        self.neighSolutions = {(0,0): 9999}
        self.regionMoves = set([])
        self.distances = {}
        self.NRegion = []
        self.N = 0
        self.data = {}
        self.objInfo = -1
        self.assignAreasNoNeighs()

        #  PREDEFINED NUMBER OF REGIONS

        seeds = []
        regions2createKeys = []
        emptyList = []
        c = 0
        lenUnassAreas = len(self.unassignedAreas)
        s = 0
        i = 0
        lseeds = 0
        if numRegionsType == "Exogenous":
            if not initialSolution:
                self.pRegions = pRegions
                seeds = self.kmeansInit()
                self.setSeeds(seeds)
                c = 0
                while lenUnassAreas > 0:
                    self.constructRegions()
                    lenUnassAreas = len(self.unassignedAreas)
                    c += 1
                self.objInfo = self.getObj()
            else:
                uniqueInitSolution = set(initialSolution)
                self.pRegions = len(uniqueInitSolution)
                seeds = []
                for s in uniqueInitSolution:
                    seeds.append(initialSolution.index(s))
                self.setSeeds(seeds)
                regions2create = {}
                c = 0

                for i in initialSolution:
                    regions2create.setdefault(i, []).append(c)
                    c += 1
                c = 0
                regions2createKeys = regions2create.keys()
                for i in regions2createKeys:
                    self.unassignedAreas = regions2create[i][1:]
                    lenUnassAreas = len(self.unassignedAreas)
                    while lenUnassAreas > 0:
                        self.constructRegions(filteredCandidates=self.unassignedAreas,
                                filteredReg=i)
                        lenUnassAreas = len(self.unassignedAreas)
                        c += 1
                self.objInfo = self.getObj()
        #  NUMBER OF REGIONS IS ENDOGENOUS WITH A THRESHOLD VALUE 

        if self.numRegionsType == "EndogenousThreshold":
            self.constructionStage = "growing"
            try: 
                self.areas[self.areas.keys()[0]].thresholdVar
            except:
                self.extractThresholdVar() 
            self.regionalThreshold = threshold
            c = 0
            self.feasibleRegions = {}
            self.regionValue = {}
            seeds = []
            for aID in self.areas:
                if self.areas[aID].thresholdVar >= self.regionalThreshold:
                    seed = aID
                    seeds = seeds + [seed]
                    self.regionValue[c] = self.areas[seed].thresholdVar
                    self.feasibleRegions[c] = [seed]
                    self.removeRegionAsCandidate()
                    c += 1
            self.setSeeds(seeds)   
            while len(self.unassignedAreas) != 0:
                numpy.random.shuffle(self.unassignedAreas)
                vals = []
                for index in self.unassignedAreas:
                    vals += [self.areas[index].thresholdVar]
                seed = self.unassignedAreas[0]
                self.setSeeds([seed], c)
                self.regionValue[c] = self.areas[seed].thresholdVar
                if  self.regionValue[c] >= self.regionalThreshold:
                    self.feasibleRegions[c] = [seed]
                    self.removeRegionAsCandidate()
                    c += 1
                else:
                    feasibleThreshold = 1
                    while self.regionValue[c] < self.regionalThreshold:
                        self.addedArea = -1
                        try:
                            self.constructRegions()
                            self.regionValue[c] += self.areas[self.addedArea].thresholdVar
                        except:
                            feasibleThreshold = 0
                            break
                    if feasibleThreshold == 1:
                        self.feasibleRegions[c] = self.region2Area[c]
                        self.removeRegionAsCandidate()
                    c += 1

        #  NUMBER OF REGIONS IS ENDOGENOUS WITH A RANGE VALUE 

        if self.numRegionsType == "EndogenousRange":
            self.constructionStage = "growing"  #  there are two values for constructionStage: "growing" and "enclaves"
            try: 
                self.areas[self.areas.keys()[0]].thresholdVar
            except:
                self.extractThresholdVar() 
            self.regionalThreshold = threshold
            c = 0
            self.feasibleRegions = {}
            while len(self.unassignedAreas) != 0:

                #  select seed

                numpy.random.shuffle(self.unassignedAreas) 
                seed = self.unassignedAreas[0]
                self.setSeeds([seed],c)

                #  regionRange contains the current range per region
                #  regionalThreshold is the predefined threshold value

                self.regionRange = {}
                maxValue = self.areas[seed].thresholdVar
                minValue = self.areas[seed].thresholdVar
                currentRange = maxValue - minValue
                self.regionRange[c] = currentRange

                # grow region if possible

                stop = 0
                while stop == 0:
                    upplim = maxValue + self.regionalThreshold - currentRange
                    lowlim = minValue - self.regionalThreshold + currentRange
                    feasibleNeigh = 0
                    toRemove = []
                    for ext in self.externalNeighs:
                        if self.areas[ext].thresholdVar <= upplim and self.areas[ext].thresholdVar >= lowlim:
                            feasibleNeigh = 1
                        if self.areas[ext].thresholdVar > upplim or self.areas[ext].thresholdVar < lowlim:
                            toRemove.append(ext)
                    self.toRemove = toRemove
                    if feasibleNeigh == 0:
                        stop = 1
                    if feasibleNeigh == 1:
                        try:
                            self.constructRegions()
                            if self.areas[self.addedArea].thresholdVar > maxValue:
                                maxValue = self.areas[self.addedArea].thresholdVar
                            if self.areas[self.addedArea].thresholdVar < minValue:
                                minValue = self.areas[self.addedArea].thresholdVar
                            currentRange = maxValue - minValue
                            self.regionRange[c] = currentRange
                        except:
                            stop = 1
                self.feasibleRegions[c] = self.region2Area[c]
                self.removeRegionAsCandidate()
                c += 1
        self.getIntraBorderingAreas()

    def kmeansInit(self):
        cachedDistances = {}
        y = self.am.y
        n = len(y)
        distances = numpy.ones(n)
        total = sum(distances)
        probabilities = map(lambda x: x / float(total), distances)
        seeds = []
        localDistanceType = self.distanceType
        localreturnDistance2Area = AreaCl.returnDistance2Area
        numpy.random.seed(getpid())
        for k in range(self.pRegions):
            random = numpy.random.uniform(0, 1)
            find = False
            acum = 0
            cont = 0
            while find == False:
                inf = acum
                sup = acum + probabilities[cont]
                if inf <= random <= sup:
                    find = True
                    seeds += [cont]
                    selfAmAreas = self.am.areas

                    for area in selfAmAreas:
                        currentArea = selfAmAreas[area]
                        tempMap = []
                        for x in seeds:
                            if x < area:
                                k = (x, area)
                            elif x > area:
                                k = (area, x)
                            else:
                                k = (0,0)
                            cached = cachedDistances.get(k, -1)
                            if cached < 0:
                                newDist = localreturnDistance2Area(currentArea, selfAmAreas[x], distanceType=localDistanceType)
                                tempMap.append(newDist)
                                cachedDistances[k] = newDist

                            else:
                                tempMap.append(cached)
                        distancei = min(tempMap)
                        distances[area] = distancei
                    total = sum(distances)
                    probabilities = map(lambda x: x / float(total), distances)
                else:
                    cont += 1
                    acum = sup
        return seeds
        
    def extractThresholdVar(self):
        """
        Separate aggregation variables (data) from the variable selected
        to satisfy a threshold value (thresholdVar)
        """
        self.totalThresholdVar = 0.0
        for areaId in self.areas.keys():
            self.areas[areaId].thresholdVar = self.areas[areaId].data[-1]
            self.areas[areaId].data = self.areas[areaId].data[0: -1]
            self.totalThresholdVar += self.areas[areaId].thresholdVar

    def removeRegionAsCandidate(self):
        """
        Remove a region from candidates
        """
        for i in self.candidateInfo.keys():
            a, r = i
            if r in self.feasibleRegions:
                self.candidateInfo.pop(i)

    def returnRegions(self):
        """
        Return regions created
        """
        areasId = self.area2Region.keys()
        areasId = numpy.sort(areasId).tolist()
        return [self.area2Region[area] for area in areasId]

    def resetNow(self):
        """
        Reset all variables
        """
        self.unassignedAreas = self.areas.keys()
        self.assignedAreas = []
        self.area2Region = {}
        self.region2Area = {}
        self.potentialRegions4Area = {}
        self.intraBorderingAreas = {}
        self.candidateInfo = {}
        self.externalNeighs = set([])
        self.neighsMinusAssigned = set([])

    def setSeeds(self, seeds, c=0):
        """
        Sets the initial seeds for clustering
        """
        if self.numRegionsType == "Exogenous" and len(seeds) <= self.pRegions:
            idx = range(self.n)
            didx = list((set(idx) - set(seeds)) - self.am.noNeighs)
            numpy.random.shuffle(didx)
            self.seeds = seeds + didx[0:(self.pRegions - len(seeds))]
        else:
            self.seeds = seeds
        for seed in self.seeds:
            self.NRegion += [0]
            self.assignSeeds(seed, c)
            c += 1
       
    def assignAreaStep1(self, areaID, regionID):
        """
        Assgin an area to a region
        """
        a = self.areas[areaID]
        neighs = a.neighs
        try:
            self.region2Area[regionID].append(areaID)
            if self.objectiveFunctionType == "GWalt":
                try:
                    self.NRegion[regionID] += a.data[0]
                    for index in range(1,len(a.data)):
                        self.data[regionID][index - 1] += a.data[index] * a.data[0]
                except:
                    self.NRegion[regionID] = a.data[0]
                    for index in range(1, len(a.data)):
                        self.data[regionID][index - 1] = a.data[index] * a.data[0]
                self.N += a.data[0]
        except:
            self.region2Area[regionID] = [areaID]
            if self.objectiveFunctionType == "GWalt":
                self.NRegion[regionID] = a.data[0]
                for index in range(1, len(a.data)):
                    if index == 1:
                        self.data[regionID] = [a.data[index] * a.data[0]]
                    else:
                        self.data[regionID] += [a.data[index] * a.data[0]]
                self.N += a.data[0]
        self.area2Region[areaID] = regionID
        try:
            aid = self.unassignedAreas.remove(areaID)
        except:
            pass
        self.assignedAreas.append(areaID)
        setNeighs = set(neighs)
        setAssigned = set(self.assignedAreas)
        self.oldExternal = self.externalNeighs
        self.externalNeighs = (self.externalNeighs | setNeighs) - setAssigned 
        self.newExternal = self.externalNeighs - self.oldExternal
        self.neighsMinusAssigned = setNeighs - setAssigned

    def assignSeeds(self, areaID, regionID):
        """
        Assign an area to a region and updates potential regions for the neighs
        Parameters
        """
        self.assignAreaStep1(areaID, regionID)
        for neigh in self.neighsMinusAssigned:
            try:
                self.potentialRegions4Area[neigh] = self.potentialRegions4Area[neigh]|set([regionID])
            except:
                self.potentialRegions4Area[neigh] = set([regionID])

        try:
            self.potentialRegions4Area.pop(areaID)
        except:
            pass
        self.changedRegion = 'null'
        self.newExternal = self.potentialRegions4Area.keys()

    def assignAreasNoNeighs(self):
        """
        Assign to the region "-1" for the areas without neighbours
        """
        noNeighs = list(self.am.noNeighs)
        nr = -1
        for areaID in noNeighs:
            self.area2Region[areaID] = nr 
            try:
                aid = self.unassignedAreas.remove(areaID)
            except:
                pass
            self.assignedAreas.append(areaID)
            setAssigned = set(self.assignedAreas)
        nr = nr - 1
        
    def assignArea(self, areaID, regionID):
        """
        Assign an area to a region and updates potential regions for neighs
        """
        self.changedRegion = regionID
        self.addedArea = areaID
        self.assignAreaStep1(areaID, regionID)
        for neigh in self.neighsMinusAssigned:
            try:
                self.potentialRegions4Area[neigh] = self.potentialRegions4Area[neigh]|set([regionID])
            except:
                self.potentialRegions4Area[neigh] = set([regionID])
        try:
            self.potentialRegions4Area.pop(areaID)
        except:
            pass

    def returnBorderingAreas(self, regionID):
        """
        Returns bordering areas of a region
        """
        areas2Eval = self.returnRegion2Area(regionID)
        borderingAreas = set([])
        for area in areas2Eval:
            try:
                if len(self.intraBorderingAreas[area]) > 0:
                    borderingAreas = borderingAreas | set([area])
            except:
                pass
        return borderingAreas

    def returnIntraBorderingAreas(self):
        """
        Returns intrabordering areas
        """
        return self.intraBorderingAreas

    def getIntraBorderingAreas(self):
        """
        Gets the intrabordering areas
        """
        self.intraBorderingAreas = {}
        if self.numRegionsType == "Exogenous":
            nr = range(self.pRegions)
        else:
            nr = self.feasibleRegions
        for regionID in nr:
            setNeighsNoRegion = set([])
            try:
                areas2Eval = self.region2Area[regionID]
            except:
                areas2Eval = []
            for area in areas2Eval:
                setNeighsNoRegion = setNeighsNoRegion | (set(self.areas[area].neighs) - set(areas2Eval))
            for neigh in list(setNeighsNoRegion):
                try:
                    self.intraBorderingAreas[neigh]=self.intraBorderingAreas[neigh]|set([regionID])
                except:
                    self.intraBorderingAreas[neigh]=set([regionID])

    def returnRegion2Area(self, regionID):
        """
        Return the areas of a region
        """
        return self.region2Area[regionID]

    def constructRegions(self, filteredCandidates=-99, filteredReg=-99):
        """
        Construct potential regions per area
        """
        lastRegion = 0
        for areaID in self.potentialRegions4Area.keys():
            a = self.areas[areaID]
            regionIDs = list(self.potentialRegions4Area[areaID])
            for region in regionIDs:
                if (self.numRegionsType != "Exogenous" and self.constructionStage == "growing"
                        and region in self.feasibleRegions):

                    #  once a region reaches the threshold its grow is rejected until the
                    #  assignation of enclaves

                    pass
                else:
                    if filteredCandidates == -99:
                        if areaID not in self.newExternal and region != self.changedRegion:
                            lastRegion = region
                            pass
                        else:                        
                            if self.selectionType != "FullRandom":
                                areasIdsIn = self.region2Area[region]
                                areasInNow = [ self.areas[aID] for aID in areasIdsIn ]
                                regionDistance = self.am.getDistance2Region(self.areas[areaID], self.region2Area[region],
                                    distanceStat = self.distanceStat, weights = self.weightsDistanceStat,
                                    indexData = self.indexDataStat)
                            else:
                                regionDistance = 0.0
                            self.candidateInfo[(areaID, region)] = regionDistance
                    elif filteredCandidates != -99 and areaID in filteredCandidates and region == filteredReg:
                        areasIdsIn = self.region2Area[region]
                        areasInNow = [ self.areas[aID] for aID in areasIdsIn ]
                        regionDistance = self.am.getDistance2Region(self.areas[areaID], self.region2Area[region],
                            distanceStat = self.distanceStat, weights = self.weightsDistanceStat,
                            indexData = self.indexDataStat)
                        self.candidateInfo[(areaID, region)] = regionDistance
                    else:
                        pass
        if len(self.candidateInfo) == 0:
            self.changedRegion = lastRegion
        if self.numRegionsType == "EndogenousRange":
            self.filterCandidate(self.toRemove)
        self.selectionTypeDispatcher[self.selectionType](self)
        
    def filterCandidate(self, removeCandidate=[]):
        """
        Filter candidates
        """
        if len(removeCandidate) > 0:
            toRemove = []
            for id in removeCandidate:
                for cand,reg in self.candidateInfo.keys():
                    if cand == id:
                        toRemove.append((cand, reg))
            for remov in toRemove:
                self.candidateInfo.pop(remov)

    def graspList(self, xList, alpha=0.0):
        """
        Return random index of values with specified range.
        """
        maxX = max(xList)
        minX = min(xList)
        xRangeMax = minX + ((maxX - minX) * alpha)
        candidates = [i <= xRangeMax for i in xList]
        indices = indexMultiple(candidates, 1)
        nCandidates = len(indices)
        idx = range(nCandidates)
        numpy.random.shuffle(idx)
        random = idx[0]
        index4Grasp = indices[random]
        return index4Grasp
    
    def getObjective(self, region2AreaDict):
        """
        Return the value of the objective function from regions to area dictionary
        """

        if (type(self.objectiveFunctionType) == type('objectiveFunctionType')):
            if len(self.indexDataOF) == 0:
                indexData = range(len(self.areas[0].data))
            else:
                indexData = self.indexDataOF
            return self.objectiveFunctionTypeDispatcher[self.objectiveFunctionType](self, region2AreaDict, indexData)
        else:
            distance = 0.0
            i = 0
            for oFT in self.objectiveFunctionType:
                if len(self.indexDataOF) == 0:
                    indexData = range(len(self.areas[0].data))
                else:
                    indexData = self.indexDataOF[i]
                if len(self.weightsObjectiveFunctionType) > 0:
                    distance += self.weightsObjectiveFunctionType[i] * self.objectiveFunctionTypeDispatcher[oFT](self, region2AreaDict, indexData)
                else:
                    distance += self.objectiveFunctionTypeDispatcher[oFT](self, region2AreaDict, indexData)
                i += 1
            return distance

    def getObjectiveFast(self, region2AreaDict, modifiedRegions=[]):
        """
        Return the value of the objective function from regions to area dictionary
        """

        if (type(self.objectiveFunctionType) == type('objectiveFunctionType')):
            if len(self.indexDataOF) == 0:
                indexData = range(len(self.areas[0].data))
            else:
                indexData = self.indexDataOF
            return self.objectiveFunctionTypeDispatcher[self.objectiveFunctionType+'f'](self, region2AreaDict, modifiedRegions, indexData)
        else:
            distance = 0.0
            i = 0
            for oFT in self.objectiveFunctionType:
                if len(self.indexDataOF) == 0:
                    indexData = range(len(self.areas[0].data))
                else:
                    indexData = self.indexDataOF[i]
                if len(self.weightsObjectiveFunctionType) > 0:
                    distance += self.weightsObjectiveFunctionType[i] * self.objectiveFunctionTypeDispatcher[oFT](self, region2AreaDict, indexData)
                else:
                    distance += self.objectiveFunctionTypeDispatcher[oFT](self, region2AreaDict, indexData)
                i += 1
            return distance

    def getLambda(self):
        """
        # FIXME: No se que hace
        """
        L = numpy.matrix(numpy.identity(self.pRegions))
        for r in range(self.pRegions):
            L[r, r] = 1.0 * self.NRegion[r] / self.N
        return L

    def getB(self):
        """
        Return matrix of parameters of all regions
        """
        B = numpy.matrix(numpy.zeros(len(self.data[0]) * self.pRegions)).T
        index = 0
        for r in range(self.pRegions):
            for i in range(len(self.data[0])):
                B[index, 0] = self.data[r][i] / self.NRegion[r]
                index += 1
        return B

    def getY(self):
        """
        Return matrix of the average variance-covariance of all regions
        """
        Y = numpy.matrix(numpy.identity(len(self.data[0])))
        centroids = {}
        for r in range(self.pRegions):
            centroids[r] = calculateCentroid([self.areas[aID] for aID in self.region2Area[r]])
        for r in range(self.pRegions):
            Y += centroids[r].var * numpy.power(self.NRegion[r] / self.N, 2)
        return Y
    
    def getH(self):
        """
        Return composite matrix
        """
        E = numpy.matrix(numpy.ones((1, self.pRegions, self.pRegions)))
        L = self.getLambda()
        H = L - L * E * L
        return H
    
    def getObj(self):
        """
        Return the value of the objective function
        """
        if self.objInfo < 0:
            self.calcObj()
        return self.objInfo

    def calcObj(self):
        """
        Calculate the value of the objective function
        """
        self.objInfo = self.getObjective(self.region2Area)
        
    def recalcObj(self, region2AreaDict, modifiedRegions=[]):
        """
        Re-calculate the value of the objective function
        """
        if "objDict" in dir(self):
            obj = self.getObjectiveFast(region2AreaDict, modifiedRegions)
        else:
            obj = self.getObjective(region2AreaDict)
            
        return obj
        
    def checkFeasibility(self, regionID, areaID, region2AreaDict):
        """
        Check feasibility from a change region (remove an area from a region)
        """
        areas2Eval = list(region2AreaDict[regionID])
        a2r = set(region2AreaDict[regionID])
        aIDset = set([areaID])
        areas2Eval.remove(areaID)
        key = list(areas2Eval)
        key.sort()
        key = tuple(key)
        seedArea = areas2Eval[0]
        newRegion = (set([seedArea]) | set(self.areas[seedArea].neighs)) & set(areas2Eval)
        areas2Eval.remove(seedArea)
        flag = 1
        newAdded = newRegion - set([seedArea])
        newNeighs = set([])
        while flag:
            for area in newAdded:
                newNeighs = newNeighs | (((set(self.areas[area].neighs) & a2r) - aIDset) - newRegion)
                areas2Eval.remove(area)
            newNeighs = newNeighs - newAdded
            newAdded = newNeighs
            newRegion = newRegion | newAdded
            if len(areas2Eval) == 0:
                feasible = 1
                flag = 0
                break
            elif newNeighs == set([]) and len(areas2Eval) > 0:
                feasible = 0
                flag = 0
                break

        return feasible

    def calculateRegionValueThreshold(self):
        """
        # FIXME: No se que hace
        """
        if self.numRegionsType == "Exogenous":
            nr = range(self.pRegions)
        else:
            nr = range(len(self.region2Area.keys()))
        for regionID in nr:
            self.regionValue[regionID] = 0
            areas2Eval = self.region2Area[regionID]
            for area in areas2Eval:
                self.regionValue[regionID] += self.areas[area].thresholdVar

    def improvingCandidates(self):
        """
        Select solutions that improve the current objective function.
        """
        intraCopy = copy.deepcopy(self.intraBorderingAreas)
        region2AreaCopy = copy.deepcopy(self.region2Area)
        area2RegionCopy = copy.deepcopy(self.area2Region)
        self.neighSolutions = {}
        for area in intraCopy.keys():
            regionIn = self.area2Region[area]
            regions4Move = list(self.intraBorderingAreas[area])
            if (len(self.region2Area[regionIn]) > 1): 
                for region in regions4Move:
                    self.swapArea(area, region, region2AreaCopy, area2RegionCopy)
                    obj = self.recalcObj(region2AreaCopy)
                    self.swapArea(area, regionIn, region2AreaCopy, area2RegionCopy)  
                    if obj < self.objInfo:
                        f = self.checkFeasibility(regionIn, area, self.region2Area)
                        if f == 1:
                            if self.numRegionsType == "Exogenous":
                                self.neighSolutions[(area, region)] = obj
                            elif self.numRegionsType == "EndogenousThreshold":
                                if  self.regionValue[region] >= self.regionalThreshold and self.regionValue[regionIn] >= self.regionalThreshold:
                                    self.neighSolutions[(area,region)] = obj

    def allCandidates(self):
        """
        Select neighboring solutions.
        """
        intraCopy = copy.deepcopy(self.intraBorderingAreas)
        region2AreaCopy = copy.deepcopy(self.region2Area)
        area2RegionCopy = copy.deepcopy(self.area2Region)
        self.neighSolutions = {}
        for area in intraCopy.keys():
            regionIn = self.area2Region[area]
            regions4Move = list(self.intraBorderingAreas[area])
            if (len(self.region2Area[regionIn]) > 1):
                for region in regions4Move:
                    f = self.checkFeasibility(regionIn, area, self.region2Area)
                    if f == 1:
                        if self.numRegionsType == "Exogenous":
                            self.swapArea(area, region, region2AreaCopy, area2RegionCopy)
                            modifiedRegions = [region, regionIn]
                            obj = self.recalcObj(region2AreaCopy, modifiedRegions)
                            self.neighSolutions[(area, region)] = obj
                            self.swapArea(area, regionIn, region2AreaCopy, area2RegionCopy)
                        elif self.numRegionsType == "EndogenousThreshold":
                            self.swapArea(area, region, region2AreaCopy, area2RegionCopy)
                            if self.regionValue[region] >= self.regionalThreshold and self.regionValue[regionIn] >= self.regionalThreshold:
                                obj = self.recalcObj(region2AreaCopy)
                                self.neighSolutions[(area, region)] = obj
                            self.swapArea(area, regionIn, region2AreaCopy, area2RegionCopy)

    def allMoves(self):
        """
        Select all posible moves.
        """        
        moves = []
        for area in self.intraBorderingAreas:
            regionIn = self.area2Region[area]
            regions4Move = list(self.intraBorderingAreas[area])
            if len(self.region2Area[regionIn]) > 1:
                for region in regions4Move:
                    moves = moves + [(area, region)]
        return moves
                            
    def swapArea(self, area, newRegion, region2AreaDict, area2RegionDict):
        """
        Removed an area from a region and appended it to another one
        """
        oldRegion = area2RegionDict[area]
        region2AreaDict[oldRegion].remove(area)
        region2AreaDict[newRegion].append(area)
        area2RegionDict[area] = newRegion
        if self.objectiveFunctionType == "GWalt":
            a = self.areas[area]
            self.NRegion[newRegion] += a.data[0]
            self.NRegion[oldRegion] -= a.data[0]
            for index in range(1, len(a.data)):
                self.data[newRegion][index - 1] += a.data[index] * a.data[0]
            for index in range(1, len(a.data)):
                self.data[oldRegion][index-1] -= a.data[index] * a.data[0]
        if self.numRegionsType == "EndogenousThreshold":
            self.regionValue[newRegion] += self.areas[area].thresholdVar
            self.regionValue[oldRegion] -= self.areas[area].thresholdVar

    def greedyMove(self, typeGreedy="random"):
        """
        Conduct a solution to the best posible with greedy moves
        """
        flag = 1
        self.round = 0
        while flag:
            self.improvingCandidates()
            self.round = 1
            if len(self.neighSolutions.keys()) == 0:
                flag = 0
            else:
                if typeGreedy == "exact":
                    sorted = sortedKeys(self.neighSolutions)
                    move = sorted[numpy.random.randint(0, len(sorted))]
                    area, region = move
                else:
                    values = self.neighSolutions.values()
                    sorted = sortedKeys(self.neighSolutions)                    
                    minVal = min(self.neighSolutions.values())
                    indicesMin = indexMultiple(values, minVal)
                    nInd = len(indicesMin)
                    idx = range(nInd)
                    numpy.random.shuffle(idx)
                    minIndex = indicesMin[idx[0]]
                    area,region = self.neighSolutions.keys()[minIndex]
                self.moveArea(area, region)

                #  self.objInfo = minVal
                
        self.regions = self.returnRegions() 
                
    def updateTabuList(self, newValue, aList, endInd):
        """
        Add a new value to the tabu list.
        """
        return [newValue] + aList[0:endInd-1]
    
    def tabuMove(self, tabuLength = 5, convTabu = 5, typeTabu="exact"):
        """
        Conduct a solution to the best posible with tabu search
        """
        aspireOBJ = self.objInfo
        currentOBJ = self.objInfo
        aspireRegions = self.returnRegions()
        region2AreaAspire = copy.deepcopy(self.region2Area)
        area2RegionAspire = copy.deepcopy(self.area2Region)
        currentRegions = aspireRegions
        bestAdmisable = 9999999.0
        tabuList = [0]*tabuLength
        cBreak = []
        c = 1
        self.round = 0
        resList = []
        epsilon = 1e-10

        while c <= convTabu:

            #  print "regions: ",self.returnRegions(), self.objInfo

            if typeTabu == "exact":
                self.objDict = objFunctions.makeObjDict(self)
                self.allCandidates()

                #print "soluciones vecinas",self.neighSolutions

            else:
                moves = self.allMoves()
            if (typeTabu == "exact" and len(self.neighSolutions) == 0) or (typeTabu == "random" and len(moves) == 0):
                c += convTabu
            else:
                if typeTabu == "exact":
                    sorted = sortedKeys(self.neighSolutions)
                    end = len(sorted)
                else:
                    end = len(moves)
                run = 0
                while run < end:
                    if typeTabu == "exact":
                        move = sorted[run]
                        area,region = move
                        obj4Move = self.neighSolutions[move]
                        candidate = 1
                    else:
                        candidate = 0
                        region2AreaCopy = copy.deepcopy(self.region2Area)
                        area2RegionCopy = copy.deepcopy(self.area2Region)
                        while (candidate == 0 and len(moves) > 0):
                            move = moves[numpy.random.randint(0, len(moves))]
                            moves.remove(move)
                            area, region = move
                            run += 1
                            regionIn = self.area2Region[area]
                            f = self.checkFeasibility(regionIn, area, self.region2Area)
                            if f == 1:
                                if self.numRegionsType == "Exogenous":
                                    self.swapArea(area, region, region2AreaCopy, area2RegionCopy)
                                    obj4Move = self.recalcObj(region2AreaCopy)
                                    self.swapArea(area, regionIn, region2AreaCopy, area2RegionCopy)
                                    candidate = 1
                                elif self.numRegionsType == "EndogenousThreshold":
                                        self.swapArea(area, region, region2AreaCopy, area2RegionCopy)
                                        if  self.regionValue[region] >= self.regionalThreshold and self.regionValue[regionIn] >= self.regionalThreshold:
                                            obj4Move = self.recalcObj(region2AreaCopy)
                                            candidate = 1
                                        self.swapArea(area, regionIn, region2AreaCopy, area2RegionCopy)
                    tabuCount = 0                    
                    if candidate == 1:

                        #  print "--- tabu List:", tabuList

                        if move in tabuList:

                                #  print "move is in tabu list" 

                                if  (aspireOBJ-obj4Move) > epsilon:

                                        #  print "CASE1: improves aspirational: ",aspireOBJ,obj4Move

                                        oldRegion = self.area2Region[area]
                                        tabuList = self.updateTabuList((area, oldRegion), tabuList, tabuLength)
                                        self.moveArea(area, region)
                                        self.objInfo = obj4Move
                                        aspireOBJ = obj4Move
                                        currentOBJ = obj4Move
                                        aspireRegions = self.returnRegions()
                                        region2AreaAspire = copy.deepcopy(self.region2Area)
                                        area2RegionAspire = copy.deepcopy(self.area2Region)
                                        currentRegions = aspireRegions
                                        bestAdmisable = obj4Move
                                        cBreak.append(c)
                                        c = 1
                                        run = end
                                        resList.append([obj4Move, aspireOBJ]) 
                                else:
                                        #  print "CASE 2: does not improve aspirational: ",aspireOBJ,obj4Move

                                        run += 1
                                        tabuCount += 1
                                        tabuList = self.updateTabuList((-1, 0), tabuList, tabuLength)
                                        if tabuCount == end:
                                                c = convTabu
                        else:
                            #  print "move is NOT in tabu list" 
                            
                                if (aspireOBJ-obj4Move) > epsilon:

                                        #  print "CASE 3: improves aspirational: ",aspireOBJ,obj4Move

                                        oldRegion = self.area2Region[area]
                                        tabuList = self.updateTabuList((area, oldRegion), tabuList, tabuLength)
                                        self.moveArea(area, region)
                                        self.objInfo = obj4Move
                                        aspireOBJ = obj4Move
                                        currentOBJ = obj4Move
                                        aspireRegions = self.returnRegions()
                                        region2AreaAspire = copy.deepcopy(self.region2Area)
                                        area2RegionAspire = copy.deepcopy(self.area2Region)
                                        currentRegions = aspireRegions
                                        bestAdmisable = obj4Move
                                        cBreak.append(c)
                                        c = 1
                                        run = end
                                        resList.append( [obj4Move, aspireOBJ] )
                                else:
                                        #  print "CASE 4: does not improve aspirational: ",aspireOBJ,obj4Move

                                        oldRegion = self.area2Region[area]
                                        tabuList = self.updateTabuList((area, oldRegion), tabuList, tabuLength)
                                        self.moveArea(area, region)
                                        self.objInfo = obj4Move
                                        currentOBJ = obj4Move
                                        currentRegions = self.returnRegions()                                        
                                        bestAdmisable = obj4Move

                                        #  cBreak.append(99)

                                        c += 1
                                        run = end
                                        resList.append([obj4Move, aspireOBJ])
                    else:
                        c += convTabu
        self.objInfo = aspireOBJ 
        self.regions = aspireRegions
        self.region2Area = copy.deepcopy(region2AreaAspire)
        self.area2Region = copy.deepcopy(area2RegionAspire)

        #  print "FINAL SOLUTION IN TABU",self.objInfo,self.regions

        self.resList = resList
        self.cBreak = cBreak

    def AZPImproving(self):
        """
        """
        improve = 1
        while improve == 1:
            regions = range(0, self.pRegions)
            while len(regions) > 0:
                
                # step 3

                if len(regions) > 1:
                    randomRegion = numpy.random.randint(0, len(regions))
                else:
                    randomRegion = 0
                region = regions[randomRegion]
                regions.remove(region)

                # step 4

                borderingAreas = list(set(self.returnBorderingAreas(region)) & set(self.returnRegion2Area(region)))
                improve = 0
                while len(borderingAreas) > 0:
                    
                    # step 5

                    randomArea = numpy.random.randint(0, len(borderingAreas))
                    area = borderingAreas[randomArea]
                    borderingAreas.remove(area)
                    posibleMove = list(self.returnIntraBorderingAreas()[area])
                    if len(self.region2Area[region]) >= 2:
                        f = self.checkFeasibility(region, area, self.region2Area)
                    else:
                        f = 0
                    if f == 1:
                        for move in posibleMove:
                            self.swapArea(area, move, self.region2Area, self.area2Region)
                            obj = self.recalcObj(self.region2Area)
                            self.swapArea(area, region, self.region2Area, self.area2Region)
                            if obj <= self.objInfo:
                                self.moveArea(area, move)
                                improve = 1
                                borderingAreas = list(set(self.returnBorderingAreas(region)) & set(self.returnRegion2Area(region)))
                                break

    def AZPSA(self, alpha, temperature):
        """
        Openshaw's Simulated Annealing for AZP algorithm
        """
        totalMoves = 0
        acceptedMoves = 0
        bestOBJ = self.objInfo
        currentOBJ = self.objInfo
        bestRegions = self.returnRegions()
        currentRegions = self.returnRegions()
        region2AreaBest = copy.deepcopy(self.region2Area)
        area2RegionBest = copy.deepcopy(self.area2Region)

        improve = 1
        while improve == 1:
            regions = range(0, self.pRegions)
            while len(regions) > 0:
                
                #  step 3
                if len(regions) > 1:
                    randomRegion = numpy.random.randint(0, len(regions) - 1)
                else:
                    randomRegion = 0
                region = regions[randomRegion]
                regions.remove(region)
                
                # step 4

                borderingAreas = list(set(self.returnBorderingAreas(region)) & set(self.returnRegion2Area(region)))
                improve = 0
                while len(borderingAreas) > 0:
                    # step 5

                    randomArea = numpy.random.randint(0, len(borderingAreas))
                    area = borderingAreas[randomArea]
                    borderingAreas.remove(area)
                    posibleMove = list(self.returnIntraBorderingAreas()[area])
                    if len(self.region2Area[region]) >= 2:
                        f = self.checkFeasibility(region, area, self.region2Area)
                    else:
                        f = 0
                    if f == 1:
                        for move in posibleMove:

                            #  if len(region2AreaCopy[area2RegionCopy[area]]) > 1:

                            self.swapArea(area, move, self.region2Area, self.area2Region)
                            obj = self.recalcObj(self.region2Area)
                            self.swapArea(area, region, self.region2Area, self.area2Region)
                            if obj <= bestOBJ:
                                self.moveArea(area, move)
                                improve = 1
                                self.objInfo = obj
                                bestOBJ = obj
                                currentOBJ = obj
                                bestRegions = self.returnRegions()
                                currentRegions = self.returnRegions()
                                region2AreaBest = copy.deepcopy(self.region2Area)
                                area2RegionBest = copy.deepcopy(self.area2Region)

                                #  print "--- Local improvement (area, region)", area, move
                                #  print "--- New Objective Function value: ", obj
                                #  step 4

                                borderingAreas = list(set(self.returnBorderingAreas(region)) & set(self.returnRegion2Area(region)))
                                break
                            else:
                                random = numpy.random.rand(1)[0]
                                totalMoves += 1
                                if (numpy.exp(-(obj - currentOBJ) / (currentOBJ * temperature))) > random:
                                    acceptedMoves += 1
                                    self.moveArea(area, move)
                                    self.objInfo = obj
                                    currentOBJ = obj
                                    currentRegions = self.returnRegions()

                                    #  print "--- NON-improving move (area, region)", area, move
                                    #  print "--- New Objective Function value: ", obj
                                    #  step 4

                                    borderingAreas = list(set(self.returnBorderingAreas(region)) & set(self.returnRegion2Area(region)))
                                    break
        self.objInfo = bestOBJ 
        self.region2Area = copy.deepcopy(region2AreaBest)
        self.area2Region = copy.deepcopy(area2RegionBest)
 
    def AZPTabuMove(self, tabuLength=5, convTabu=5):
        """
        Tabu search algorithm for Openshaws AZP-tabu (1995)
        """
        aspireOBJ = self.objInfo
        currentOBJ = self.objInfo
        aspireRegions = self.returnRegions()
        region2AreaAspire = copy.deepcopy(self.region2Area)
        area2RegionAspire = copy.deepcopy(self.area2Region)
        currentRegions = copy.deepcopy(aspireRegions)
        tabuList = numpy.zeros(tabuLength)
        tabuList = tabuList.tolist()
        cBreak = []
        c = 1
        self.round = 0
        resList = []
        epsilon = 1e-10

        while c <= convTabu:
            self.objDict = objFunctions.makeObjDict(self)
            self.allCandidates()
            if len(self.neighSolutions) == 0:
                c += convTabu
            else:
                minFound = 0
                neighSolutionsCopy = copy.deepcopy(self.neighSolutions)
                c += 1
                neighNoTabuKeys = list(set(neighSolutionsCopy.keys()) - set(tabuList))
                neighNoTabuDict = dict((key, neighSolutionsCopy[key]) for key in neighNoTabuKeys)                
                if len(neighNoTabuDict) > 0:
                    move = min(neighNoTabuDict, key = lambda x: neighNoTabuDict.get(x))
                    obj4Move = self.neighSolutions[move]
                    moveNoTabu = move
                    obj4MoveNoTabu = obj4Move                    
                    if  (currentOBJ - obj4Move) >= epsilon:
                        minFound = 1
                    else:
                        neighTabuKeys = list(set(neighSolutionsCopy.keys()) & set(tabuList))
                        neighTabuDict = dict((key, neighSolutionsCopy[key]) for key in neighTabuKeys)                
                        if len(neighTabuDict) > 0:
                            move = min(neighTabuDict, key = lambda x: neighTabuDict.get(x))
                            obj4Move = self.neighSolutions[move]
                            moveTabu = move
                            obj4MoveTabu = obj4Move  
                            if  (aspireOBJ - obj4Move) > epsilon:
                                minFound = 1
                if minFound == 1:                    
                    area, region = move
                    obj4Move = self.neighSolutions[move]
                    oldRegion = self.area2Region[area]
                    tabuList = self.updateTabuList((area, oldRegion), tabuList, tabuLength)
                    self.moveArea(area, region)
                    self.objInfo = obj4Move
                    if  (aspireOBJ - obj4Move) > epsilon:
                        aspireOBJ = obj4Move
                        aspireRegions = self.returnRegions()
                        region2AreaAspire = copy.deepcopy(self.region2Area)
                        area2RegionAspire = copy.deepcopy(self.area2Region)
                        c = 1
                    currentOBJ = obj4Move
                    currentRegions = self.returnRegions()
                else:
                    move = moveNoTabu
                    area, region = move
                    obj4Move = self.neighSolutions[move]
                    oldRegion = self.area2Region[area]
                    tabuList = self.updateTabuList((area, oldRegion), tabuList, tabuLength)
                    self.moveArea(area, region)
                    self.objInfo = obj4Move
                    currentOBJ = obj4Move
                    currentRegions = self.returnRegions()
        self.objInfo = aspireOBJ 
        self.regions = aspireRegions
        self.region2Area = copy.deepcopy(region2AreaAspire)
        self.area2Region = copy.deepcopy(area2RegionAspire)
        self.resList = resList

    def reactiveTabuMove(self, convTabu=99):
        """
        AZP 
        Openshaw's Reactive Tabu algorithm  
        """
        
        #  step 2

        tabuLength = 1       
        tabuList = numpy.zeros(tabuLength)
        tabuList = tabuList.tolist()
        rAvg = 1
        K1 = 3
        K2 = 3
        visitedSolutions = []
        allVisitedSolutions = {}
        self.round = 0
        epsilon = 1e-10
        aspireOBJ = self.objInfo
        aspireRegions = self.returnRegions()
        region2AreaAspire = copy.deepcopy(self.region2Area)
        area2RegionAspire = copy.deepcopy(self.area2Region)
        c = 1
        while c <= convTabu:
            improved = 0

            #  step 3

            self.objDict = objFunctions.makeObjDict(self)
            self.allCandidates()
            if len(self.neighSolutions) == 0:
                c += convTabu
            else:
                neighSolutionsCopy = copy.deepcopy(self.neighSolutions)
                neighNoTabuKeys = list(set(neighSolutionsCopy.keys()) - set(tabuList))
                neighNoTabuDict = dict((key, neighSolutionsCopy[key]) for key in neighNoTabuKeys)                
                
                # step 4

                if len(neighNoTabuDict) > 0:
                    move = min(neighNoTabuDict, key = lambda x: neighNoTabuDict.get(x))
                    obj4Move = self.neighSolutions[move]                    
                else:
                    c += convTabu
                    break;
                
                #  step 5

                area, region = move
                obj4Move = self.neighSolutions[move]
                oldRegion = self.area2Region[area]
                tabuList = self.updateTabuList((area, oldRegion), tabuList, tabuLength)
                self.moveArea(area, region)
                self.objInfo = obj4Move

                #  update aspirational

                if  (aspireOBJ - obj4Move) > epsilon:
                    aspireOBJ = obj4Move
                    aspireRegions = self.returnRegions()
                    region2AreaAspire = copy.deepcopy(self.region2Area)
                    area2RegionAspire = copy.deepcopy(self.area2Region)
                    improved = 1

                #  step 6

                currentSystem = self.returnRegions()
                nVisits = visitedSolutions.count(currentSystem)
                if nVisits == 0:

                    #  zoning system not found (go to step 10)
                    #  step 10

                    visitedSolutions.append(currentSystem)
                
                #  step 7

                elif nVisits > K1:
                    try:
                        nVisitsAll = allVisitedSolutions[currentSystem]
                    except:
                        nVisitsAll = 0
                    nVisitsAll =+ 1
                    allVisitedSolutions[currentSystem] = nVisitsAll
                    if nVisitsAll >= K2:

                        #  go to step 11
                        #  step 11a

                        visitedSolutions = []
                        self.objDict = objFunctions.makeObjDict(self)
                        self.allCandidates()
                        moveIndex = range(len(self.neighSolutions))
                        numpy.random.suffle(moveIndex)
                        for move in moveIndex[0:int(1 + 0.5 * rAvg)]:
                            area, region = move
                            obj4Move = self.neighSolutions[move]
                            oldRegion = self.area2Region[area]
                            tabuList = self.updateTabuList((area,oldRegion), tabuList, tabuLength)
                            self.moveArea(area, region)
                            obj4Move = self.neighSolutions[move]

                            #  update aspirational

                            if  (aspireOBJ-obj4Move) > epsilon:
                                aspireOBJ = obj4Move
                                aspireRegions = self.returnRegions()
                                region2AreaAspire = copy.deepcopy(self.region2Area)
                                area2RegionAspire = copy.deepcopy(self.area2Region)
                                improved = 1
                                
                #  step 8

                elif nVisits < K1:
                    rAvg += 1
                    tabuLength = 1.1*tabuLength
                    
                    #  step 9

                    if tabuLength > rAvg:
                        tabuLength = max(0.9 * tabuLength, 1)
                    tabuLength = int(round(tabuLength))

                    #  step 10

                    visitedSolutions.append(currentSystem)
                if improved == 1:
                    c = 1
                else:
                    c += 1

        self.objInfo = aspireOBJ 
        self.regions = aspireRegions
        self.region2Area = copy.deepcopy(region2AreaAspire)
        self.area2Region = copy.deepcopy(area2RegionAspire)

    def moveArea(self, areaID, regionID):
        """
        Move an area to a region
        """
        oldRegion = self.area2Region[areaID]
        self.region2Area[oldRegion].remove(areaID)
        self.region2Area[regionID].append(areaID)
        self.area2Region[areaID] = regionID
        a = self.areas[areaID]
        toUpdate = [areaID] + a.neighs
        if self.objectiveFunctionType == "GWalt":
            self.NRegion[regionID] += a.data[0]
            self.NRegion[oldRegion] -= a.data[0]
        if self.numRegionsType == "EndogenousThreshold":
            self.regionValue[regionID] += self.areas[areaID].thresholdVar
            self.regionValue[oldRegion] -= self.areas[areaID].thresholdVar
        try:
            for index in range(1, len(a.data)):
                self.data[regionID][index - 1] += a.data[index] * a.data[0]
            for index in range(1, len(a.data)):
                self.data[oldRegion][index - 1] -= a.data[index] *a.data[0]
        except:
            pass
        for area in toUpdate:
            regionIn = self.area2Region[area]
            areasIdsIn = self.region2Area[regionIn]
            areasInNow = [self.areas[aID] for aID in areasIdsIn]
            areasInRegion = set(areasIdsIn)
            aNeighs = set(self.areas[area].neighs) 
            neighsInOther = aNeighs - areasInRegion
            if len(neighsInOther) == 0 and area in self.intraBorderingAreas:
                self.intraBorderingAreas.pop(area)
            else:
                borderRegions = set([])
                for neigh in neighsInOther:
                    borderRegions = borderRegions | set([self.area2Region[neigh]])
                if area in self.intraBorderingAreas:
                    self.intraBorderingAreas.pop(area)
                self.intraBorderingAreas[area] = borderRegions
        self.calcObj()

    def recoverFromExtendedMemory(self, extendedMemory):
        """
        Recover a solution form the extended memory
        """
        self.objInfo = extendedMemory.objInfo
        self.area2Region = extendedMemory.area2Region
        self.region2Area = extendedMemory.region2Area
        self.intraBorderingAreas = extendedMemory.intraBorderingAreas

    def getSeeds(self):
        """
        Return the seeds of the solution
        """
        return self.seeds;

def indexMultiple(x,value):
    """
    Return indexes in x with multiple values.
    """
    return [ i[0] for i in enumerate(x) if i[1] == value ]

def calculateGetisG(keyList, dataMean, dataStd, dataDictionary, dataLength):
    """
    This function returns the local G statistic a given region.
    """
    sum = 0
    for i in keyList:
        sum = sum + numpy.double((dataDictionary[i]))
    neighborNumber = len(keyList)
    numerator = sum - dataMean * neighborNumber
    denominator = dataStd * ((float(dataLength * neighborNumber - (neighborNumber ** 2)) / (dataLength - 1)) ** 0.5)
    
    #  denominator = (dataStd*((dataLength*neighborNumber-(neighborNumber**2))/(dataLength-1))**0.5)
    
    G = numerator / denominator
    return G

def quickSortIntersection(dataList, keyList, discardList):
    """
    quickSortIntersection recursively sorts the list of values usinga 
    quick sort algorithm.
    """
    if len(keyList) <= 1:
        return keyList
    else:
        lessData = []
        lessKey = []
        moreData = []
        moreKey = []
        pivot = dataList[-1]
        kpivot = keyList[-1]
        for i in range(len(dataList) - 1):
            if keyList[i] not in discardList:
                if dataList[i] <= pivot:
                    lessData.append(dataList[i])
                    lessKey.append(keyList[i])
                else:
                    moreData.append(dataList[i])
                    moreKey.append(keyList[i])
        return quickSortIntersection(lessData, lessKey, discardList) + [kpivot] + quickSortIntersection(moreData, moreKey, discardList)

def quickSort2(keys, y):
    """
    quickSortIntersection recursively sorts the list of values using a 
    quick sort algorithm.
    """
    if len(keys) <= 1:
        return keys
    else:
        lessData = []
        lessKey = []
        moreData = []
        moreKey = []
        pivot = y[keys[-1]]
        kpivot = keys[-1]
        keys=keys[0: -1]
        for i in keys:
            if y[i] <= pivot:
                lessKey.append(i)
            else:
                moreKey.append(i)
        return quickSort2(lessKey, y) + [kpivot] + quickSort2(moreKey, y)

def neighborSort(dictionary, discardList):
    """
    Returns the list of keys of a dictionary sorted by the
    values that are assigned by them.
    """
    dataList = dictionary.values()
    keyList = dictionary.keys()
    return quickSortIntersection(dataList, keyList, discardList)

def vectorDistance(v1, v2):
    """
    this function calculates de euclidean distance between two 
    vectors.
    """
    sum = 0
    for i in range(len(v1)):
        sum += (v1[i] - v2[i]) ** 2
    return sum ** 0.5

#  INTERNOS

def calculateCentroid(areaList):
    """
    This function return the centroid of an area list
    """
    pg = 0.0
    pk = []
    centroid = AreaCl(0, [], [])
    for area in areaList:
        pg += area.data[0]
        pk = pk + [area.data[0]]
    pkPg = numpy.matrix(pk).T / pg
    data = [0.0] * len(area.data)
    var = numpy.matrix(areaList[0].var) * 0.0
    j = 0
    for area in areaList:
        var += area.var * pow(pkPg[j, 0], 2)
        for i in range(len(area.data)):
            data[i] += area.data[i] * pkPg[j, 0]
        j += 1
    centroid.data = data
    centroid.var = var
    return centroid


def factorial(n):
    """
    Returns the factorial of a number.
    """
    fact = 1.0
    if n > 1:
        fact = n * factorial(n - 1)
    return fact

def comb(n, m):
    """
    This function calculates the number of possible combinations of n items
    chosen by m.
    """
    return factorial(n) / (factorial(m) * factorial(n - m))

def recode(X):
    """
    Tranform a list with regions begining in x to a lis begining in 0.
    """
    XP = X + []
    assigned = []
    r = 0
    for i in range(len(X)):
        if (i not in assigned):
            XP[i] = r
            for j in range(len(X) - i - 1):
                k = i + j + 1
                if (k not in assigned):
                    if X[k] == X[i]:
                        XP[k] = r
                        assigned = assigned + [k]
            r = r + 1
    return XP

def sortedKeys(d):
    """
    Return keys of the dictionary d sorted based on their values.
    """
    values = d.values()
    sortedIndices = numpy.argsort(values)
    sortedKeys = [d.keys()[i] for i in sortedIndices]
    minVal = min(values)
    countMin = values.count(minVal)
    if countMin > 1:
        minIndices = sortedKeys[0: countMin]
        nInd = len(minIndices)
        idx = range(nInd)
        numpy.random.shuffle(idx)
        permMins = idx
        c = 0
        for i in range(nInd):
            place = permMins[c]
            sortedKeys[c] = minIndices[place] 
            c += 1
    return sortedKeys

def feasibleRegion(feasDict):
    """
    Return if a list of areas are connected
    """
    areas2Eval = []
    areas = {}
    for key in feasDict.keys():
        try:
            neighbours = feasDict[key]
        except:
            neighbours = {}
        a = AreaCl(key, neighbours, [])
        areas[key] = a
        areas2Eval = areas2Eval + [key]
    feasible = 1
    newRegion = set([])
    for area in areas2Eval:
        newRegion = newRegion | (set(areas[area].neighs) & set(areas2Eval))
    if set(areas2Eval) - newRegion != set([]):
        feasible = 0
    return feasible

class AreaCl:
    """
    Area Class for Regional Clustering.
    """
    def __init__(self, id, neighs, data, variance="false"):
        """
        @type id: integer
        @param id: Id of the polygon/area

        @type neighs: list
        @param neighs: Neighborhood ids

        @type data: list.
        @param data: Data releated to the area.
        
        @type variance: boolean
        @keyword variance: Boolean indicating if the data have variance matrix
        """
        self.id = id
        self.neighs = neighs
        if variance == "false":
            self.data = data
        else:
            n = (numpy.sqrt(9 + 8 * (len(data) - 1)) - 3) / 2
            self.var = numpy.matrix(numpy.identity(n))
            index = n + 1
            for i in range(int(n)):
                for j in range(i + 1):
                    self.var[i, j] = data[int(index)]
                    self.var[j, i] = data[int(index)]
                    index += 1
            self.data = data[0: int(n + 1)]
    
    def returnDistance2Area(self, otherArea, distanceType="EuclideanSquared", indexData=[]):
        """
        Return the distance between the area and other area
        """
        y0 = []
        y1 = []
        index = 0
        if len(indexData) == 0:
            indexData = range(len(self.data))
        for index in indexData:
            y0 += [self.data[index]]
            y1 += [otherArea.data[index]]
#        data = numpy.concatenate(([y0], [y1]))
        data = [y0] + [y1]
        areaDistance = distanceFunctions.distMethods[distanceType](data)
        try:
            dist = areaDistance[0][0]
        except:
            dist = areaDistance[0]
        return dist

class somManager():
    """SOM Manager object
    """
    def __init__(self,
                 data,
                 iters,
                 outputLayer,
                 alphaType,
                 initialDistribution,
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
            dist = numpy.array(inputY) - numpy.array(self.actualData[i])
            alph = self.__alpha(iter)
            self.actualData[i] = list(numpy.array(self.actualData[i]) \
                                     + alph * dist)

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
    def __init__(self,data,
                 iters,
                 outputLayer,
                 alphaType,
                 initialDistribution,
                 BMUContiguity,
                 iCentroids,
                 oCentroids):
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
        somManager.__init__(self,data,
                 iters,
                 outputLayer,
                 alphaType,
                 initialDistribution,
                 BMUContiguity)
        self.iCentroids=iCentroids
        self.oCentroids=oCentroids
        self.geoWinner, self.feasibleBMU=self.defGeoWinnerAttributes()
    
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
        
