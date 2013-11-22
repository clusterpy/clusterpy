"""
Testing clustering algorithms in Clusterpy
** All the following tests take considerable time to complete **
"""

from unittest import TestCase, skip
from nose.plugins.attrib import attr
import clusterpy
from numpy.random import seed as make_static_random
from clusterpy.core.toolboxes.cluster.componentsAlg import AreaManager
from clusterpy.core.toolboxes.cluster.componentsAlg import RegionMaker

map_type = 'n100'
into_regions = 10

_seed = 10

sample_input_path = "clusterpy/data_examples/" + map_type
sample_output_path = "tests/sample_output/" + map_type

def _final_regions_are_contiguous_in_instance(instance):
    exp_name = instance.fieldNames[-1]
    clustering_results = instance.outputCluster[exp_name]
    final_region_assignment = clustering_results['r2a']
    am = AreaManager(instance.Wrook, instance.Y)
    return am.checkFeasibility(final_region_assignment)

def _final_objfunction_from_instance(instance):
    exp_name = instance.fieldNames[-1]
    clustering_results = instance.outputCluster[exp_name]
    return clustering_results['objectiveFunction']

class TestArisel(TestCase):
    def setUp(self):
        self.map_instance = clusterpy.importArcData(sample_input_path)

    def tearDown(self):
        pass

    @attr('slow')
    def test_arisel_never_breaks_contiguity(self):
        """
        Tests that the output regions never break the contiguity constraint.
        """
        instance = self.map_instance

        instance.cluster('arisel', ['SAR1'],
                                  into_regions, dissolve = 1,
                                  inits = 20)

        feasible = _final_regions_are_contiguous_in_instance(instance)

        self.assertTrue(feasible)

    @attr('slow')
    def test_arisel_gives_at_least_same_obj_func(self):
        """
        Tests that the objective function is at least the same, but not worse.
        """
        instance = self.map_instance

        make_static_random(_seed)
        initial_obj_func = float(90.1868744781) # Using a seed of _seed

        instance.cluster('arisel', ['SAR1'],
                                  into_regions, dissolve = 1,
                                  inits = 20)

        final_obj_func = _final_objfunction_from_instance(instance)

        self.assertTrue(initial_obj_func >= final_obj_func)

class TestMaxPTabu(TestCase):
    def setUp(self):
        self.map_instance = clusterpy.importArcData(sample_input_path)

    def tearDown(self):
        pass

    @attr('slow')
    def test_maxpt_never_breaks_contiguity(self):
        instance = self.map_instance

        instance.cluster('maxpTabu',
                         ['SAR1', 'Uniform2'],
                         threshold = 130,
                         dissolve = 1)

        feasible = _final_regions_are_contiguous_in_instance(instance)

        self.assertTrue(feasible)

    @attr('slow')
    def test_maxpt_gives_at_least_same_obj_func(self):
        instance = self.map_instance

        make_static_random(_seed)
        initial_obj_func = float(140) # Using a seed of _seed

        instance.cluster('maxpTabu',
                         ['SAR1', 'Uniform2'],
                         threshold = 130,
                         dissolve = 1)

        final_obj_func = _final_objfunction_from_instance(instance)

        self.assertTrue(initial_obj_func >= final_obj_func)

class TestAZPalgorithms(TestCase):
    """ Tests for AZP, AZPrTabu, AZPSA """
    def setUp(self):
        self.map_instance = clusterpy.importArcData(sample_input_path)

    def tearDown(self):
        pass

    @attr('slow')
    def test_azp_never_breaks_contiguity(self):
        instance = self.map_instance

        instance.cluster('azp',
                         ['SAR1'],
                         into_regions,
                         dissolve=1)

        feasible = _final_regions_are_contiguous_in_instance(instance)

        self.assertTrue(feasible)

    @attr('slow')
    def test_azp_gives_at_least_same_obj_func(self):
        instance = self.map_instance
        aream = AreaManager(instance.Wrook, instance.Y)
        rm = RegionMaker(aream, into_regions)

        ob_before = rm.objInfo
        rm.AZPImproving()
        ob_after = rm.objInfo

        self.assertTrue(ob_before >= ob_after)

    @attr('slow', 'azpsa')
    def test_azpsa_never_breaks_contiguity(self):
        instance = self.map_instance

        instance.cluster('azpSa',
                         ['SAR1'],
                         into_regions,
                         dissolve=1)

        feasible = _final_regions_are_contiguous_in_instance(instance)

        self.assertTrue(feasible)

    @attr('slow', 'azpsa')
    def test_azpsa_gives_at_least_same_obj_func(self):
        instance = self.map_instance

        aream = AreaManager(instance.Wrook, instance.Y)
        rm = RegionMaker(aream, into_regions)

        alpha = 0.85
        maxiterations = 3

        ob_before = rm.objInfo
        rm.AZPSA(alpha, maxiterations)
        ob_after = rm.objInfo
        self.assertTrue(ob_before >= ob_after)

    @attr('slow')
    def test_azptabu_never_breaks_contiguity(self):
        instance = self.map_instance

        instance.cluster('azpTabu',
                         ['SAR1'],
                         into_regions,
                         dissolve=1)

        feasible = _final_regions_are_contiguous_in_instance(instance)

        self.assertTrue(feasible)

    @attr('slow')
    def test_azptabu_gives_at_least_same_obj_func(self):
        instance = self.map_instance
        aream = AreaManager(instance.Wrook, instance.Y)
        rm = RegionMaker(aream, into_regions)

        convTabu = max(10, len(instance.Y) / into_regions)
        tabuLength = 10

        ob_before = rm.objInfo
        rm.AZPTabuMove(tabuLength=tabuLength, convTabu=convTabu)
        ob_after = rm.objInfo

        self.assertTrue(ob_before >= ob_after)

    @attr('slow')
    def test_azprtabu_never_breaks_contiguity(self):
        instance = self.map_instance

        instance.cluster('azpRTabu',
                         ['SAR1'],
                         into_regions,
                         dissolve=1)

        feasible = _final_regions_are_contiguous_in_instance(instance)

        self.assertTrue(feasible)

    @attr('slow')
    def test_azprtabu_gives_at_least_same_obj_func(self):
        instance = self.map_instance
        aream = AreaManager(instance.Wrook, instance.Y)
        rm = RegionMaker(aream, into_regions)

        convTabu = len(instance.Y)/into_regions

        ob_before = rm.objInfo
        rm.reactiveTabuMove(convTabu)
        ob_after = rm.objInfo

        self.assertTrue(ob_before >= ob_after)

