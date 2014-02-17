"""
Testing clustering algorithms in Clusterpy -Helper functions-
Tests for one of the core classes in clusterpy. Region Maker.
"""

from unittest import TestCase, skip
from clusterpy import importArcData
from clusterpy.core.toolboxes.cluster.componentsAlg import AreaManager
from clusterpy.core.toolboxes.cluster.componentsAlg import RegionMaker

map_type = 'n100'
max_num_regions = 10
sample_input_path = "clusterpy/data_examples/" + map_type

class TestMulticore(TestCase):
    def setUp(self):
        map_instance = importArcData(sample_input_path)

        self.Y = map_instance.Y
        self.Wrook = map_instance.Wrook
        self.Wqueen = map_instance.Wqueen

    def tearDown(self):
        pass

    def test_randomness_on_same_process(self):
        """This tests that running multiple instances of the region maker
        on the same script (process) will """
        am = AreaManager(self.Wrook, self.Y)
        regions = []
        for _reg in xrange(1, max_num_regions):
            rm = RegionMaker(am, pRegions=max_num_regions)
            self.assertEqual(max_num_regions, len(rm.region2Area))
            self.assertTrue(am.checkFeasibility(rm.returnRegions()))
            regions.append(rm.returnRegions())

        for regioni in xrange(len(regions) - 1):
            for regionj in xrange(regioni + 1, len(regions)):
                self.assertNotEqual(regions[regioni], regions[regionj])

    @skip
    def test_randomness_on_multiple_processes(self):
        pass
