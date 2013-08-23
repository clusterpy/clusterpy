"""
Testing clustering algorithms in Clusterpy
** All the following tests take considerable time to complete **
"""

from unittest import TestCase
import clusterpy

map_type = 'n529'
sample_input_path = "./sample_input_data/" + map_type
sample_output_path = "./sample_output/" + map_type

class TestClusteringAlgorithms(TestCase):
    def setUp(self):
        self.map_instance = clusterpy.importArcData(sample_input_path)

    def tearDown(self):
        # Remove generated output/Arc data
        pass

    def test_arisel(self):
        output_file = sample_output_path + 'arisel'
        into_regions = 53
        self.map_instance.cluster('arisel',
                                  ['SAR1'],
                                  into_regions,
                                  dissolve = 1,
                                  inits = 20)
        assert False
