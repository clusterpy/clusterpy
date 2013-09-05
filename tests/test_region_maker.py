"""
Testing clustering algorithms in Clusterpy -Helper functions-
Tests for one of the core classes in clusterpy. Region Maker.
"""

from unittest import TestCase, skip
from math import pi
from clusterpy.core.toolboxes.cluster.componentsAlg import AreaManager
from clusterpy.core.toolboxes.cluster.componentsAlg import RegionMaker

class TestRegionMaker(TestCase):
    def setUp(self):

        self.Y = {i:[pi*i] for i in xrange(8)}

        """
        Simple map of 6 Areas.

        0123
        4567
        """        
        self.Wrook = {0:[1, 4],
                      1:[0, 2, 5],
                      2:[1, 3, 6],
                      3:[2, 7],
                      4:[0, 5],
                      5:[1, 4, 6],
                      6:[2, 5, 7],
                      7:[3, 6]}

        self.Wqueen = {0:[1, 4, 5],
                       1:[0, 2, 4, 5, 6],
                       2:[1, 3, 5, 6, 7],
                       3:[2, 6, 7],
                       4:[0, 1, 5],
                       5:[0, 1, 2, 4, 6],
                       6:[1, 2, 3, 5, 7],
                       7:[2, 3, 6]}

    def tearDown(self):
        pass

    @skip
    def test_grow_contiguos_regions_in_region_maker_init(self):
        am = AreaManager(self.Wqueen, self.Y)
        rm = RegionMaker(am)

        self.assertIsNotNone(rm)
