"""
Testing clustering algorithms in Clusterpy -Helper functions-
Tests for one of the core classes in clusterpy. Region Maker.
"""

from unittest import TestCase, skip
from math import pi
from clusterpy import importArcData
from clusterpy.core.toolboxes.cluster.componentsAlg import AreaManager
from clusterpy.core.toolboxes.cluster.componentsAlg import RegionMaker

map_type = 'n100'
max_num_regions = 10
sample_input_path = "clusterpy/data_examples/" + map_type

class TestRegionMaker(TestCase):
    def setUp(self):
        map_instance = importArcData(sample_input_path)

        self.Y = map_instance.Y
        self.Wrook = map_instance.Wrook
        self.Wqueen = map_instance.Wqueen

    def tearDown(self):
        pass

    @skip
    def test_construct_regions_method(self):
        self.assertTrue(False)

    def test_grow_exogenous_regions_rook(self):
        """Number of regions is exogenous, aka given (Wrook)"""
        am = AreaManager(self.Wrook, self.Y)

        for regions in xrange(1, max_num_regions):
            rm = RegionMaker(am, pRegions=regions)
            self.assertEqual(regions, len(rm.region2Area))
            self.assertTrue(am.checkFeasibility(rm.returnRegions()))

    def test_grow_exogenous_regions_queen(self):
        """Number of regions is exogenous, aka given (Wqueen)"""
        am = AreaManager(self.Wqueen, self.Y)

        for regions in xrange(1, max_num_regions):
            rm = RegionMaker(am, pRegions=regions)
            self.assertEqual(regions, len(rm.region2Area))
            self.assertTrue(am.checkFeasibility(rm.returnRegions()))

    @skip
    def test_grow_exogenous_regions_with_initial_solution(self):
        """Number of regions is exogenous, aka given, and an initial solution"""
        am = AreaManager(self.Wqueen, self.Y)
        rm = RegionMaker(am)

        self.assertIsNotNone(rm)

    @skip
    def test_grow_endogenous_threshold_regions(self):
        """Number of regions is endogenous with a threshold value"""
        am = AreaManager(self.Wqueen, self.Y)
        rm = RegionMaker(am)

        self.assertIsNotNone(rm)

    @skip
    def test_grow_endogenous_range_regions(self):
        """Number of regions is endogenous with a range value"""
        am = AreaManager(self.Wqueen, self.Y)
        rm = RegionMaker(am)

        self.assertIsNotNone(rm)
