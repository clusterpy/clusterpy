# encoding: latin2
"""Algorithm utilities
G{packagetree core}
"""
__author__ = "Juan C. Duque"
__credits__ = "Copyright (c) 2009-11 Juan C. Duque"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"

from clusterpy.core.toolboxes.cluster.componentsAlg.distanceFunctions import distMethods
import numpy as np

class AreaCl:
    """
    Area Class for Regional Clustering.
    """
    def __init__(self, id, neighs, data, variance="false"):
        """
        @type id: integer
        @param id: Id of the polygon/area

        @type neighs: list
        @param neighs: Neighborhood ids

        @type data: list.
        @param data: Data releated to the area.

        @type variance: boolean
        @keyword variance: Boolean indicating if the data have variance matrix
        """
        self.id = id
        self.neighs = neighs
        if variance == "false":
            self.data = data
        else:
            n = (np.sqrt(9 + 8 * (len(data) - 1)) - 3) / 2
            self.var = np.matrix(np.identity(n))
            index = n + 1
            for i in range(int(n)):
                for j in range(i + 1):
                    self.var[i, j] = data[int(index)]
                    self.var[j, i] = data[int(index)]
                    index += 1
            self.data = data[0: int(n + 1)]

    def returnDistance2Area(self, otherArea, distanceType="EuclideanSquared", indexData=[]):
        """
        Return the distance to `otherArea`
        """
        y0 = []
        y1 = []

        if indexData:
            for index in indexData:
                y0 += [self.data[index]]
                y1 += [otherArea.data[index]]
        else:
            y0 = self.data
            y1 = otherArea.data

        data = [y0] + [y1]
        areaDistance = distMethods[distanceType](data)
        try:
            dist = areaDistance[0][0]
        except:
            dist = areaDistance[0]
        return dist
