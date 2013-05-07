# encoding: latin2
""" Module to fix set of areas with problems in T intersections 
"""
__author__ = "Juan C. Duque, Alejandro Betancourt"
__credits__ = "Copyright (c) 2010-11 Juan C. Duque"
__license__ = "New BSD License"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"
__all__ = [fixIntersections]

# fixIntersections

def fixIntersections(AREAS):
    """fix set of areas with problems in T intersections

    :param AREAS: set of areas 
    :type AREAS: List
    :rtype: List
    :return: set of areas with intersections fixed 
    """
    areas = AREAS
    ring2areas = {}
    segment2areas = {}
    point2areas = {}
    point2segment = {}
    Wqueen = {}
    Wrook = {}
    for idx in range(len(AREAS)):
        Wqueen[idx] = []
        Wrook[idx] = []
    for a, area in enumerate(areas):
        for r, ring in enumerate(area):
            for p, point in enumerate(ring[0: -1]):
                p1 = point
                p2 = ring[p + 1]
                segment = [p1, p2]
                segment.sort(key=lambda x: x[0]**2 + x[1]**2)
                #if a == 30:
                #    import pdb
                #    pdb.set_trace()
                sortSegment = tuple(segment)
                if segment2areas.has_key(sortSegment):
                    segment2areas[sortSegment] += [a]
                else:
                    segment2areas[sortSegment] = [a]
                if point2areas.has_key(p1):
                    point2areas[p1] += [a]
                else:
                    point2areas[p1] = [a]

    points = point2areas.keys()
    segments = segment2areas.keys()
    segments = filter(lambda x: len(segment2areas[x]) == 1,segments)
    for seg in segments:
        if seg[1][0] - seg[0][0] != 0:
            m = (seg[1][1] - seg[0][1])/float(seg[1][0] - seg[0][0])
        else:
            m = 0
        f = lambda x: m*x - m*seg[0][0] + seg[0][1]
        possiblePoints = filter(lambda p: min(seg[0][0],seg[1][0])<p[0]<max(seg[0][0],seg[1][0]) and min(seg[0][1],seg[1][1])< p[1] < max(seg[0][1],seg[1][1]) and f(p[0]) - 10e-3 <= p[1] <= f(p[0]) + 10e-3,points)
        if len(possiblePoints) > 0:
            areaId = segment2areas[seg][0]
            area = AREAS[areaId]
            ringId = 0
            end = False
            while not end:
                if seg[0] in area[ringId]:
                    end = True
                else:
                    ringId += 1
            p1 = area[ringId].index(seg[0])
            p2 = area[ringId].index(seg[1])
            if p1 == 0 and p2 != 1:
                p1 = p2 + 1
            
            if p2 == 0 and p1 != 1:
                p2 = p1 + 1

            if p1 < p2:
                possiblePoints.sort(key=lambda x: ((x[0]-seg[0][0])**2 + (x[1]-seg[0][1])**2)**0.5)
            else:
                possiblePoints.sort(key=lambda x: ((x[0]-seg[1][0])**2 + (x[1]-seg[1][1])**2)**0.5)
            for point in possiblePoints:
                if p1 < p2:
                    area[ringId].insert(p2,point)
                else:
                    area[ringId].insert(p1,point)

            AREAS[areaId] = area
    return AREAS

