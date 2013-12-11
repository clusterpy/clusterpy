# encoding: latin2
"""Toolboxes module
"""
__author__ = "Juan C. Duque, Alejandro Betancourt"
__credits__= "Copyright (c) 2009-10 Juan C. Duque"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"

rimapsActive = False
import os
import sys
import cluster as clus
import sstats as ssts
from cluster import * 
from sstats import *

folders = os.listdir(os.path.split(__file__)[0])
if "rimaps" in folders:
    try:
        import Polygon
        import scipy
    except:
        pass
    else:
        from rimaps import *
        rimapsActive = True

__all__ = clus.__all__ + ssts.__all__ 
