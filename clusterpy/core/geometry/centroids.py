"""Centroids calculation module
"""
__author__ = "Juan C. Duque, Alejandro Betancourt"
__credits__= "Copyright (c) 2009-10 Juan C. Duque"
__license__ = "New BSD License"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"
__all__ = ['getCentroids']


def getCentroids(layer):
    """
    This function calculates the centroids for the polygons of
    a map and returns it as a dictionary with the
    coordinates of each area's centroid.

    For computational efficiency it's recommended to store the results
    on the layer database using the addVariable layer function.
    
    :param layer: layer with the areas to be calculated
    :type layer: Layer Object 
    
    Users must call this function through a layer object as in the 
    following example.

    **Example**

    >>> import clusterpy
    >>> china = clusterpy.importArcData("clusterpy/data_examples/china")
    >>> china.getCentroids()
    """
    area = 0
    polygons = layer.areas
    geometricAreas = layer.getGeometricAreas()
    centroids = {}
    for a, area in enumerate(polygons):
        areaAcum = 0
        areaXAcum = 0
        areaYAcum = 0
        for r, ring in enumerate(area):
            ringAcum = 0
            ringXAcum = 0
            ringYAcum = 0
            for p, point in enumerate(ring):
                p1 = point
                if p == len(ring) - 1:
                    p2 = ring[0]
                else:
                    p2 = ring[p + 1]
                ringAcum += p1[0] * p2[1] - p1[1] * p2[0]
                ringXAcum += (p1[0] + p2[0]) * (p1[0] * p2[1] - p2[0] * p1[1])
                ringYAcum += (p1[1] + p2[1]) * (p1[0] * p2[1] - p2[0] * p1[1])
            areaAcum += ringAcum / float(2)
            ringPercent = abs(areaAcum) / float(geometricAreas[a])
            areaXAcum += ringPercent * ringXAcum / float(6 * areaAcum)
            areaYAcum += ringPercent * ringYAcum / float(6 * areaAcum)
        centroids[a] = [areaXAcum, areaYAcum]
    return centroids
    
