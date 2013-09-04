"""
Testing clustering algorithms in Clusterpy -Helper functions-
Tests for one of the core classes in clusterpy.
"""

from unittest import TestCase
from math import pi
from clusterpy.core.toolboxes.cluster.componentsAlg import AreaManager

class TestAreaManager(TestCase):
    def setUp(self):

        self.Y = {0:[pi], 1:[pi], 2:[pi],
                  3:[pi], 4:[pi], 5:[pi],
                  6:[pi], 7:[pi]}

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

    def test_possible_solution_configuration_on_queen(self):
        """
        Using the Wqueen, test for a possible region assignment
        """
        """
        Possible solution:
        0011
        0101
        """
        possible_solution = [0, 0, 1, 1, 0, 1, 0, 1]
        am = AreaManager(self.Wqueen, self.Y)
        result = am.checkFeasibility(possible_solution)
        self.assertTrue(result)

    def test_impossible_solution_configuration_on_queen(self):
        """
        Using the Wqueen, test for an impossible region assignment
        """
        """
        Impossible solution:
        0110
        1010
        """
        possible_solution = [0, 1, 1, 0, 1, 0, 1, 0]
        am = AreaManager(self.Wqueen, self.Y)
        result = am.checkFeasibility(possible_solution)
        self.assertFalse(result)

    def test_possible_solution_configuration_on_rook(self):
        """
        Using the Wrook, test for a possible region assignment
        """
        """
        Possible solution:
        0112
        0002
        """
        possible_solution = [0, 1, 1, 2, 0, 0, 0, 2]
        am = AreaManager(self.Wrook, self.Y)
        result = am.checkFeasibility(possible_solution)
        self.assertTrue(result)

    def test_impossible_solution_configuration_on_rook(self):
        """
        Using the Wrook, test for a impossible region assignment.
        """
        """
        Possible solution:
        0011
        0101
        """
        possible_solution = [0, 0, 1, 1, 0, 1, 0, 1]
        am = AreaManager(self.Wrook, self.Y)
        result = am.checkFeasibility(possible_solution)
        self.assertFalse(result)

    def test_possible_solution_configuration_on_rook_w_empty_region(self):
        """
        Using the Wrook, test for a impossible region assignment where one
        area is missing.
        """
        """
        Possible solution:
        0022
        0202
        """
        possible_solution = [0, 0, 2, 2, 0, 2, 0, 2]
        am = AreaManager(self.Wrook, self.Y)
        result = am.checkFeasibility(possible_solution)
        self.assertFalse(result)

    def test_possible_solution_configuration_on_rook_w_one_region(self):
        """
        Using the Wrook, test for a possible region assignment where only
        one region exists.
        """
        """
        Possible solution:
        0000
        0000
        """
        possible_solution = [0, 0, 0, 0, 0, 0, 0, 0]
        am = AreaManager(self.Wrook, self.Y)
        result = am.checkFeasibility(possible_solution)
        self.assertTrue(result)
