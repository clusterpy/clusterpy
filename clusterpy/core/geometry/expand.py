# encoding: latin2
"""Expand Layer geometry
"""
__author__ = "Juan C. Duque, Alejandro Betancourt"
__credits__ = "Copyright (c) 2009-10 Juan C. Duque"
__license__ = "New BSD License"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"
__all__ = ['expandLayer']

# expandLayer
def expandLayer(layer, xproportion, yproportion):
    """
    This function scales layer width and height according to input 
    proportions  

    :param xproportion: Proportion to scale x
    :type xproportion: float
    :param yproportion: Proportion to scale y
    :type yproportion: float

    **Example**

    >>> import clusterpy
    >>> clusterpy.importArcData("../data_examples/china")
    >>> china.expand(100, 100)
    """
    for a, ar in enumerate(layer.areas):
        for r, ri in enumerate(ar):
            for p, po in enumerate(ri):
                x = layer.areas[a][r][p][0] 
                y = layer.areas[a][r][p][1] 
                layer.areas[a][r][p] = \
                (xproportion * (x - layer.bbox[0]) + layer.bbox[0],
                yproportion * (y - layer.bbox[1]) + layer.bbox[1])
    layer.bbox = [layer.bbox[0],
            layer.bbox[1],
            xproportion * (layer.bbox[2] - layer.bbox[0]) + layer.bbox[0],
            yproportion * (layer.bbox[3] - layer.bbox[1]) + layer.bbox[1]]
