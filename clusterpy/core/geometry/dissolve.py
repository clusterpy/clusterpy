# encoding: latin2
"""Dissolve manager
"""
__author__ = "Boris Dev,Juan C. Duque, Alejandro Betancourt"
__credits__ = "Copyright (c) 2009-10 Juan C. Duque"
__license__ = "New BSD License"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"
__all__ = ['dissolveLayer']

import copy
import re
import numpy

# dissolveLayer
# dissolveMap
# getScaleRatio
# scale
# readAreas
# reconnect
# invertScale
# Area
# Ring
# Point
# Segment
# MultiRingCluster
# connector
# isHole
# getArea

def dissolveLayer(father, son, region2areas):
    """Dissolve method based on segment intersections

    :param region2areas: Output algorithm vector
    :type region2areas: list
    """
    if not region2areas:
        print "Problem: No clustering algorithm has been executed on the layer"
    if len(region2areas) != len(father.areas):
        print "Problem: Amount of assigned regions does not match number of areas"
        print "Regions:", father.region2areas
    else:
        areas = father.areas
        s,mx,my = getScaleRatio(areas, canvasH=500, canvasW=500)
        scAreas = scale(areas)
        areaObjs, ringObjs, wq, wr, v = readAreas(scAreas)   
        try:
            clusterObjs = dissolveMap(scAreas, areaObjs, ringObjs, region2areas)
            scaledAreas = reconnect(clusterObjs)
            son.areas = invertScale(s, mx, my,scaledAreas)
            son.areaObjs, son.ringObjs, son.Wqueen,son.Wrook, vertexList = \
                readAreas(son.areas)
            son.fieldNames = copy.deepcopy(father.fieldNames)
            son.father = father
            son.shpType = 'polygon'
            son.name = father.name + '_' + str(len(father.results))
            father.results.append(son)
        except KeyError as ke:
            print "clusterPy is not able to dissolve your map based on this solution.\
Please execute the command Layer.exportArcData(""dissolveProblem"") and send us \
the resulting files to software@rise-group.org to analyse the problem and give \
you a solution as soon asposible. Your feedback is important for us."
            raise ke
        except ValueError as ve:
            print "clusterPy is not able to dissolve your map based on this solution.\
Please execute the command Layer.exportArcData(""dissolveProblem"") and send us \
the resulting files to software@rise-group.org to analyse the problem and give \
you a solution as soon asposible. Your feedback is important for us."
            raise ve
        
         
def dissolveMap(originalAREAS, areaObjsList, ringObjsDict, regions):
    AREAS = originalAREAS
    RegAreaObjsD = {} # RegAreaObjsD is {region : [areaObjs]}
    for oldareaIdx, region in enumerate(regions):
        if RegAreaObjsD.has_key(region):
            RegAreaObjsD[region].append(areaObjsList[oldareaIdx])
        else:
            RegAreaObjsD[region]=[areaObjsList[oldareaIdx]]

    # 1. Consolidate all rings of a new clustered area

    clusters = []
    for idx, region_key in enumerate(RegAreaObjsD.keys()):
        clusterObj = MultiRingCluster()
        clusters.append(clusterObj)
        for areaObj in RegAreaObjsD[region_key]:
            clusterObj.ringIds.extend(areaObj.ringIds)
            for ringObj in areaObj:
                    clusterObj.append(ringObj)

    # 2. Make ring sets based on neighboring ring structure     
    # NOTE: clustered areas do not have to be contiguous for alg to work
    # REVIEW THIS CODE BELOW!!

    ringcount = 0
    colortext = ["pink", "yellow", "grey", "blue", "red", "green"]
    NEWAREAS = []
    for n_c, clusterObj in enumerate(clusters):
        newArea = []
        NEWAREAS.append(newArea)
        for n, ringObj in enumerate(clusterObj):
            # check if ring is a hole
            if ringObj.isHole == True: 
                clusterObj.holeRings.append(ringObj)
            else:
                # KEY TO FINDING CONTIGUOUS RINGS 
                intersect = set(ringObj.ringNeighbors) & set(clusterObj.ringIds)
                if len(intersect) == 0: # island
                    clusterObj.independentRings.append(ringObj)
                else:
                    newset = set()
                    newsets = newset
                    newsets.update([id(ringObj)])
                    newsets.update(intersect)
                    if len(clusterObj.contiguosRings) == 0: # if no contiguous rings
                        clusterObj.contiguosRings.append(newset)
                    else:  # consolidation HERE
                        memberships = [len(ringset & newset) > 0 for ringset in clusterObj.contiguosRings]
                        total = sum(memberships)
                        if total == 0:
                            clusterObj.contiguosRings.append(newset)
                        elif total == 1:
                            for idx, check in enumerate(memberships):
                                if check == True:
                                    clusterObj.contiguosRings[idx].update(newset)
                        else:  # total > 1 so colsolidate the sets
                            toberemoved = []
                            for idx, check in enumerate(memberships):
                                if check == True:
                                    oldset = clusterObj.contiguosRings[idx]
                                    newsets.update(oldset)
                                    toberemoved.append(oldset)
                            clusterObj.contiguosRings.append(newset)
                            for x in toberemoved:        
                                clusterObj.contiguosRings.remove(x)

        # 3. dissolve each set of contiguous rings into a new ringObj

        if len(clusterObj.contiguosRings) > 0: 
            for ringset in clusterObj.contiguosRings:
                segs = []
                for ringId in ringset:
                    segs.extend([segmentObj.sorted for segmentObj in ringObjsDict[ringId].segments])

        # remove segments shared by 2 areas in the same regional cluster

                segmentsToKeep = []
                segs.sort()
                if segs[0] != segs[1]:
                    segmentsToKeep.append(segs[0])
                i = 1
                while i < (len(segs) - 1):
                    if segs[i - 1] != segs[i] != segs[i + 1]:
                        segmentsToKeep.append(segs[i])
                    i += 1
                if segs[-2] != segs[-1]:
                    segmentsToKeep.append(segs[-1])
                clusterObj.unlinkedSegments.append(segmentsToKeep)
    return clusters

def getScaleRatio(shapes, canvasH=500, canvasW=500):
    buff = .05  # % white space of canvas between map and window edge, to see peripheral maplines
    canvasH = canvasH * (1.0 - buff)
    canvasW = canvasW * (1.0 - buff)
    xs = []
    ys = []
    for shape in shapes:
        for ring in shape:
            xs.extend([tup[0] for tup in ring])
            ys.extend([tup[1] for tup in ring])
    minxs = min(xs)     
    maxxs = max(xs)    
    minys = min(ys)    
    maxys = max(ys)  
    if abs(minxs - maxxs) > abs(minys - maxys):  # xdim is longer than y dim
        scale = canvasW / abs(minxs - maxxs)
    else:
        scale = canvasH / abs(minys - maxys)
    return scale, minxs, minys    

def scale(shapes, canvasH=500, canvasW=500):
    buff = .05  # % white space of canvas between map and window edge, to see peripheral maplines
    canvasH = canvasH * (1.0 - buff)
    canvasW = canvasW * (1.0 - buff)
    xs = []
    ys = []
    for shape in shapes:
        for ring in shape:
            xs.extend([tup[0] for tup in ring])
            ys.extend([tup[1] for tup in ring])
    minxs = min(xs)     
    maxxs = max(xs)    
    minys = min(ys)    
    maxys = max(ys)  
    if abs(minxs - maxxs) > abs(minys - maxys):  # xdim is longer than y dim
        scale = canvasW / abs(minxs - maxxs)
    else:
        scale = canvasH / abs(minys - maxys)
    canvasShapes = []
    for shape in shapes:
        newshape = []
        for ring in shape:
            newring = []
            x=[((x - minxs) * scale) + 5 for x in [p[0] for p in ring]]
            y=[500 - ((y-minys) * scale) - 5 for y in [p[1] for p in ring]]
            points = zip(x, y)
            newring.extend(points)
            newshape.append(newring)
        canvasShapes.append(newshape)    
    return canvasShapes    

def readAreas(AREAS):
    #  Map Meta-info

    areaObjsList = []  # to draw, ie. areaObj.ringObjs or .draw() .highlight()
    ringObjsDict = {}  # to loop through to make ring.lines    
    point2areas = {}  # to get queen neighbors where point shared by 2 areas,below..
    Wqueen = dict([(idx, set()) for idx in range(len(AREAS))])
    segment2areas = {}  # to get rook neighbors where segment is shared by 2 areas,below..
    Wrook = dict([(idx,[]) for idx in range(len(AREAS))])
    segment2rings = {} # to dissolve() where line shared by 2 rings, ie. ringObj.ringNeigbors
    Wrings = {}
    point2segments = {} # to split ring into ringObj.lines where point shares 3 segs 
    #  after 2nd loop with { point : segments } we make, below ...        
    vertexList = []  # vertex points to create line segs

    #  dissolve()
    #   iterate through composite rings of the new clustered area 
    #   if ring has ring neighbors in the same clustered area
    #       new ring
    #       updateRingSet(ring), recursively through ring.ringNeighbors 
    #   mergeLinesRingSet()

    for position, area in enumerate(AREAS):
        #  make Areas

        areaObj = Area(position)
        areaObjsList.append(areaObj)
        for ring in area:

            #  make Rings

            ringObj = Ring(ring)

            #  print ringObj.isHole

            areaObj.append(ringObj)
            areaObj.ringIds.append(id(ringObj))
            ringObjsDict[id(ringObj)] = ringObj

            for i in range(len(ring) - 1):

                #  makes ring.segments, {point:segments} , {point:areas} , Wrook

                point1 = ring[i] 
                point2 = ring[i + 1]
                lineseg = [point1, point2] 
                sortedlineseg = tuple(sorted(lineseg))
                segObj = Segment()
                segObj.unsorted.extend(lineseg)
                segObj.sorted = sortedlineseg
                ringObj.segments.append(segObj)
                if point2segments.has_key(point1):
                    point2segments[point1].update(sortedlineseg)

                    #  if len(point2segments[point1]) >= 3: 
                    #   print point2segments # RESULTS??
                    #   vertexList.append(point1)

                    point2areas[point1].update([areaObj.positionalId]) 
                else:
                    point2segments[point1] = set([sortedlineseg]) 
                    point2areas[point1] = set([areaObj.positionalId])
                if segment2areas.has_key(sortedlineseg):
                    area1 = segment2areas[sortedlineseg]
                    area2 = areaObj.positionalId

                    #  if 2 diff areas share a segment and the pair isn't in W

                    if area1 != area2 and Wrook[area1].count(area2) == 0:
                        Wrook[area1].append(area2)
                        Wrook[area2].append(area1)
                    ring1 = segment2rings[sortedlineseg]
                    ring2 = id(ringObj)

                    #  if 2 diff rings share a segment and not in each others
                    #  ringObj.ringNeighbors [] attribute

                    if ring1 != ring2 and ringObjsDict[ring1].ringNeighbors.count(ring2) == 0:
                        ringObjsDict[ring1].ringNeighbors.append(ring2)
                        ringObjsDict[ring2].ringNeighbors.append(ring1)
                else:
                    segment2areas[sortedlineseg] = areaObj.positionalId
                    segment2rings[sortedlineseg] = id(ringObj)
                if (i == len(ring) - 1) and point2 != ring[0]:    
                    raise Exception, "PROBLEM: last point of last segment != ring[0]"

    #  Below is an example of how to identify points basedby num of areas sharing it
    #  point3areas = [(v, k) for (k, v) in point2areas.iteritems() if len(v) > 2]
    #  Make Wqueen based on info in point2areas

    ListAreasOfSharedPoints = [list(v) for (k, v) in point2areas.iteritems() if len(v) > 1]
    WqueenSet = Wqueen
    for areas in ListAreasOfSharedPoints:
        for area in areas:
            WqueenSet[area].update(areas)
            WqueenSet[area].remove(area)
    Wqueen = dict([(k, list(v)) for (k, v) in WqueenSet.iteritems()])

    ##  EXTRA STUFF NONESSENTIAL BELOW: COMPARE QUEEN vs. ROOK 

    WqueenList = [(k, set(v)) for (k, v) in Wqueen.iteritems()]
    WrookList = [(k, set(v)) for (k, v) in Wrook.iteritems()]

    #  what areas are not in each others neighborset

    RookVersusQueen = [ WqueenSet[ area[0] ] ^ area[1] for area in WrookList ]
    diffcount = 0
    for i in RookVersusQueen:
        diffcount = diffcount + len(i)
    for R in ringObjsDict.values():
        start = 0
        for i, p in enumerate(R[1:]):

            #  print p

            try:
                vertexList.index(p)
                line = R[start: i + 1]
                R.lines.append(line)
                start = i
            except ValueError:
                pass
    return areaObjsList, ringObjsDict, Wqueen, Wrook, vertexList

def reconnect(clusters, drawmap=False):

    # canvas = makeCanvas(h=500, w=500)

    NEW_AREAS = []
    HOLE_indices = []
    for c, cluster in enumerate(clusters):
        NEW_RINGS = []
        if len(cluster.unlinkedSegments) > 0:

            #  for each newring's unconnected segments...
            #  print "=========="

            for r, RINGSEGS in enumerate(cluster.unlinkedSegments):
                if RINGSEGS == []:
                    pass
                else:

                    #  print "==== above connector() ==== "
                    #  print "CLUSTER", c
                    #  print 'RING of clusterObj.unlinkedSegments', r

                    P = connector(RINGSEGS)
                    if len(P) == 1:  #  Just 1 main ring for this cluster
                        newring = P[0]
                        if isHole(newring) == False:
                            NEW_RINGS.append(newring)
                        else:
                            newring.reverse()
                            NEW_RINGS.append(newring)
                    elif len(P) > 1: #  see which is biggest ring consider rest as holes
                        ringsAreas = [getArea(p) for p in P]
                        idxMainRing = ringsAreas.index(max(ringsAreas))  #  biggest one circumscribes holes
                        biggestRing = P.pop(idxMainRing)
                        if isHole(biggestRing) == False:
                            NEW_RINGS.append(biggestRing)
                        else:
                            biggestRing.reverse()
                            NEW_RINGS.append(biggestRing)

                        #  Smaller Rings

                        for i, ring in enumerate(P):
                            if isHole(ring) == False:
                                NEW_RINGS.append(ring)
                            else:
                                ring.reverse()
                                NEW_RINGS.append(ring)

        #  TO FIX: BORIS HACK BELOW oct 22 in Medellin to force it to work 
        #  problem with connector's starting item not being deleted??? 

        #  remove RINGS WITH VERY SMALL AREAS
        #  tHIS PRESUMER PROBLEMS ASSOCUIATED WITH POINTS OF ORIGINAL SHAPEFILE
        #  Diagram of a special case where this occurs: 
        #  area1 \   area2
        #  *------*-----------------*
        #  *------------------------*
        #  ptA    ptB    area4      ptC
        #  ptA, ptB, ptC are left stranded, should have dissolved
        #  Below catches this problem orginating with
        #  shapefile(ie. should have had a ptB in area4)
        #  FIND ALG FOR: IS poly A within a POLY B ?

        if len(NEW_RINGS) > 1:
            for ri, g in enumerate(NEW_RINGS[1:]):
                gArea = getArea(g)
                if gArea < 9:

                    #  print 'area of this prob ring', gArea
                    #  Review having this code?

                    NEW_RINGS.remove(g)

                #  Xa=g[0][0]
                #  Xb=g[1][0]
                #  Xc=g[2][0]
                #  Ya=g[0][1]
                #  Yb=g[1][1]
                #  Yc=g[2][1]
                #  S = .5 * abs( (Xc - Xa) * (Yb - Ya) - (Xb - Xa) * (Yc - Ya) )

                # if S < 9 :
                #   print 'area of this prob ring', S
                #   NEW_RINGS.remove(g)
                #   print 'length NEW_RINGS', len(NEW_RINGS)

        if len(cluster.holeRings) > 0:
            for holeRing in cluster.holeRings:
                if isHole(holeRing) == True:
                    NEW_RINGS.append(holeRing)
                else:
                    holeRing.reverse()
                    NEW_RINGS.append(holeRing)
                HOLE_indices.append( (c, len(NEW_RINGS) - 1) )
        if len(cluster.independentRings) > 0:
            for Iring in cluster.independentRings:
                if isHole(Iring) == False:
                    NEW_RINGS.append(Iring)
                else:
                    Iring.reverse()
                    NEW_RINGS.append(Iring)
        NEW_AREAS.append(NEW_RINGS)
    if drawmap == True:

     #  drawCanvasRings(canvas,NEW_AREAS)

        drawAreaRings(NEW_AREAS)

    #  HOLE_indices is WRONG INFO I THINK???

    return NEW_AREAS

def invertScale(scale, minxs, minys, shapes):
    canvasShapes = []
    for shape in shapes:
        newshape = []
        for ring in shape:
            newring = []

            #  x = [((x - minxs) * scale) + 5 for x in [p[0] for p in ring]]
            #  y = [500 - ((y - minys) * scale)- 5 for y in [p[1] for p in ring]]

            x=[((x - 5) / scale) + minxs for x in [p[0] for p in ring]]
            y=[(-1 * ( (y - 495) / scale)) + minys for y in [p[1] for p in ring]]
            points = zip(x, y)
            newring.extend(points)
            newshape.append(newring)
        canvasShapes.append(newshape)    
    return canvasShapes    
class Area(list):
    """A list of rings"""

    def __init__(self, filePosition):
        self.positionalId = filePosition
        self.ringIds = []

class Ring(list):
    """A list of points"""

    def __init__(self, ringtuples):
        self.area = "na"
        self.segments = []
        self.lines = []
        self.ringNeighbors = []
        self.extend(ringtuples)
        self.isHole = self.checkIfInnerDonutRing(ringtuples)
        
    def add(self, segment):
        self.extend(segment)
        self.setfirstlastpt()

    def setfirstlastpt(self):
        self.firstpt = self[0]
        self.lastpt = self[-1]

    def checkIfInnerDonutRing(self, ring):
        """# problem due to inverted Tkinker canvas, so i do opposite of
        below:

        Checks to see if points are in counterclockwise order which denotes a
        inner ring of a polygon that has a donut-like shape or a hole such as
        a lake etc.

        Argument:
        
        Ring - a list of tuples denoting x,y coordinates [(x1,y1),...]
        
        Return: 
        TRUE or FALSE
        
        Notes:
        http://www.cartotalk.com/index.php?showtopic=2467
        Charlie Frye 9/26/07 says:
        "Ring order could mean one of two things. First, when a shape has more than one
        part, e.g., a donut hole or an island, it's shape will be comprised of
        multiple parts, or rings. Each ring defines the geometry (list of
        coordinates). The expected implementation is that the rings are listed in size
        order, with the largest ring (covering the most area) being first in the list.
        Another issue is whether the coordinates in each ring are listed in clockwise
        or counterclockwise order; clockwise means it is an exterior ring or an
        island, and counterclockwise is an interior ring or an island [ A HOLE ]."
        """
        x = [p[0] for p in ring]
        y = [p[1] for p in ring]
        n = len(x)

        #  Below checks if inner ring, counterclockwise

        a = sum([x[i] * y[i + 1] - x[i + 1] * y[i] for i in range(n - 1)]) 
        if a > 0:
            counterClockWise = True
            hole = False  #  opoosite of normal for Tkinter canvas coordinates
        else:
            counterClockWise = False  #  opoosite of normal for Tkinter canvas coordinates
            hole = True
        return hole 

class Point(list):
    """A (x,y) tuple"""

    def __init__(self):
        self.areas = []
        self.segments = []

class Segment(tuple):
    """A list of 2 points...((1,2),(3,4))"""

    def __init__(self):
        self.areas = []
        self.rings = []
        self.sorted = "Null"
        self.unsorted = []

class MultiRingCluster(list):
    """A list of areas"""

    def __init__(self):
        self.ringIds = []
        self.independentRings = []
        self.holeRings = []
        self.newHoleRings = []
        self.contiguosRings = []
        self.unlinkedSegments = []
        self.newRings = []

def connector(lines):
    """Warning:

    Only works using clustering based on rook contiguity (or shared line). May not work 
    after a clustering and dissolve started with queen contiguity, because in a ring of 
    say region A there can be many rings of different region(s) that act like holes on 
    the edge of region A.

    Overview:
    Connect lines segments into rings. 

    Arguments:
    [((x1,y1),(x2,y2)),...,((x3,y3),(x4,y4))] a list of tuple-like line segements of 2 points

    Returns:
    [[(x1,y1),(x2,y2),...,(x1,y1)]], a list of lists of closed ArcGIS-like multi-area polygons
    """
    if lines[0] == tuple: lines = [ list(seg) for seg in lines]  #  convert lines of tuples to of lists
    for line in lines:
        if line[0] == line[1] or (line == []):
            lines.remove(line)  #  REMOVE LINE SEG BASED ON DUP POINT

    #  DICTIONARY OF POTENTIAL SEGMENTS TO MATCH WITH ONE ANOTHER

    newRings = []
    point2segs = {}
    for line in lines:
        if point2segs.has_key(line[0]) == False: point2segs[line[0]] = [line[1]]
        else: point2segs[line[0]].append(line[1])
        if point2segs.has_key(line[1]) == False: point2segs[line[1]] = [line[0]]
        else: point2segs[line[1]].append(line[0])

    #  Clean bad lines segments that are not truly part of a loop, like stranded hairs
    #  Example of a bad line segment:

    CLEAN = False
    while CLEAN == False:
        N = len(point2segs.items())
        cleancount = 0
        for item in point2segs.items():
            if len(item[1]) == 1:  #  problem: key point connects to just one other point
                keypt = item[0]
                pt = item[1]
                point2segs.pop(keypt)  #  step 1 remove the key point from dict
                point2segs[pt].remove(keypt)  #  step 2 remove other point from dict
                if point2segs[pt] == []:
                    point2segs.pop(pt)  #  remove empty [] value
            else:
                cleancount = cleancount + 1
                if cleancount == N: 
                    CLEAN = True  #  all segs in DICT are OK!!!

    # separate figure-8 and nonfigure-8 segments

    nonFig8items = []
    Fig8items = []
    for idx, item in enumerate(point2segs.items()):
        if len(item[1]) == 2: 
            nonFig8items.append(item)
        elif len(item[1]) == 4: 
            Fig8items.append(item)
        else:
            print " Problem points :"
            print "len(item): ", len(item)
    FIG8START = copy.deepcopy(Fig8items)
    if len(Fig8items) > 0:  #  start with fig8 ring's middle point, if fig8 exists
        startitem = Fig8items.pop()
        startkeypt = startitem[0]
    else:
        startkeypt=point2segs.items()[0][0]
    pt = point2segs[startkeypt].pop()  #  from 4 (or 2) pts to 3 (or 1) pt(s) in list
    partRing = [startkeypt, pt]
    point2segs[pt].remove(startkeypt)  #  step 2 remove seg from dict
    if point2segs[pt] == []: 
        point2segs.pop(pt)
    DONE = False
    while DONE == False:
        possibleEndRing = point2segs[partRing[-1]]  #  look4match
        if len(possibleEndRing) > 1:  #  figure-8 originally started with 4 pts 
            KEYPT = copy.deepcopy(partRing[-1])
            newpt = possibleEndRing.pop(-1)  #  remove last pt 
            partRing.append(newpt)  #  connect pt to new chain
            point2segs[KEYPT]=possibleEndRing  #  put revised list of fig8 pts back into dict
        else:
            newEndpt = point2segs.pop(partRing[-1])[0]  #  look4match for new end pt
            point2segs[newEndpt].remove(partRing[-1])  #  ERROR HERE?step 2 remove seg from dict
            if point2segs[newEndpt] == []: 
                point2segs.pop(newEndpt)
            partRing.append(newEndpt)  #  connect pt to new chain
        if partRing[0] == partRing[-1] and len(point2segs.keys()) != 0: 
            newRings.append(partRing)
            if len(Fig8items) > 0:  #  start with fig8 ring's middle point, if fig8 exists
                startitem = Fig8items.pop()
                startkeypt = startitem[0]
                FIG8 = True
            else:
                startkeypt=point2segs.items()[0][0]
                FIG8 = False
            pt = point2segs[startkeypt].pop()  #  from 4 (or 2) pts to 3 (or 1) pt(s) in list
            partRing = [ startkeypt, pt]
            point2segs[pt].remove(startkeypt)  #  step 2 remove seg from dict
        elif partRing[0] == partRing[-1] and len(point2segs.keys()) == 0:
            newRings.append(partRing)
            DONE = True

    #f  for ring in newRings:
    #       canvas.create_polygon(ring,fill=colorlist[c])
    #   2nd stage nesting: make sure connetor can do figure-8 
    #  1st stage nesting: polyInsidePoly()==True make sure its a ringHole 

    return newRings

def isHole(ring):
    """# problem due to inverted Tkinker canvas, so i do opposite of
    below:

    Checks to see if points are in counterclockwise order which denotes a
    inner ring of a polygon that has a donut-like shape or a hole such as
    a lake etc.

    Argument:
    ring - a list of tuples denoting x,y coordinates [(x1,y1),...]
    
    Return: 
    TRUE or FALSE
    
    Notes:
    http://www.cartotalk.com/index.php?showtopic=2467
    Charlie Frye 9/26/07 says:
    "Ring order could mean one of two things. First, when a shape has more than one
    part, e.g., a donut hole or an island, it's shape will be comprised of
    multiple parts, or rings. Each ring defines the geometry (list of
    coordinates). The expected implementation is that the rings are listed in size
    order, with the largest ring (covering the most area) being first in the list.
    Another issue is whether the coordinates in each ring are listed in clockwise
    or counterclockwise order; clockwise means it is an exterior ring or an
    island, and counterclockwise is an interior ring or an island [ A HOLE ]."
    """
    x = [p[0] for p in ring]
    y = [p[1] for p in ring]
    n = len(x)

    #  Below checks if inner ring, counterclockwise

    a = sum([x[i] * y[i + 1] - x[i + 1] * y[i] for i in range(n - 1)]) 
    if a > 0:
        counterClockWise = True
        hole = False  #  opposite of normal for Tkinter canvas coordinates
    else:
        counterClockWise = False  #  opposite of normal for Tkinter canvas coordinates
        hole = True
    return hole 

def getArea(ring):
    a = [] 
    for i in range(len(ring) - 1):
        a.append(ring[i][0] * ring[i + 1][1] - ring[i + 1][0] * ring[i][1])
    return abs(sum(a)) / 2.0
