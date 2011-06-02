# encoding: latin2
"""Transport Layer geometry
"""
__author__ = "Juan C. Duque, Alejandro Betancourt"
__credits__ = "Copyright (c) 2009-10 Juan C. Duque"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"
__all__ = ['getBbox']

#  transportLayer

def getBbox(layer):
    """
    Finds the layer's bounding box
    
    :param layer: object layer
    :type layer: Layer

    This is how you can ask for a bounding box of a layer
    >>> layer.bbox

    **Example**

    >>> import clusterpy
    >>> clusterpy.importArcData("../data_examples/china")
    >>> china.bbox
    """
    xmin = xmax = layer.areas[0][0][0][0]
    ymin = ymax = layer.areas[0][0][0][1]
    for area in layer.areas:
        for ring in area:
            for point in ring:
                if point[0] < xmin:
                    xmin = point[0]
                if point[0] > xmax:
                    xmax = point[0]
                if point[1] < ymin:
                    ymin = point[1]
                if point[1] > ymax:
                    ymax = point[1]
    return xmin, ymin, xmax, ymax
