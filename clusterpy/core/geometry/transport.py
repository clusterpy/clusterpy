# encoding: latin2
"""Transport Layer geometry
"""
__author__ = "Juan C. Duque, Alejandro Betancourt"
__credits__ = "Copyright (c) 2009-10 Juan C. Duque"
__license__ = "New BSD License"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"
__all__ = ['transportLayer']

# transportLayer
def transportLayer(layer, xoffset, yoffset):
    """
    This function transports all the coordinates of a layer object given the input offsets.

    :param xoffset: length of the translation to be made on the x coordinates
    :type xoffset: float
    :param yoffset: length of the translation to be made on the y coordinates
    :type yoffset: float

    **Example**

    >>> import clusterpy
    >>> clusterpy.importArcData("../data_examples/china")
    >>> china.transport(100, 100)
    """
    for a, ar in enumerate(layer.areas):
        for r, ri in enumerate(ar):
            for p, po in enumerate(ri):
                layer.areas[a][r][p] = (layer.areas[a][r][p][0] + xoffset,layer.areas[a][r][p][1] + yoffset)
    layer.bbox = [layer.bbox[0] + xoffset,
            layer.bbox[1] + yoffset,
            layer.bbox[2] + xoffset,
            layer.bbox[3] + yoffset]
