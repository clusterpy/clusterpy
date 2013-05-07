# encoding: latin2
"""global inequality change test
"""
__author__ = "Juan C. Duque, Alejandro Betancourt"
__credits__ = "Copyright (c) 2009-11 Juan C. Duque"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"

__all__ = ['inequalityDynamic']

from theilIndex import theil 
import numpy
import itertools

def interregionalInequalityDifferences(Y, fieldNames, area2regions,
            area2regionsNames, outFile="", permutations=9999):
    """Interregional inequality differences 

    This function examines whether the differences across a set of clustering
    solutions are significant. For more information on this function see
    [Rey_Sastre2010] (this function recreates Table 6 in that paper).
    
        Layer.inequality('interregionalInequalityDifferences', var, clusters, outFile="", <permutations>)

    :keyword var: List with variables to be analyzed; e.g: ['Y1978', 'Y1979', 'Y1980', 'Y1981'] 
    :type var: list
    :keyword clusters: variables in Layer containing regionalization schemes e.g.: ["arisel1", "arisel2", "arisel3", "BELS"]
    :type clusters: list 
    :keyword outFile: Name for the output file; e.g.: "regionsDifferenceTest.csv"
    :type outFile: string 
    :keyword permutations: Number of random spatial permutations. Default value permutations = 9999.
    :type permutations: integer 


    **Example 1** ::

        import clusterpy
        china = clusterpy.importArcData("clusterpy/data_examples/china")
        china.inequality('regionsInequalityDifferenceTest',['Y1978', 'Y1979', 'Y1980', 'Y1981'], ['BELS','T78-98','T86_98'], "interregional_inequality_differences.csv")

    """
    def getVar(Y, possition):
        result = {}
        for k in Y:
            result[k] = [Y[k][possition]]
        return result    
    
    def shuffleMap(Y):
        values = Y.values()
        numpy.random.shuffle(values)
        keys = Y.keys()
        newY = dict(zip(keys,values))
        return newY    

    results = {}
    for nv1, v1 in enumerate(fieldNames):
        for na2r_1,a2r_1 in enumerate(area2regions):
            var = getVar(Y,nv1)
            t1,tb1,tw1 = theil(var,a2r_1)
            name = area2regionsNames[na2r_1]
            results[(v1,name,name)] = tb1
            for na2r_2,a2r_2 in enumerate(area2regions[na2r_1+1:]):
                t2,tb2,tw2 = theil(var,a2r_2)
                oDifference = tb1 - tb2
                numerator = 1
                for iter in range(permutations):
                    var = shuffleMap(var)
                    t3,tb3,tw3 = theil(var,a2r_1)
                    t4,tb4,tw4 = theil(var,a2r_2)
                    rDifference = tb3 - tb4
                    if abs(rDifference) <= abs(oDifference):
                        numerator += 1
                p = numerator/float(permutations+1)
                name2 = area2regionsNames[na2r_2 + na2r_1 + 1]
                results[(v1,name,name2)] = oDifference
                results[(v1,name2,name)] = p
    if outFile:
        fout = open(outFile,"w")
        for var1 in fieldNames:
            aux = str(area2regionsNames).replace("[","")
            aux = aux.replace("]","")
            aux = aux.replace("'","")
            line = "".join([var1,",",aux])
            fout.write("".join([line,"\n"]))
            for a2r in area2regionsNames:
                line = [a2r]
                for a2r2 in area2regionsNames:
                    line += [results[(var1,a2r,a2r2)]]
                line = str(line).replace("[","")
                line = line.replace("]","")
                line = line.replace("'","")
                fout.write("".join([line,"\n"]))
            fout.write("\n")    
        fout.close()        
    return None
