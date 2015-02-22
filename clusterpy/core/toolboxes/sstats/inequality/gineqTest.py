# encoding: latin2
"""global inequality change test
"""
__author__ = "Juan C. Duque, Alejandro Betancourt"
__credits__ = "Copyright (c) 2009-11 Juan C. Duque"
__license__ = "New BSD License"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"

__all__ = ['globalInequalityTest']

from theilIndex import theil 
import numpy

def globalInequalityChanges(Y, fieldNames, outFile, permutations=9999):
    """Global inequality change test 

    This function tests whether global inequality has significantly changed
    for the Theil statistic over the period t to t+k. For more information on
    this function see [Rey_Sastre2010] (this function recreates Table 2 in
    that paper).
    
        Layer.inequality('globalInequalityChanges', var, outFile, <permutations>)

    :keyword var: List with variables to be analyzed; e.g: ['Y1978', 'Y1979', 'Y1980', 'Y1981'] 
    :type var: list
    :keyword outFile: Name for the output file; e.g.: "regionsDifferenceTest.csv"
    :type outFile: string 
    :keyword permutations: Number of random spatial permutations. Default value permutations = 9999.
    :type permutations: integer 


    **Example 1** ::

        import clusterpy
        china = clusterpy.importArcData("clusterpy/data_examples/china")
        result = china.inequality('globalInequalityChanges',['Y1978', 'Y1979', 'Y1980', 'Y1981'],  "interregional_inequality_differences.csv")

    """

    def getVar(Y, possition):
        result = {}
        for k in Y:
            result[k] = [Y[k][possition]]
        return result    
    
    def shufflePeriods(Y,pos1,pos2):
        result = {}
        for k in Y:
            possibilities = [Y[k][pos1],Y[k][pos2]]
            result[k] = [possibilities[numpy.random.randint(0,2)]]
        return result    

    print "Creating global Inequality Changes [Rey_Sastre2010 - Table 2]"
    results = {}
    r2a = range(len(Y))
    for nv1, var1 in enumerate(fieldNames):
        var = getVar(Y,nv1)
        t1,tb1,tw1 = theil(var,r2a)
        results[(var1,var1)] = t1
        for nv2, var2 in enumerate(fieldNames[nv1+1:]):
            var = getVar(Y,nv1+nv2+1)
            t2,tb2,tw2 = theil(var,r2a)
            results[(var1,var2)] = t2 - t1
            numerator = 1
            for iter in range(permutations):
                var = shufflePeriods(Y,nv1,nv1 + nv2 + 1)
                t3,tb3,tw3 = theil(var,r2a)
                if abs(t2-t1) < abs(t3-t1):
                    numerator += 1
                results[(var2,var1)] = numerator/float(permutations+1)
    if outFile:
        fout = open(outFile,"w")
        aux = str(fieldNames).replace("[","")
        aux = aux.replace("]","")
        aux = aux.replace("'","")
        line = "".join([",",aux])
        fout.write("".join([line,"\n"]))
        for var1 in fieldNames:
            line = [var1]
            for var2 in fieldNames:
                line += [results[(var1,var2)]]
            line = str(line).replace("[","")
            line = line.replace("]","")
            line = line.replace("'","")
            fout.write("".join([line,"\n"]))
        fout.close()        
    print "global Inequality Changes created!"
    return results                
