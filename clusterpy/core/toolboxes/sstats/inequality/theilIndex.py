# encoding: latin2
"""Theil index
"""
__author__ = "Juan C. Duque, Alejandro Betancourt"
__credits__ = "Copyright (c) 2009-11 Juan C. Duque"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"

__all__ = ['theil']
import math

def theil(var, area2region):
    """Theil index (global, between and within groups)

    This function calculates global inequality, inequality between groups and
    inequality within groups. For more information on the Theil index see
    [Theil1967] and [Theil1972] and for its application in space-time analysis see
    [Rey2004] or [Rey_Sastre2010] (eq.8)::

        Layer.inequality('theil', var, clusters)

    :keyword var: Area attribute (e.g. 'SAR1') 
    :type var: string
    :keyword clusters: variables in Layer containing regionalization schemes e.g.: 'BELS'
    :type clusters: string 


    **Example 1** ::

        import clusterpy
        instance = clusterpy.createGrid(10, 10)
        instance.generateData("SAR", 'rook', 1, 0.9)
        instance.cluster('arisel', ['SAR1'], 15)
        instance.inequality('theil', 'SAR1', 'arisel_20121027222718')

    """
    n = len(var)
    region2area = {}
    regionsY = {}
    for area,region in enumerate(area2region):
        if region2area.has_key(region):
            region2area[region].append(area)
            regionsY[region] += var[area][0]
        else:
            region2area[region] = [area]
            regionsY[region] = var[area][0]
    totalY = sum([x[0] for x in var.values()])
    t_b = 0
    t_w = 0
    for region in regionsY:
        s_g = regionsY[region]/float(totalY)
        n_g = len(region2area[region])
        t_b += s_g*math.log(n/float(n_g)*s_g)
        aux_t_bg = 0
        for area in region2area[region]:
            s_ig = var[area][0]/float(regionsY[region])
            aux_t_bg += s_ig*math.log(n_g*s_ig)
        t_w += s_g*aux_t_bg
    t = t_b + t_w     
    return t,t_b,t_w
