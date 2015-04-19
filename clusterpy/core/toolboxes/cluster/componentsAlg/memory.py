# encoding: latin2
"""Algorithm utilities
G{packagetree core}
"""
__author__ = "Juan C. Duque"
__credits__ = "Copyright (c) 2009-11 Juan C. Duque"
__license__ = "New BSD License"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"

from copy import deepcopy

class BasicMemory:
    """
    Keeps the minimum amount of information about a given solution. It keeps the
    Objective function value (self.objInfo) and the region each area has been assigned to
    (self.regions)
    """
    def __init__(self, objInfo=99999999E10, regions={}):
        """
        @type objInfo: float
        @keyword objInfo: Objective function value.

        @type regions: list
        @keyword regions: list of RegionŽs IDs
        values.
        """
        self.objInfo = objInfo
        self.regions = regions

    def updateBasicMemory(self, rm):
        """
        Updates BasicMemory when a solution is modified.
        """
        self.objInfo = rm.objInfo
        self.regions = rm.returnRegions()


class ExtendedMemory(BasicMemory):
    """
    This memory is designed to allow the algorithm to go back to a given solution
    (different from the current solution). It gives to RegionManager all the information that must be
    available in order to continue an iteration process.
    """
    def __init__(self, objInfo=99999999E10, area2Region={}, region2Area={},
            intraBorderingAreas={}):
        """
        @type objInfo: float
        @keyword objInfo: Objective function value

        @type area2region: dictionairy
        @keyword area2region: Region to which the area is in.

        @type region2area: dictionary
        @keyword region2area: areas within the region.

        @type intraBorderingAreas: dictionary
        @keyword intraBorderingAreas: areas in the border of the region.
        """
        BasicMemory.__init__(self, objInfo, {})
        self.area2Region = area2Region
        self.region2Area = region2Area
        self.intraBorderingAreas = intraBorderingAreas

    def updateExtendedMemory(self, rm):
        """
        Updates ExtendedMemory when a solution is modified.
        """
        BasicMemory.updateBasicMemory(self, rm)
        self.area2Region = deepcopy(rm.area2Region)
        self.region2Area = deepcopy(rm.region2Area)
        self.intraBorderingAreas = deepcopy(rm.intraBorderingAreas)

