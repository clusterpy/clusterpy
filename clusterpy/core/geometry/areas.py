"""Geometric area calculation Module
"""
__author__ = "Juan C. Duque, Alejandro Betancourt"
__credits__ = "Copyright (c) 2009-10 Juan C. Duque"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"
__all__ = ['getGeometricAreas']

def getGeometricAreas(layer):
    """
    This function calculates the geometric area for the polygons of
    a map and returns it as a dictionary.

    For computational efficiency it's recommended to store the results
    on the layer database using the addVariable layer function.
    
    :param layer: layer with the areas to be calculated
    :type layer: Layer 
    
    Users must call this function through a layer object as can be seen
    in the example below. 
 
    **Example**

    >>> import clusterpy
    >>> china = clusterpy.importArcData("clusterpy/data_examples/china")
    >>> china.getGeometricAreas()
    """
    print "Processing geometric areas"
    area = 0
    polygons = layer.areas
    lenAreas = {}
    for a, area in enumerate(polygons):
        areaAcum = 0
        for r, ring in enumerate(area):
            ringAcum = 0
            for p, point in enumerate(ring):
                p1 = point
                if p == len(ring) - 1:
                    p2 = ring[0]
                else:
                    p2 = ring[p + 1]
                ringAcum += p1[0] * p2[1] - p1[1] * p2[0]
            areaAcum += ringAcum
        lenAreas[a] = abs(float(areaAcum) / 2)
    print "Done"
    return lenAreas
    
