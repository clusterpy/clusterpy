# encoding: latin2
"""global inequality change test
"""
__author__ = "Juan C. Duque, Alejandro Betancourt"
__credits__ = "Copyright (c) 2009-11 Juan C. Duque"
__license__ = "New BSD License"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"

__all__ = ['inequalityDynamic']

from theilIndex import theil 
import numpy
import itertools

def interregionalInequalityTestOneVariable(Y, area2region, permutations=9999):
    def getVar(Y, possition):
        result = {}
        for k in Y:
            result[k] = [Y[k][possition]]
        return result    
    
    def shuffleMap(Y):
        result = {}
        values = Y.values()
        numpy.random.shuffle(values)
        keys = Y.keys()
        newY = dict(zip(keys,values))
        return newY    

    results = []
    for nv1 in range(len(Y[0])):
        var = getVar(Y,nv1)
        t1,tb1,tw1 = theil(var,area2region)
        numerator = 1
        for iter in range(permutations):
            var = shuffleMap(var)
            t2,tb2,tw2 = theil(var,area2region)
            if tb1 <= tb2:
                numerator += 1
        results.append(numerator/float(permutations+1))
    return results    

def interregionalInequalityTest(Y, fieldNames, area2regions, clusteringNames, outFile, permutations=9999):
    """Interregional inequality tests over time (p-values) 

    This function examines whether the differences across a set of clustering
    solutions are significant. For more information on this function see
    [Rey_Sastre2010] (this function recreates Table 5 in that paper).

        Layer.inequality('interregionalInequalityTest', vars, area2regions, outFile=, <permutations>)

    :keyword vars: List with variables to be analyzed; e.g: ['Y1978', 'Y1979', 'Y1980', 'Y1981'] 
    :type vars: list

    :keyword area2regions: variables in Layer containing regionalization schemes e.g.: ["arisel1", "arisel2", "arisel3", "BELS"]
    :type area2regions: list 

    :keyword outFile: Name for the output file; e.g.: "regionsDifferenceTest.csv"
    :type fileName: string

    :keyword permutations: Number of random spatial permutations. Default value permutations = 9999.
    :type permutations: integer 

    :rtype: None
    :return: None 

    **Example 1** ::

        import clusterpy
        china = clusterpy.importArcData("clusterpy/data_examples/china")
        china.inequality('interregionalInequalityTest',['Y1978', 'Y1979', 'Y1980', 'Y1981'], ['BELS','T78-98','T78-85'], "interregional_inequality_test.csv")

    """
    print "Creating interregional Inequality Test [Rey_Sastre2010 - Table 5]"
    fout = open(outFile,"w")
    line = "," + ",".join(fieldNames) + "\n"
    fout.write(line)
    for ni, i in enumerate(area2regions[0]):
        area2region = [area2regions[x][ni] for x in area2regions]
        results = interregionalInequalityTestOneVariable(Y, area2region, permutations=permutations)
        results = [str(x) for x in results]
        line = clusteringNames[ni] + "," + ",".join(results) + "\n"
        fout.write(line)
    fout.close()
    print "interregional Inequality Test created!"
    return None    
    
