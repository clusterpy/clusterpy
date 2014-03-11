"""
Testing Spatial Statistics algorithms in Clusterpy
This file contains tests for the indexes.
"""

from unittest import TestCase, skip
import clusterpy

class TestStatsIndex(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_areaChangeIndex_function(self):
        """
        """
        output = None
        clusterpy.toolboxes.sstats.areaChangeIndex(None, None, None)
        self.assertTrue(output)

    def test_translationLocalIndex_function(self):
        """
        """
        output = None
        clusterpy.toolboxes.sstats.translationLocalIndex(None, None, None)
        self.assertTrue(output)

    def test_translationGlobalIndex_function(self):
        """
        """
        output = None
        clusterpy.toolboxes.sstats.translationGlobalIndex(None, None, None)
        self.assertTrue(output)
