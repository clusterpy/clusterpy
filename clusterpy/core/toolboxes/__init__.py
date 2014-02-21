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
from cluster import * 
from sstats import *

folders = os.listdir(os.path.split(__file__)[0])
if "rimaps" in folders:
    try:
        from rimaps import *
        rimapsActive = True
    except Exception as e:
        print "Some functions are not available, reason:", e

