"""
Testing clustering algorithms in Clusterpy -Helper functions-
** Some of the following tests take considerable time to complete **
"""

from unittest import TestCase
from clusterpy import importArcData
from clusterpy.core.toolboxes.cluster.componentsAlg import AreaManager
from clusterpy.core.toolboxes.cluster.componentsAlg import RegionMaker
import numpy

map_type = 'n100' # When changing this input map, solution sizes must change too
into_regions = 10 # When changing this input map, solution sizes must change too

sample_input_path = "clusterpy/data_examples/" + map_type
sample_output_path = "tests/sample_output/" + map_type

class TestContiguosRegionsMove(TestCase):
    def setUp(self):
        self.layer = importArcData(sample_input_path)

        """ Simple 10x10 Grid with valid Region WRook configuration:
        '**********' area 0-9
        '**********' area 1-19
        '**********' area 20-29
        '*******ooo' area 30-39
        '*********o' area 40-49
        'oooooooooo' area 50-59
        'oooooooooo' area 60-69
        'oooooooooo' area 70-79
        'oooooooooo' area 80-89
        'oooooooooo' area 90-99
        """
        self.possible_rook_solution = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                                  1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                                  1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                                  1, 1, 1, 1, 1, 1, 1, 0, 0, 0,
                                  1, 1, 1, 1, 1, 1, 1, 1, 1, 0,
                                  0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                  0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                  0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                  0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                  0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        """ Simple 10x10 Grid with valid Region WQueen configuration:
        '**********' area 0-9
        '**********' area 1-19
        '**********' area 20-29
        '*******ooo' area 30-39
        '********oo' area 40-49
        'oooooooo*o' area 50-59
        'oooooooooo' area 60-69
        'oooooooooo' area 70-79
        'oooooooooo' area 80-89
        'oooooooooo' area 90-99
        """
        self.possible_queen_solution = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                                        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                                        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                                        1, 1, 1, 1, 1, 1, 1, 0, 0, 0,
                                        1, 1, 1, 1, 1, 1, 1, 1, 0, 0,
                                        0, 0, 0, 0, 0, 0, 0, 0, 1, 0,
                                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


    def tearDown(self):
        pass

    def test_true_possible_rook_region_movement(self):
        """
        A possible region change is in fact a feasible movement using rook contiguity.
        """
        am = AreaManager(self.layer.Wrook, self.layer.Y)
        rm = RegionMaker(am, initialSolution = self.possible_rook_solution)

        """ Removing area 29 from region 1 is an allowed movement"""
        feasible = rm.checkFeasibility(1, 29, rm.region2Area)

        assert feasible

    def test_false_possible_rook_region_movement(self):
        """
        Removing an area that breaks the contiguity constraint.
        """
        am = AreaManager(self.layer.Wrook, self.layer.Y)
        rm = RegionMaker(am, initialSolution = self.possible_rook_solution)

        """ Removing area 47 from region 1 leaves area 48 as an island"""
        feasible = rm.checkFeasibility(1, 47, rm.region2Area)

        assert not feasible

    def test_true_possible_queen_region_movement(self):
        """
        A region removal yields in fact a feasible solution using queen contiguity.
        """
        am = AreaManager(self.layer.Wqueen, self.layer.Y)
        rm = RegionMaker(am, initialSolution = self.possible_queen_solution)

        """ Removing area 49 from region 0 leaves areas attached by a point"""
        feasible = rm.checkFeasibility(0, 49, rm.region2Area)

        assert feasible

    def test_false_possible_queen_region_movement(self):
        """
        An infeasible region removal yields an uncontiguos region. Using WQueen.
        """
        am = AreaManager(self.layer.Wqueen, self.layer.Y)
        rm = RegionMaker(am, initialSolution = self.possible_queen_solution)

        """ Removing area 47 from region 1 leaves area 58 as an island"""
        feasible = rm.checkFeasibility(1, 47, rm.region2Area)

        assert not feasible
