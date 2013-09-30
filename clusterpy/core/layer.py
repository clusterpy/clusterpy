# encoding: latin2
"""Repository of clusterPy's main class "Layer"
"""
__author__ = "Juan C. Duque, Alejandro Betancourt"
__credits__ = "Copyright (c) 2009-10 Juan C. Duque"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"
__all__ = ['Layer']
                 

import copy
import cPickle
import numpy
import os
import re
import time
import itertools

from data import generateSAR
from data import generateSMA
from data import generateCAR
from data import generateSpots
from data import generatePositiveSpots
from data import generateUniform
from data import generateGBinomial
from data import generateLBinomial
from data import dissolveData
from data import fieldOperation
from data import spatialLag

from geometry import dissolveLayer
from geometry import transportLayer
from geometry import expandLayer
from geometry import getBbox
from geometry import getGeometricAreas
from geometry import getCentroids

# Clustering
from toolboxes import execAZP
from toolboxes import execArisel
from toolboxes import execAZPRTabu
from toolboxes import execAZPSA
from toolboxes import execAZPTabu
from toolboxes.cluster.pRegionsExact import execPregionsExact
#from toolboxes.cluster.maxpExact import execMaxpExact
from toolboxes import execMaxpTabu
from toolboxes import execAMOEBA
from toolboxes import originalSOM
from toolboxes import geoSom
from toolboxes import geoAssociationCoef
from toolboxes import redistributionCoef
from toolboxes import similarityCoef


# Irregular Maps
from toolboxes import topoStatistics
from toolboxes import noFrontiersW

# Spatial statistics
from toolboxes import globalInequalityChanges
from toolboxes import inequalityMultivar
from toolboxes import interregionalInequalityTest
from toolboxes import interregionalInequalityDifferences


from outputs import dbfWriter
from outputs import shpWriterDis
from outputs import csvWriter

# Contiguity function
from contiguity import dict2matrix 
from contiguity import dict2gal
from contiguity import dict2csv

# Layer
# Layer.dissolveMap
# Layer.addVariable
# Layer.getVars
# Layer.generateData
# Layer.resetData
# Layer.cluster
# Layer.getVars
# Layer.resetData
# Layer.cluster
# Layer.esda
# Layer.exportArcData
# Layer.save
# Layer.exportDBFY
# Layer.exportCSVY
# Layer.exportGALW
# Layer.exportCSVW
# Layer.exportOutputs
# Layer.transport
# Layer.expand
class Layer():
    """Main class in clusterPy

    It is an object that represents an original map and all the
    other maps derived from it after running any algorithm.

    The layer object can be also represented as an inverse tree
    with an upper root representing the original map and the
    different branches representing other layers related to the
    root.

    """
    def __init__(self):
        """
    **Attributes**

        * Y: dictionary (attribute values of each feature)
        * fieldNames: list (fieldNames List of attribute names)
        * areas: list (list containing the coordinates of each feature)
        * region2areas: list (list of lenght N (number of areas) with the ID of the region to which each area has been assigned during the last algorithm run)
        * Wqueen: dictionary (spatial contiguity based on queen criterion)
        * Wrook: dictionary (spatial contiguity based on rook criterion)
        * Wcustom: dictionary (custom spatial contiguity based on any other criterion)
        * type: string (layer's geometry type ('polygons','lines','points'))
        * results: list (repository of layer instances from running an algorithm)
        * outputCluster: dictionary (information about different characteristics of a solution (time, parameters, OS, among others))
        * name: string (layer's name; default is 'root')
        * outputDissolve: dictionary (keep information from which the current layer has been created)
        * father: Layer (layer from which the current layer has been generated)
        * bbox: tuple (bounding box)
        """
        # Object Attributes
        self.Y = {}
        self.fieldNames = []
        self.areas = []
        self.region2areas = []
        self.Wqueen = {}
        self.Wrook = {}
        self.customW = {}
        self.shpType = ''
        self.results = []
        self.name = ""
        self.outputCluster = {}
        self.outputCluster['r2a'] = []
        self.outputCluster['r2aRoot'] = []
        self.outputDissolve = {}
        self.outputDissolve['r2a'] = []
        self.outputDissolve['r2aRoot'] = []
        self.father = []
        self.bbox = []
        self.tStats = []

    def dissolveMap(self, var=None, dataOperations={}):
        """
        **Description**

        Once you run an aggregation algorithm you can use the dissolve function to create a new map where the new polygons result from dissolving borders between areas assigned to the same region.

        The dissolve map is an instance of a layer that is located inside the original layer. The dissolved map is then a "child" layer to which you can apply the same methods available for any layer. It implies that you can easily perform nested aggregation by applying aggregation algorithms to already dissolved maps.

        :param var: It is the variable that indicates which areas belong to the same regions. This variable is usually the variable that is saved to a layer once an aggregation algorithm is executed. This variable can also be already included in your map, or it can be added from an external file.
        :type var: string

        :param dataOperations: Dictionary which maps a variable to a list of operations to run on it. The dissolved layer will contain in it's data all the variables specified in this dictionary. Be sure to check the dissolved layer fieldNames before use it's variables.
        :type dataOperations: dictionary

        The dictionary structure must be as showed bellow.::

        >>> X = {}
        >>> X[variableName1] = [function1, function2,....]
        >>> X[variableName2] = [function1, function2,....]

        Where functions are strings which represent the names of the functions to be used on the given variable (variableName). Functions could be,'sum','mean','min','max','meanDesv','stdDesv','med', 'mode','range','first','last','numberOfAreas'. 
        
        If you do not use this structure, the new layer (i.e.., the dissolved
        map) will have just the ID field.

        **Examples**

        Dissolve china using the result from an aggregation algorithm ::
        
            import clusterpy
            china = clusterpy.importArcData("clusterpy/data_examples/china")
            china.cluster('azpSa', ['Y1990', 'Y991'], 5)
            china.dissolveMap()
        
        Dissolve a China layer using a stored result on BELS ::
        
            import clusterpy
            china = clusterpy.importArcData("clusterpy/data_examples/china")
            china.dissolveMap(var="BELS")


        Dissolve china using the result from an aggregation algorithm. It also generates two new variables in the dissolved map. These new variables are the regional mean and sum of attributes "Y1978" and "Y1979" ::

            import clusterpy
            china = clusterpy.importArcData("clusterpy/data_examples/china")
            china.cluster('azpSa', ['Y1990', 'Y991'], 5)
            dataOperations = {'Y1978':['sum', 'mean'],'Y1979':['sum', 'mean']}
            china.dissolveMap(dataOperations=dataOperations)

        
        """
        print "Dissolving lines"
        sh = Layer()
        if var is not None:
            if var in self.fieldNames:
                region2areas = map(lambda x: x[0],self.getVars(var).values())
                dissolveLayer(self, sh, region2areas)
                sh.outputDissolve = {"objectiveFunction": "Unknown",\
                "runningTime": "Unknown", "aggregationVariables": "Unknown",\
                "algorithm":"Unknown", "weightType":"Unknown", \
                "regions": len(sh.areas), "distanceType": "Unknown", "distanceStat": "Unknown", \
                "selectionType": "Unknown", "objectiveFunctionType": "Unknown", \
                "OS":os.name, "proccesorArchitecture": os.getenv('PROCESSOR_ARCHITECTURE'), \
                "proccesorIdentifier": os.getenv('PROCESSOR_IDENTIFIER'),
                "numberProccesor": os.getenv('NUMBER_OF_PROCESSORS'),
                "r2a": self.region2areas}
                sh.Y, sh.fieldNames = dissolveData(self.fieldNames, self.Y,
                                                  region2areas, dataOperations)
            else:
                raise NameError("The variable (%s) is not valid" %var)
        else:
            if self.region2areas == []:
                raise NameError("You have not executed any algorithm")
            else:
                dissolveLayer(self, sh, self.region2areas)
                outputKey = self.fieldNames[-1]
                dissolveInfo = self.outputCluster[outputKey]
                dissolveInfo['fieldName'] = outputKey
                sh.outputDissolve = dissolveInfo
                sh.Y,sh.fieldNames = dissolveData(self.fieldNames, self.Y,
                                                      self.region2areas, dataOperations)
        print "Done"

    def getVars(self, *args):
        """Getting subsets of data
        
        :param args: subset data fieldNames.
        :type args: tuple
        :rtype: Dictionary (Data subset)

        **Description**

        This function allows the user to extract a subset of variables from a
        layer object.
        
        **Examples**

        Getting Y1998 and Y1997 from China ::
        
            import clusterpy
            china = clusterpy.importArcData("clusterpy/data_examples/china")
            subset = china.getVars(["Y1998", "Y1997"])
        """
        print "Getting variables"
        fields = []
        for argument in args:
            if isinstance(argument, list):
                for argumentIn in argument:
                    fields.append(argumentIn)
            else:
                fields.append(argument)
        labels = self.fieldNames
        count = 0
        subY = {}
        for i in self.Y.keys():
            subY[i] = []
        for j in fields:
            for i in range(len(labels)):
                if labels[i] == j:
                    for j in self.Y.keys():
                        subY[j] = subY[j] + [self.Y[j][i]]
        print "Variables successfully extracted"
        return subY

    def addVariable(self, names, values):
        """Adding new variables
        
        :param names: field name
        :type names: list
        :param values: data
        :type values: dictionary

        **Description**

        On the example below the population of China in 1990 is multiplied by 10 and stored on the layer as "10Y1900". Note that using the power of Python and clusterPy together the number of possible new variables is unlimited.

        **Examples**

        **Example 1**::

            import clusterpy
            china = clusterpy.importArcData("clusterpy/data_examples/china")
            Y1990 = china.getVars(["Y1990"])
            MY1990 = {}
            for area_i,pop in enumerate(Y1990):
               MY1990[area_i] = pop*10
            china.addVariable(['10Y1990'], MY1990)

        **Example 2** ::

            import clusterpy
            china = clusterpy.importArcData("clusterpy/data_examples/china")
            chinaData = clusterpy.importCSV("clusterpy/data_examples/china.csv")
            china.addVariable(chinaData[1],chinaData[0])
        """
        print "Adding variables"
        self.fieldNames += (names)
        for area in range(len(values)):
            if area in self.Y:
                if type(values[area]) is not list:
                    self.Y[area] += [values[area]]
                else:
                    self.Y[area] += values[area]
            else:
                self.Y[area] = [values[area]]
        print "Done"

    def spatialLag(self,variables,wtype="queen"):
        """Spatial lag of a set of variables
        
        :param variables: data dictionary to be lagged
        :type variables: dictionary

        **Description**

        This function calculates the lagged value of a set of variables using
        the wrook specified as input. The result is stored in the layer data
        using the original variable name preceded of "sl_"

        **Examples**

        **Example 1**::

            import clusterpy
            china = clusterpy.importArcData("clusterpy/data_examples/china")
            china.spatialLag(["Y1990","Y1991"])
            china.exportArcData("chinaLagged")
        """
        if wtype == 'rook':
            w = self.Wrook
        elif wtype == 'queen':
            w = self.Wqueen
        else:
            print "Contiguity type is not supported"
        
        wmatrix = dict2matrix(w,std=1,diag=0)
        data = self.getVars(*variables)
        lags = spatialLag(data,wmatrix)
        names = ["sl_" + x  for x in variables]
        self.addVariable(names,lags)

        
    
    def generateData(self, process, wtype, n, *args, **kargs):
        """Simulate data according to a specific stochastic process
        
        :param process: type of data to be generated.
        :type process: string
        :param wtype: contiguity matrix to be used in order to generate the data.
        :type wtype: string 
        :param n: number of processes to be generated.
        :type n: integer
        :param args: extra parameters of the simulators
        :type args: tuple

        :keyword integer: 0 for float variables and 1 for integer variables , by default 0.
        :type integer: boolean

        **Description**
        
        In order to make the random data generation on clusterPy easier, we
        provide a wide range of processes that can be generated with a single command. At the 
        moment the available processes and their optional parameters are:

        * **Spatial autoregressive process (SAR)** 
            * rho: Autoregressive coefficient
        * **Spatial Moving Average (SMA)**
            * rho: Autoregressive coefficient
        * **CAR**
            * rho: Autoregressive coefficient
        * **Random Spatial Clusters (Spots)**
            * nc: Number of clusters
            * compact: Compactness level (0 chain clusters - 1 compact clusters) 
            * Zalpha: Z value for the significance level of each cluster.
        * **Positive Random Spatial Clusters (postive_spots)**
            * nc: Number of clusters
            * compact: Compactness level (0 chain clusters - 1 compact clusters) 
            * Zalpha: Z value of the significance level of each cluster. It is necesary
            to take into account that the dsitribution of data is the absolute of a normal
            distribution.
        * **Uniform process (Uniform)** 
            * min: Uniform minimum
            * max: Uniform maximum
        * **Global Binomial (GBinomial)** (Only one distribution for all the areas)
            * pob: Global Population
            * prob: Global Probabilities
        * **Local Binomial LBinomial** (Different distributions for each area.)
            * Var_pob: Population field name.
            * Var_prob: Probability field name.

        **Examples**
        
        Generating a float SAR variable for China with an autoregressive
        coefficient of 0.7 ::
        
            import clusterpy
            china = clusterpy.importArcData("clusterpy/data_examples/china")
            china.generateData("SAR", "rook", 1, 0.7)

        Generating a integer SAR variable for China with an autoregressive coefficient of 0.7 ::

            import clusterpy
            china = clusterpy.importArcData("clusterpy/data_examples/china")
            china.generateData("SAR", "rook", 1, 0.7, integer=1)

        Generating a float SMA variable for China with an autoregressive coefficient of 0.3 ::

            import clusterpy
            china = clusterpy.importArcData("clusterpy/data_examples/china")
            china.generateData("SMA", "queen", 1, 0.3)

        Generating an integer SMA variable for China with an autoregressive coefficient of 0.3 ::

            import clusterpy
            china = clusterpy.importArcData("clusterpy/data_examples/china")
            china.generateData("SMA", "queen", 1, 0.3, integer=1)

        Generating a float CAR variable for China with an autoregressive coefficient of 0.7 ::
        
            import clusterpy
            china = clusterpy.importArcData("clusterpy/data_examples/china")
            china.generateData("CAR", "queen", 1, 0.7)

        Generating an integer CAR variable for China with an autoregressive coefficient of 0.7 ::
        
            import clusterpy
            china = clusterpy.importArcData("clusterpy/data_examples/china")
            china.generateData("CAR", "queen", 1, 0.7, integer=1)

        Generating a float Spot process on China each with 4 clusters, and compactness level of 0.7 and an Zalpha value of 1.28 ::

            import clusterpy
            china = clusterpy.importArcData("clusterpy/data_examples/china")
            china.generateData("Spots", "queen", 1, 4, 0.7, 1.28)

        Generating an integer Spot process on China each with 4 clusters, and compactness level of 0.7 and an Zalpha value of 1.28::

            import clusterpy
            china = clusterpy.importArcData("clusterpy/data_examples/china")
            china.generateData("Spots", "queen", 1, 4, 0.7, 1.28, integer=1)

        Generating a float Spot process with only positive values on China each with 4 clusters, and compactness level of 0.7 and an Zalpha value of 1.64 ::

            import clusterpy
            china = clusterpy.importArcData("clusterpy/data_examples/china")
            china.generateData("positive_spots", "queen", 1, 4, 0.7, 1.64)
        
        Generating a float Spot process with only positive values over a grid
        of 30 by 30 with 4 clusters, a compactness level of 0.7 and an Zalpha
        value of 1.64 ::

            import clusterpy
            grid = clusterpy.createGrid(30,30)
            grid.generateData("positive_spots", "queen", 1, 4, 0.7, 1.64)
        
        Generating a local Binomial process on china with Y1998 as population level and simulated uniform probability (Uniform31) as risk level. ::

            import clusterpy
            china = clusterpy.importArcData("clusterpy/data_examples/china")
            china.generateData("Uniform", "queen", 1, 0, 1)
            china.fieldNames
            china.generateData("LBinomial", "rook", 1, "Y1998", "Uniform31")

        Generating a Binomial process on China with the same parameters for all the features ::

            import clusterpy
            china = clusterpy.importArcData("clusterpy/data_examples/china")
            china.generateData("GBinomial", 'queen',1 , 10000, 0.5)

        Generating a float Uniform process between 1 and 10 ::

            import clusterpy
            china = clusterpy.importArcData("clusterpy/data_examples/china")
            china.generateData("Uniform", 'queen', 1, 1, 10)

        Generating an integer Uniform process between 1 and 10 ::

            import clusterpy
            china = clusterpy.importArcData("clusterpy/data_examples/china")
            china.generateData("Uniform", 'queen', 1, 1, 10, integer=1)
        """
        fields = []
        print "Generating " + process
        if wtype == 'rook':
            w = self.Wrook
        else:
            w = self.Wqueen
        if kargs.has_key("integer"):
            integer = kargs["integer"]
        else:
            integer = 0
        if process == 'SAR':
            y = generateSAR(w, n, *args)
            fields.extend(['SAR'+ str(i + len(self.fieldNames)) for i in range(n)])
        elif process == 'SMA':
            y = generateSMA(w, n, *args)
            fields.extend(['SMA'+ str(i + len(self.fieldNames)) for i in range(n)])
        elif process == 'CAR':
            y = generateCAR(w, n, *args)
            fields.extend(['CAR'+ str(i + len(self.fieldNames)) for i in range(n)])
        elif process == 'Spots':
            ylist = [generateSpots(w, *args) for i in xrange(n)]
            fields.extend(['Spots' + str(i + len(self.fieldNames)) for i in range(n)])
            y = {}
            for i in xrange(len(w)):
                y[i] = [x[i][0] for x in ylist]
        elif process == 'positive_spots':
            ylist = [generatePositiveSpots(w, *args) for i in xrange(n)]
            fields.extend(['pspots' + str(i + len(self.fieldNames)) for i in range(n)])
            y = {}
            for i in xrange(len(w)):
                y[i] = [x[i][0] for x in ylist]
        elif process == 'Uniform':
            y = generateUniform(w, n, *args)
            fields.extend(['Uniform' + str(i + len(self.fieldNames)) for i in range(n)])
        elif process == 'GBinomial':
            # global parameters for the data
            y = generateGBinomial(w, n, *args)
            fields.extend(['Bino'+ str(i + len(self.fieldNames)) for i in range(n)])
        elif process == 'LBinomial':
            # local parameters for each area
            arg = [arg for arg in args]
            y_pob = self.getVars(arg[0])
            y_pro = self.getVars(arg[1])
            y = generateLBinomial(n, y_pob, y_pro)
            fields.extend(['Bino' + str(i + len(self.fieldNames)) for i in range(n)])

        for i in self.Y.keys():
            if integer == 1:
                self.Y[i] = self.Y[i] + [int(z) for z in y[i]]
            else:
                self.Y[i] = self.Y[i] + y[i]

        self.fieldNames.extend(fields)
        print "Done [" + process + "]" 
        
    def dataOperation(self,function):
        """
        This function allows the creation of new variables. The variables must
        be created using python language operations between variables.

        :param function: This string is a python language operation which must include the variable name followed by the character "=" and the operations that must be executed in order to create the new variable.  The new variable will be added as a new data attribute and the variable name will be added to fieldNames.  
        :type function: string
        
        
        **Examples**

        Creating a new variable wich is the sum of another two ::

            import clusterpy
            china = clusterpy.importArcData("clusterpy/data_examples/china")
            china.dataOperation("Y9599 = Y1995 + Y1998")

        Standardizing Y1995 ::

            import clusterpy
            import numpy
            china = clusterpy.importArcData("clusterpy/data_examples/china")
            values = [i[0] for i in china.getVars("Y1995").values()]
            mean_value = numpy.mean(values)
            std_value = numpy.std(values)
            china.dataOperation("Y1995St = (Y1995 - " + str(mean_value) + ")/float(" + str(std_value) + ")")

        Scaling Y1998 bewtween 0 and 1. ::

            import clusterpy
            import numpy
            china = clusterpy.importArcData("clsuterpy/data_examples/china")
            values = [i[0] for i in china.getVars("Y1998").values()]
            max_value = max(values)
            min_value = min(values)
            china.dataOperation("Y1998Sc = (Y1998 - " + str(min_value) + ")/float(" + str(max_value - min_value) + ")")
        """
        m = re.match(r"(.*)\s?\=\s?(.*)", function)
        if "groups" in dir(m):
            fieldName = m.group(1).replace(" ", "")
            if fieldName in self.fieldNames:
                raise NameError("Variable " + str(fieldName) + " already exists")
            function = m.group(2)
            newVariable = fieldOperation(function, self.Y, self.fieldNames)
            print "Adding " + fieldName + " to fieldNames"
            print "Adding values from " + function + " to Y"
            self.addVariable([fieldName], newVariable)
        else:
            raise NameError("Function is not well structured, it must include variable\
Name followed by = signal followed by the fieldOperations")
    

    def resetData(self):
        """
        All data available on the layer is deleted, keeping only the 'ID'
        variable 

        **Examples** ::   

            import clusterpy
            china = clusterpy.importArcData("clusterpy/data_examples/china")
            china.resetData()
        """
        for i in self.Y.keys():
            self.Y[i] = [i]
        self.fieldNames = ['ID']
        print "Done"
    
    def cluster(*args, **kargs):
        """
        Layer.cluster contains a wide set of algorithms for clustering with spatial contiguity constraints. For literature reviews on constrained clustering, see [Murtagh1985]_, [Gordon1996]_, [Duque_Ramos_Surinach2007]_.

        Below you will find links that take you to a detailed description of
        each algorithm.

        The available algorithms are:

        * Arisel [Duque_Church2004]_, [Duque_Church_Middleton2011]_: 
            * :ref:`Arisel description <arisel_description>`.
            * :ref:`Using Arisel with clusterPy <arisel_examples>`.

        * AZP [Openshaw_Rao1995]_: 
            * :ref:`AZP description <azp_description>`.
            * :ref:`Using AZP with clusterPy <azp_examples>`.

        * AZP-Simulated Annealing [Openshaw_Rao1995]_.
            * :ref:`AZPSA description <azpsa_description>`.
            * :ref:`Using AZPSA with clusterPy <azpsa_examples>`.

        * AZP-Tabu [Openshaw_Rao1995]_.
            * :ref:`AZP Tabu description <azpt_description>`.
            * :ref:`Using AZP Tabu with clusterPy <azpt_examples>`.

        * AZP-R-Tabu [Openshaw_Rao1995]_.
            * :ref:`AZP Reactive Tabu description <azprt_description>`.
            * :ref:`Using AZP reactive Tabu with clusterPy <azprt_examples>`.

        ORGANIZAR QUE FUNCIONE
        * P-regions (Exact) [Duque_Church_Middleton2009]_.
            * :ref:`P-regions description <pregions_description>`.
            * :ref:`Using P-regions with clusterPy <pregions_examples>`. 

        * Max-p-regions (Tabu) [Duque_Anselin_Rey2010]_.
            * :ref:`Max-p description <maxp_description>`.
            * :ref:`Using Max-p with clusterPy <maxp_examples>`.

        * AMOEBA [Alstadt_Getis2006]_, [Duque_Alstadt_Velasquez_Franco_Betancourt2010]_.
            * :ref:`AMOEBA description <amoeba_description>`.
            * :ref:`Using AMOEBA with clusterPy <amoeba_examples>`.

        * SOM [Kohonen1990]_.
            * :ref:`SOM description <som_description>`.
            * :ref:`Using SOM with clusterPy <som_examples>`.
         
        * geoSOM [Bacao_Lobo_Painho2004]_.
            * :ref:`GeoSOM description <geosom_description>`.
            * :ref:`Using geoSOM with clusterPy <geosom_examples>`.

        * Random     

        :param args: Basic parameters.
        :type args: tuple
        :param kargs: Optional parameter keywords.
        :type kargs: dictionary
        
        The dataOperations dictionary used by 'dissolveMap <dissolveMap>' could be 
        passed in order to specify which data should be calculated for the dissolved
        layer. The dataOperations dictionary must be:

        >>> X = {}
        >>> X[variableName1] = [function1, function2,....]
        >>> X[variableName2] = [function1, function2,....]

        Where functions are strings wich represents the name of the functions to 
        be used on the given variableName. Functions could be,'sum','mean','min',
        'max','meanDesv','stdDesv','med', 'mode','range','first','last',
        'numberOfAreas. By deffault just ID variable is added to the dissolved 
        map.

        **Examples**

        .. _arisel_examples:

        **ARISEL**

        :ref:`Arisel description <arisel_description>`:

        **Example 1** ::

            import clusterpy
            instance = clusterpy.createGrid(10, 10)
            instance.generateData("SAR", 'rook', 1, 0.9)
            instance.exportArcData("testOutput/arisel_1_input")
            instance.cluster('arisel', ['SAR1'], 15, dissolve=1)
            instance.results[0].exportArcData("testOutput/arisel_1_solution")

        .. image:: ../_static/ARISEL1.png

        **Example 2** ::

            import clusterpy
            instance = clusterpy.createGrid(10, 10)
            instance.generateData("SAR", 'rook', 2, 0.9)
            instance.exportArcData("testOutput/arisel_2_input")
            instance.cluster('arisel', ['SAR1', 'SAR2'], 15, wType='queen', std=1, inits=3, convTabu=5, tabuLength=5, dissolve=1)
            instance.results[0].exportArcData("testOutput/arisel_2_solution")


        **Example 3** ::
        
            import clusterpy
            instance = clusterpy.createGrid(3, 3)
            instance.generateData("SAR", 'rook', 2, 0.9)
            instance.exportArcData("testOutput/arisel_3_input")
            instance.cluster('arisel', ['SAR1', 'SAR2'], 3, wType='queen', std=1, inits=1, initialSolution=[0, 0, 1, 0, 1, 1, 2, 2, 2], convTabu=5, tabuLength=5, dissolve=1)
            instance.results[0].exportArcData("testOutput/arisel_3_solution")


        **Example 4** ::
        
            import clusterpy
            calif = clusterpy.importArcData("clusterpy/data_examples/CA_Polygons")
            calif.fieldNames
            dataOperations = {'POP1970':['sum', 'mean'], 'POP2001':['sum', 'mean']}
            calif.exportArcData("testOutput/arisel_4_input")
            calif.cluster('arisel', ['POP1970', 'POP2001'], 15, inits= 3, dissolve=1, dataOperations=dataOperations)
            calif.results[0].exportArcData("testOutput/arisel_4_solution")


        **Example 5** ::
        
            import clusterpy
            calif = clusterpy.importArcData("clusterpy/data_examples/CA_Polygons")
            calif.fieldNames
            calif.dataOperation("g70_01 = float(POP2001 - POP1970) / POP1970")
            calif.exportArcData("testOutput/arisel_5_input")
            calif.cluster('arisel', ['g70_01'], 15, inits= 4, dissolve=1)
            calif.results[0].exportArcData("testOutput/arisel_5_solution")


        .. image:: ../_static/ARISEL5.png
       
        .. _azp_examples:

        **AZP**
       
        :ref:`AZP description <azp_description>`

        **Example 1** ::

            import clusterpy
            instance = clusterpy.createGrid(10, 10)
            instance.generateData("SAR", 'rook', 2, 0.9)
            instance.exportArcData("testOutput/azp_1_input")
            instance.cluster('azp', ['SAR1'], 15, dissolve=1)
            instance.results[0].exportArcData("testOutput/azp_1_solution")


        .. image:: ../_static/AZP1.png


        **Example 2** ::

            import clusterpy
            instance = clusterpy.createGrid(10, 10)
            instance.generateData("SAR", 'rook', 2, 0.9)
            instance.exportArcData("testOutput/azp_2_input")
            instance.cluster('azp', ['SAR1', 'SAR2'], 15, wType='queen', std=1, dissolve=1)
            instance.results[0].exportArcData("testOutput/azp_2_solution")


        **Example 3** ::
        
            import clusterpy
            instance = clusterpy.createGrid(3, 3)
            instance.generateData("SAR", 'rook', 2, 0.9)
            instance.exportArcData("testOutput/azp_3_input")
            instance.cluster('azp', ['SAR1', 'SAR2'], 3, wType='queen', std=1, initialSolution=[0, 0, 1, 0, 1, 1, 2, 2, 2], dissolve=1)
            instance.results[0].exportArcData("testOutput/azp_3_solution")


        **Example 4** ::
        
            import clusterpy
            calif = clusterpy.importArcData("clusterpy/data_examples/CA_Polygons")
            calif.fieldNames
            dataOperations = {'POP1970':['sum', 'mean'], 'POP2001':['sum', 'mean']}
            calif.exportArcData("testOutput/azp_4_input")
            calif.cluster('azp', ['POP1970', 'POP2001'], 15, dissolve=1, dataOperations=dataOperations)
            calif.results[0].exportArcData("testOutput/azp_4_solution")


        **Example 5** ::
        
            import clusterpy
            calif = clusterpy.importArcData("clusterpy/data_examples/CA_Polygons")
            calif.fieldNames
            calif.dataOperation("g70_01 = float(POP2001 - POP1970) / POP1970")
            calif.exportArcData("testOutput/azp_5_input")
            calif.cluster('azp', ['g70_01'], 15, dissolve=1)
            calif.results[0].exportArcData("testOutput/azp_5_solution")


        .. image:: ../_static/AZP5.png

        .. _azpsa_examples:

        **AZP Simulated Annealing**
        
        :ref:`AZP Simulated Annealing description <azpsa_description>`

        **Example 1** ::

            import clusterpy
            instance = clusterpy.createGrid(10, 10)
            instance.generateData("SAR", 'rook', 2, 0.9)
            instance.exportArcData("testOutput/azpSA_1_input")
            instance.cluster('azpSa', ['SAR1'], 15, dissolve=1)
            instance.results[0].exportArcData("testOutput/azpSA_1_solution")


        .. image:: ../_static/AZPSA1.png

        **Example 2** ::

            import clusterpy
            instance = clusterpy.createGrid(10, 10)
            instance.generateData("SAR", 'rook', 2, 0.9)
            instance.exportArcData("testOutput/azpSA_2_input")
            instance.cluster('azpSa', ['SAR1', 'SAR2'], 15, wType='queen', std=1, maxit=2, dissolve=1)
            instance.results[0].exportArcData("testOutput/azpSA_2_solution")


        **Example 3** ::
        
            import clusterpy
            instance = clusterpy.createGrid(3, 3)
            instance.generateData("SAR", 'rook', 2, 0.9)
            instance.exportArcData("testOutput/azpSA_3_input")
            instance.cluster('azpSa', ['SAR1', 'SAR2'], 3, wType='queen', std=1, initialSolution=[0, 0, 1, 0, 1, 1, 2, 2, 2], maxit=2, dissolve=1)
            instance.results[0].exportArcData("testOutput/azpSA_3_solution")


        **Example 4** ::
        
            import clusterpy
            calif = clusterpy.importArcData("clusterpy/data_examples/CA_Polygons")
            calif.fieldNames
            dataOperations = {'POP1970':['sum', 'mean'], 'POP2001':['sum', 'mean']}
            calif.exportArcData("testOutput/azpSA_4_input")
            calif.cluster('azpSa', ['POP1970', 'POP2001'], 15, dissolve=1, dataOperations=dataOperations)
            calif.results[0].exportArcData("testOutput/azpSA_4_solution")


        **Example 5** ::
        
            import clusterpy
            calif = clusterpy.importArcData("clusterpy/data_examples/CA_Polygons")
            calif.fieldNames
            calif.dataOperation("g70_01 = float(POP2001 - POP1970) / POP1970")
            calif.exportArcData("testOutput/azpSA_5_input")
            calif.cluster('azpSa', ['g70_01'], 15, dissolve=1)
            calif.results[0].exportArcData("testOutput/azpSA_5_solution")

        .. image:: ../_static/AZPSA5.png

        .. _azpt_examples:

        **AZP Tabu**

        :ref:`AZP tabu description <azpt_description>`

        **Example 1** ::
        
            import clusterpy
            instance = clusterpy.createGrid(10, 10)
            instance.generateData("SAR", 'rook', 1, 0.9)
            instance.exportArcData("testOutput/azpTabu_1_input")
            instance.cluster('azpTabu', ['SAR1'], 15, dissolve=1)
            instance.results[0].exportArcData("testOutput/azpTabu_1_solution")


        .. image:: ../_static/AZPT1.png

        **Example 2** ::

            import clusterpy
            instance = clusterpy.createGrid(10, 10)
            instance.generateData("SAR", 'rook', 2, 0.9)
            instance.exportArcData("testOutput/azpTabu_2_input")
            instance.cluster('azpTabu', ['SAR1', 'SAR2'], 15, wType='queen', std=1, convTabu=5, tabuLength=5, dissolve=1)
            instance.results[0].exportArcData("testOutput/azpTabu_2_solution")


        **Example 3** ::
        
            import clusterpy
            instance = clusterpy.createGrid(3, 3)
            instance.generateData("SAR", 'rook', 2, 0.9)
            instance.exportArcData("testOutput/azpTabu_3_input")
            instance.cluster('azpTabu', ['SAR1', 'SAR2'], 3, wType='queen', std=1, initialSolution=[0, 0, 1, 0, 1, 1, 2, 2, 2], convTabu=5, tabuLength=5, dissolve=1)
            instance.results[0].exportArcData("testOutput/azpTabu_3_solution")


        **Example 4** ::
        
            import clusterpy
            calif = clusterpy.importArcData("clusterpy/data_examples/CA_Polygons")
            calif.fieldNames
            dataOperations = {'POP1970':['sum', 'mean'], 'POP2001':['sum', 'mean']}
            calif.exportArcData("testOutput/azpTabu_4_input")
            calif.cluster('azpTabu', ['POP1970', 'POP2001'], 15, dissolve=1, dataOperations=dataOperations)
            calif.results[0].exportArcData("testOutput/azpTabu_4_solution")



        **Example 5** ::
        
            import clusterpy
            calif = clusterpy.importArcData("clusterpy/data_examples/CA_Polygons")
            calif.fieldNames
            calif.dataOperation("g70_01 = float(POP2001 - POP1970) / POP1970")
            calif.exportArcData("testOutput/azpTabu_5_input")
            calif.cluster('azpTabu', ['g70_01'], 15, dissolve=1)
            calif.results[0].exportArcData("testOutput/azpTabu_5_solution")


        .. image:: ../_static/AZPT5.png

        .. _azprt_examples:

        **AZP Reactive Tabu**

        :ref:`AZP reactive tabu description <azprt_description>`

        **Example 1** ::

            import clusterpy
            instance = clusterpy.createGrid(10, 10)
            instance.generateData("SAR", 'rook', 1, 0.9)
            instance.exportArcData("testOutput/azpRTabu_1_input")
            instance.cluster('azpRTabu', ['SAR1'], 15, dissolve=1)
            instance.results[0].exportArcData("testOutput/azpRTabu_1_solution")


        .. image:: ../_static/AZPR1.png

        **Example 2** ::

            import clusterpy
            instance = clusterpy.createGrid(10, 10)
            instance.generateData("SAR", 'rook', 2, 0.9)
            instance.exportArcData("testOutput/azpRTabu_2_input")
            instance.cluster('azpRTabu', ['SAR1', 'SAR2'], 15, wType='queen', std=1, convTabu=5, dissolve=1)
            instance.results[0].exportArcData("testOutput/azpRTabu_2_solution")


        **Example 3** ::
        
            import clusterpy
            instance = clusterpy.createGrid(3, 3)
            instance.generateData("SAR", 'rook', 2, 0.9)
            instance.exportArcData("testOutput/azpRTabu_3_input")
            instance.cluster('azpRTabu', ['SAR1', 'SAR2'], 3, wType='queen', std=1, initialSolution=[0, 0, 1, 0, 1, 1, 2, 2, 2], convTabu=5, dissolve=1)
            instance.results[0].exportArcData("testOutput/azpRTabu_3_solution")


        **Example 4** ::
        
            import clusterpy
            calif = clusterpy.importArcData("clusterpy/data_examples/CA_Polygons")
            calif.fieldNames
            dataOperations = {'POP1970':['sum', 'mean'], 'POP2001':['sum', 'mean']}
            calif.exportArcData("testOutput/azpRTabu_4_input")
            calif.cluster('azpRTabu', ['POP1970', 'POP2001'], 15, dissolve=1, dataOperations=dataOperations)
            calif.results[0].exportArcData("testOutput/azpRTabu_4_solution")


        **Example 5** ::
        
            import clusterpy
            calif = clusterpy.importArcData("clusterpy/data_examples/CA_Polygons")
            calif.fieldNames
            calif.dataOperation("g70_01 = float(POP2001 - POP1970) / POP1970")
            calif.exportArcData("testOutput/azpRTabu_5_input")
            calif.cluster('azpRTabu', ['g70_01'], 15, dissolve=1)
            calif.results[0].exportArcData("testOutput/azpRTabu_5_solution")


        .. image:: ../_static/AZPR5.png

        .. _lamaxp_examples:

        **MAX-P**
        
        :ref:`Max-p region description <maxp_description>`

        **Example 1** ::

            import clusterpy
            instance = clusterpy.createGrid(10, 10)
            instance.generateData("SAR", 'rook', 1, 0.9)
            instance.generateData('Uniform', 'rook', 1, 10, 15)
            instance.exportArcData("testOutput/maxpTabu_1_input")
            instance.cluster('maxpTabu', ['SAR1', 'Uniform2'], threshold=130, dissolve=1)
            instance.results[0].exportArcData("testOutput/maxpTabu_1_solution")


        .. image:: ../_static/Maxp1.png

        **Example 2** ::

            import clusterpy
            instance = clusterpy.createGrid(10, 10)
            instance.generateData("SAR", 'rook', 1, 0.9)
            instance.generateData('Uniform', 'rook', 1, 10, 15)
            instance.exportArcData("testOutput/maxpTabu_2_input")
            instance.cluster('maxpTabu', ['SAR1', 'Uniform2'], threshold=130, wType='queen', maxit=3, tabuLength=5, dissolve=1)
            instance.results[0].exportArcData("testOutput/maxpTabu_2_solution")


        **Example 3** ::
        
            import clusterpy
            calif = clusterpy.importArcData("clusterpy/data_examples/CA_Polygons")
            calif.fieldNames
            dataOperations = {'POP1970':['sum', 'mean'], 'POP2001':['sum', 'mean']}
            calif.exportArcData("testOutput/maxpTabu_3_input")
            calif.cluster('maxpTabu', ['POP1970', 'POP2001'], threshold=100000, dissolve=1, dataOperations=dataOperations)
            calif.results[0].exportArcData("testOutput/maxpTabu_3_solution")


        **Example 4** ::

            import clusterpy
            calif = clusterpy.importArcData("clusterpy/data_examples/CA_Polygons")
            calif.fieldNames
            calif.dataOperation("g70_01 = float(POP2001 - POP1970) / POP1970")
            calif.exportArcData("testOutput/maxpTabu_4_input")
            calif.cluster('maxpTabu', ['g70_01', 'POP2001'], threshold=100000, dissolve=1,std=1)
            calif.results[0].exportArcData("testOutput/maxpTabu_4_solution")

        .. image:: ../_static/Maxp4.png

        .. _amoeba_examples:

        **AMOEBA**

        :ref:`AMOEBA description <amoeba_description>`

        **Example 1** ::
            
            import clusterpy
            instance = clusterpy.createGrid(33, 33)
            instance.generateData("Spots", 'rook', 1, 2, 0.7, 0.99)
            instance.cluster('amoeba', ['Spots1'],significance=0.01)
            instance.exportArcData("testOutput/amoeba_1_solution")


        .. image:: ../_static/AMOEBA1.png

        **Example 2**::

            import clusterpy
            instance = clusterpy.createGrid(25, 25)
            instance.generateData("Spots", 'rook', 1, 2, 0.7, 0.99)
            instance.cluster('amoeba', ['Spots1'],wType="queen",significance=0.01)
            instance.exportArcData("testOutput/amoeba_2_solution")


        **Example 3** ::

            import clusterpy
            calif = clusterpy.importArcData("clusterpy/data_examples/CA_Polygons")
            calif.dataOperation("g70_01 = float(POP2001 - POP1970) / POP1970")
            calif.cluster('amoeba', ['g70_01'],significance=0.01)
            calif.exportArcData("testOutput/amoeba_3_solution")


        .. image:: ../_static/AMOEBA3.png

        .. _som_examples:

        **Self Organizing Maps (SOM)**

        :ref:`SOM description <som_description>`

        **Example 1** ::

            import clusterpy
            instance = clusterpy.createGrid(33, 33)
            instance.generateData("SAR", "rook", 1, 0.9)
            instance.cluster("som", ["SAR1"], nRows=2,nCols=2)
            instance.exportArcData("testOutput/som_1_dataLayer")

        .. image:: ../_static/som1.png

        **Example 2** ::

            import clusterpy
            instance = clusterpy.createGrid(33,33)
            instance.generateData("SAR",'rook',1,0.9)
            instance.generateData("SAR",'rook',1,0.9)
            instance.cluster('som',['SAR1','SAR2'],nRows=2,nCols=2,alphaType='quadratic', fileName="testOutput/NeuronsLayer")
            instance.exportArcData("testOutput/som_2_dataLayer")


        **Example 3** ::

            import clusterpy
            calif = clusterpy.importArcData("clusterpy/data_examples/CA_Polygons")
            calif.dataOperation("g70_01 = float(POP2001 - POP1970) / POP1970")
            calif.cluster('som',['g70_01'],nRows=2,nCols=2,alphaType='linear')
            calif.exportArcData("testOutput/som_3_solution")


        .. image:: ../_static/som3.png

        .. _geosom_examples:

        **Geo Self Organizing Maps (geoSOM)**

        :ref:`GeoSOM description <geosom_description>`



        **Example 1** ::

            import clusterpy
            instance = clusterpy.createGrid(33, 33)
            instance.generateData("SAR", "rook", 1, 0.9)
            instance.cluster("geoSom", ["SAR1"], nRows=3,nCols=3)
            instance.exportArcData("testOutput/geoSom_1_dataLayer")


        .. image:: ../_static/geosom1.png

        **Example 2** ::
        
            import clusterpy
            instance = clusterpy.createGrid(33,33)
            instance.generateData("SAR",'rook',1,0.9)
            instance.generateData("SAR",'rook',1,0.9)
            instance.cluster('geoSom',['SAR1','SAR2'],nRows=3,nCols=3,alphaType='quadratic', fileName="testOutput/NeuronsLayer")
            instance.exportArcData("testOutput/geoSom_2_dataLayer")


        **Example 3** ::

            import clusterpy
            calif = clusterpy.importArcData("clusterpy/data_examples/CA_Polygons")
            calif.dataOperation("g70_01 = float(POP2001 - POP1970) / POP1970")
            calif.cluster('geoSom',['g70_01'],nRows=3,nCols=3,alphaType='linear')
            calif.exportArcData("testOutput/geoSom_3_solution")


        .. image:: ../_static/geosom3.png
        
        """
        self = args[0]
        algorithm = args[1]
        # Extracting W type from arguments
        if kargs.has_key('wType'):
            wType = kargs['wType']
            kargs.pop('wType')
        else:
            wType = 'rook'
        # Extracting W according to requirement
        if wType == 'rook':
            algorithmW = self.Wrook
        elif wType == 'queen':
            algorithmW = self.Wqueen
        else:
            algorithmW = self.Wrook
        # Extracting standardize variables
        if kargs.has_key('std'):
            std = kargs.pop('std')
        else:
            std = 0
        # Setting dissolve according to requirement
        if kargs.has_key("dissolve"):
            dissolve = kargs.pop('dissolve')
        else:
            dissolve = 0
        # Extracting dataOperations
        if kargs.has_key("dataOperations"):
            dataOperations = kargs.pop("dataOperations")
        else:
            dataOperations = {}
        # Construction of parameters per algorithm
        if algorithm in ["geoSom","amoeba","som"]:
            dissolve = 0
            dataOperations = {}
            print "The parameters ""dissolve"" and ""dataOperations"" is not available for the this \
algorithm" 

        #import pdb; pdb.set_trace()
        if algorithm == "geoSom":
            fieldNames = tuple(args[2])
            args = (self, fieldNames) + args[3:]
        else:
            fieldNames = tuple(args[2])
            algorithmY = self.getVars(*fieldNames)
            if std==1:
                for nn,name in enumerate(fieldNames):
                    values = [i[0] for i in self.getVars(name).values()]
                    mean_value = numpy.mean(values)
                    std_value = numpy.std(values)
                    newVar = fieldOperation("( " + name + " - " + str(mean_value) + ")/float(" + str(std_value) + ")", algorithmY, fieldNames)
                    for nv,val in enumerate(newVar):
                        algorithmY[nv][nn] = val
                # Adding original population to de algortihmY
                if algorithm == "maxpTabu":
                    population = fieldNames[-1]
                    populationY = self.getVars(population)
                    for key in populationY:
                        algorithmY[key][-1] = populationY[key][0]
            args = (algorithmY,algorithmW) + args[3:]
        name = algorithm + "_" +  time.strftime("%Y%m%d%H%M%S")
        self.outputCluster[name] = {
            "random": lambda *args, **kargs: execRandom(*args, **kargs),
            "azp": lambda *args, **kargs: execAZP(*args, **kargs),
            "arisel": lambda *args, **kargs: execArisel(*args, **kargs),
            "azpTabu": lambda *args, **kargs: execAZPTabu(*args, **kargs),
            "azpRTabu": lambda *args, **kargs: execAZPRTabu(*args, **kargs),
            "azpSa": lambda *args, **kargs: execAZPSA(*args, **kargs),
            "amoeba": lambda *args, **kargs: execAMOEBA(*args, **kargs),
            "som": lambda *args, **kargs: originalSOM(*args, **kargs),
            "geoSom": lambda *args, **kargs: geoSom(*args, **kargs),
            "pRegionsExact": lambda *args, **kargs: execPregionsExact(*args, **kargs),
            "maxpTabu": lambda *args, **kargs: execMaxpTabu(*args, **kargs)
        }[algorithm](*args, **kargs)
        self.outputCluster[name]["weightType"] = wType
        self.outputCluster[name]["aggregationVariables"] = fieldNames 
        self.outputCluster[name]["OS"] = os.name
        self.outputCluster[name]["proccesorArchitecture"] = os.getenv('PROCESSOR_ARCHITECTURE')
        self.outputCluster[name]["proccesorIdentifier"] = os.getenv('PROCESSOR_IDENTIFIER')
        self.outputCluster[name]["numberProccesor"] = os.getenv('NUMBER_OF_PROCESSORS')
        sol = self.outputCluster[name]["r2a"]
        self.region2areas = sol
        self.addVariable([name], sol)
        self.outputCluster[name]["fieldName"] = self.fieldNames[-1]
        if dissolve == 1:
            self.dissolveMap(dataOperations=dataOperations)

    def spmorph(self,variables,minShocks,maxShocks,
                        inequalityIndex,outFile,clusterAlgorithm,
                        nClusters, **kargs):
        """
            This function runs the algorithm spMorph, devised by
            [Duque_Ye_Folch2012], for a predefined shock. spMorph is an
            exploratory space-time analysis tool for describing processes of
            spatial redistribution of a given variable.  
            

            :keyword variables: List with variables to be analyzed. The variables must be chronologically sorted; e.g: ['Y1978', 'Y1979', 'Y1980', 'Y1981', 'Y1982', 'Y1983', 'Y1984', 'Y1985', 'Y1986', 'Y1987', 'Y1988'] 
            :type variables: list

            :keyword minShocks: minimum number of shocks to evaluate
            :type minShocks: integer

            :keyword maxShocks: maximum number of shocks to evaluate
            :type maxShocks: integer

            :keyword inequalityIndex: name of the inequality index to be utilized in the algorithm. By now, the only option is 'theil' 
            :type inequalityIndex: string

            :keyword outFile: Name for the output file; e.g.: "spMorph" (no extension)
            :type outFile: string 


            :keyword clusterAlgorithm: name of the spatial clustering algorithm to be utilized in the algorithm. The clustering algorithm must be any version of 'azp' or 'arisel'
            :type clusterAlgorithm: string

            :keyword nClusters: number of regions 
            :type nClusters: integer

            After the parameter nClusters you can include more parameters related with the clustering algorithm that you are using. We recomend not to use dissolve=1 option

            **Example 1**::
            import clusterpy
            china = clusterpy.importArcData("clusterpy/data_examples/china")
            variables = ['Y1978', 'Y1979', 'Y1980', 'Y1981']
            china.multishockFinder(variables,0,2,'theil',"sphmorph",'azpTabu',4)
        """
        def createTable(index,comb,shock):
            auxline = str(index)
            auxline = auxline.replace("[","")
            auxline = auxline.replace("]","")
            combtext = str(comb)
            combtext = combtext.replace(","," ")
            line = "".join([str(len(comb)),",",str(combtext),",",shock,",",auxline,",","\n"])
            return line
        bestSolutions = {}
        table_t = ""
        table_tw = ""
        table_tb = ""
        table_tw_t = ""
        table_lowerTw_t = ""
        table_a2r = ""
        auxline = str(variables)
        auxline = auxline.replace("[","")
        auxline = auxline.replace("]","")
        auxline = auxline.replace("'","")
        header = "".join(["#shocks,shocks,shock,",auxline,"\n"])
        auxline = str(range(len(self.areas)))
        auxline = auxline.replace("[","")
        auxline = auxline.replace("]","")
        header_a2r = "".join(["#shocks,shocks,shock,",auxline,"\n"])
        fout_t = open(outFile + "_t.csv","w")
        fout_t.write(header)
        fout_tb = open(outFile + "_tb.csv","w")
        fout_tb.write(header)
        fout_tw = open(outFile + "_tw.csv","w")
        fout_tw.write(header)
        fout_twt = open(outFile + "_twt.csv","w")
        fout_twt.write(header)
        fout_lb = open(outFile + "_lb.csv","w")
        fout_lb.write(header)
        fouta2r = open(outFile + "_a2r.csv","w")
        fouta2r.write(header_a2r)
        cachedSolutions = {}
        for nElements in range(minShocks,maxShocks+1):
            bestSol = [] # (t,tb,tw,tw/t,loweTw/t,comb,objectiveFunction)
            for comb in itertools.combinations(variables[1:],nElements):
                comb = list(comb)
                comb.sort()
                comb = tuple(comb)
                t, tb, tw, tw_t, lowerTw_t,a2r = self.inequalityShock(variables,
                    comb,inequalityIndex,clusterAlgorithm,nClusters,cachedSolutions,**kargs)
                if bestSol == [] or sum(lowerTw_t) <= (bestSol["of"]):
                    bestSol = {"t" : t,
                                "tb" : tb,
                                "tw" : tw,
                                "tw_t" : tw_t,
                                "lowerTw_t" : lowerTw_t,
                                "comb" : comb,
                                "of" : sum(lowerTw_t),
                                "a2r" : a2r}
            fout_t = open(outFile + "_t.csv","a")
            fout_tb = open(outFile + "_tb.csv","a")
            fout_tw = open(outFile + "_tw.csv","a")
            fout_twt = open(outFile + "_twt.csv","a")
            fout_lb = open(outFile + "_lb.csv","a")
            fouta2r = open(outFile + "_a2r.csv","a")
            for nc in range(nElements+1):
                line = createTable(bestSol["t"][nc],bestSol["comb"],str(nc))
                fout_t.write(line)
                line = createTable(bestSol["tb"][nc],bestSol["comb"],str(nc))
                fout_tb.write(line)
                line = createTable(bestSol["tw"][nc],bestSol["comb"],str(nc))
                fout_tw.write(line)
                line = createTable(bestSol["tw_t"][nc],bestSol["comb"],str(nc))
                fout_twt.write(line)
                line = createTable(bestSol["a2r"][nc],bestSol["comb"],str(nc))
                fouta2r.write(line)
            line = createTable(bestSol["lowerTw_t"],comb,"")
            fout_lb.write(line)
            fout_t.close()
            fout_tb.close()
            fout_tw.close()
            fout_twt.close()
            fout_lb.close()
            fouta2r.close()


    def inequalityShock(self,variables,shokVariables,
                        inequalityIndex,clusterAlgorithm,
                        nClusters,cachedSolutions,**kargs):
        """
            This function runs the algorithm spMorph, devised by
            [Duque_Ye_Folch2012], for a predefined shock. spMorph is an
            exploratory space-time analysis tool for describing processes of
            spatial redistribution of a given variable.  
            

            :keyword variables: List with variables to be analyzed. The variables must be chronologically sorted; e.g: ['Y1978', 'Y1979', 'Y1980', 'Y1981', 'Y1982', 'Y1983', 'Y1984', 'Y1985', 'Y1986', 'Y1987', 'Y1988'] 
            :type variables: list

            :keyword shokVariables: list with the name of the variable (in
            vars) in wich a shock ocurred. NOTE: the shock variable is
            included as the first variable of the next period; e.g: ['Y1981', 'Y1984'], this implies that the periods to analyze are: 1978-1980; 1981-1983 and 1984-1988.
            :type shokVariables: list

            :keyword inequalityIndex: name of the inequality index to be utilized in the algorithm. By now, the only option is 'theil' 
            :type inequalityIndex: string

            :keyword clusterAlgorithm: name of the spatial clustering algorithm to be utilized in the algorithm. The clustering algorithm must be any version of 'azp' or 'arisel'
            :type clusterAlgorithm: string

            :keyword nClusters: number of regions 
            :type nClusters: integer

            After the parameter nClusters you can include more parameters related with the clustering algorithm that you are using. We recomend not to use dissolve=1 option

            The function returns:

            t: total Theil

            tb: between groups inequality
            
            tw: within groups inequality
            
            lb: lower bound
            
            a2r: solution vector for the regionalization algorithm

            **Example**::
            import clusterpy
            china = clusterpy.importArcData("clusterpy/data_examples/china")
            variables = ['Y1978', 'Y1979', 'Y1980', 'Y1981', 'Y1982',
            'Y1983', 'Y1984', 'Y1985', 'Y1986', 'Y1987', 'Y1988',
            'Y1989', 'Y1990', 'Y1991', 'Y1992' , 'Y1993', 'Y1994',
            'Y1995', 'Y1996', 'Y1997', 'Y1998']
            shokVariable = ['Y1984']
            t,tb,tw,tw_t,lb,a2r=china.inequalityShock(variables,shokVariable,'theil',
            'arisel',5)
            

        """    
        tempSet = []
        area2regions = {}
        area2regionsList = []
        tempSetOrdered = []
        for var in variables:
            if var in shokVariables:
                if tempSet == []:
                    raise NameError("First period could not \
be a shock period")
                else:
                    tempSet.sort()
                    tempSet = tuple(tempSet)
                    if tempSet not in cachedSolutions:
                        clusterArgs = (clusterAlgorithm,tempSet,nClusters)
                        self.cluster(*clusterArgs,**kargs)
                        area2regions[tempSet] = self.region2areas
                        tempSetOrdered.append(tempSet)
                    else:
                        area2regions[tempSet] = cachedSolutions[tempSet][-1]
                        tempSetOrdered.append(tempSet)
                tempSet = [var]
            else:
                tempSet.append(var)
        tempSet.sort()
        tempSet = tuple(tempSet)
        if tempSet not in cachedSolutions:
            clusterArgs = (clusterAlgorithm,tempSet,nClusters)
            self.cluster(*clusterArgs,**kargs)
            area2regions[tempSet] = self.region2areas
            tempSetOrdered.append(tempSet)
        else:
            area2regions[tempSet] = cachedSolutions[tempSet][-1]
            tempSetOrdered.append(tempSet)
        Y = self.getVars(*variables)
        t = []
        tb = []
        tw = []
        tw_t = []
        for a2r in tempSetOrdered:
            if a2r in cachedSolutions:
                t2,tb2,tw2,tw_t2,a2rc = cachedSolutions[a2r]
            else:
                t2,tb2,tw2,tw_t2 = inequalityMultivar(Y,area2regions[a2r],inequalityIndex)
                cachedSolutions[a2r] = t2,tb2,tw2,tw_t2,area2regions[a2r]
                a2rc = area2regions[a2r]
            t.append(t2)
            tb.append(tb2)
            tw.append(tw2)
            tw_t.append(tw_t2)
            area2regionsList.append(a2rc)
        
        lowerTw_t = [min(x) for x in zip(*tw_t)]
        return t, tb, tw, tw_t, lowerTw_t,area2regionsList
            



    def inequality(*args,**kargs):
        """
            Documentacion Juank
        """
        self = args[0]
        algorithm = args[1]
        if algorithm == 'globalInequalityChanges':
            variables = args[2]
            outFile = args[3]
            Y = self.getVars(*variables)
            args = (Y,variables,outFile)
            globalInequalityChanges(*args,**kargs)
            result = None
        elif algorithm == 'inequality':
            variables = args[2]
            area2region = args[3]
            Y = self.getVars(*variables)
            area2region = [x[0] for x in self.getVars(area2region).values()]
            args = (Y,area2region)
            result = inequalityMultivar(*args,**kargs)
        elif algorithm == 'interregionalInequalityTest':
            fieldNames = args[2]
            area2region = args[3]
            outFile = args[4]
            Y = self.getVars(*fieldNames)
            area2regions = self.getVars(area2region)
            args = (Y,fieldNames,area2regions,area2region,outFile)
            result = interregionalInequalityTest(*args,**kargs)
        elif algorithm == 'regionsInequalityDifferenceTest':
            fieldNames = args[2]
            area2region = args[3]
            outFile = args[4]
            Y = self.getVars(*fieldNames)
            area2regions = self.getVars(area2region)
            area2regions = zip(*area2regions.values())
            args = (Y,fieldNames,area2regions,area2region,outFile)
            result = interregionalInequalityDifferences(*args,**kargs)
        return result

    def esda(*args, **kargs):
        """
            Documentacion Juank

        Exploratory spatial data analysis algorithms. For more information
        about the basic and the optional parameters, read the official 
        'algorithm documentation <www.rise-group.org>'

        :param args: basic paramters.
        :type args: tuple
        :param kargs: optional parameter keywords.
        :type kargs: dictionary

        **Examples** 
        
        Geographical association coefficient (GAC)
        
        >>> import clusterpy
        >>> new = clusterpy.createGrid(10, 10)
        >>> new.generateData("SAR", 'rook', 1, 0.9)
        >>> new.generateData("SAR", 'rook', 1, 0.9)
        >>> gac = new.esda("GAC", "SAR1", "SAR2")

        Redistribution coefficient

        >>> import clusterpy
        >>> new = clusterpy.createGrid(10, 10)
        >>> new.generateData("SAR", 'rook', 1, 0.9)
        >>> new.generateData("SAR", 'rook', 1, 0.9)
        >>> rdc = new.esda("RDC", "SAR1", "SAR2")
        
        Similarity coefficient

        >>> import clusterpy
        >>> new = clusterpy.createGrid(10, 10)
        >>> new.generateData("SAR", 'rook', 1, 0.9)
        >>> new.generateData("SAR", 'rook', 1, 0.9)
        >>> SIMC = new.esda("SIMC", "SAR1", "SAR2")
        """
        self = args[0]
        algorithm = args[1]
        args = [self] + list(args[2:])
        kargs = {}
        result = {
        "GAC": lambda *args, **kargs: geoAssociationCoef(*args, **kargs),
        "RDC": lambda *args, **kargs: redistributionCoef(*args, **kargs),
        "SIMC": lambda *args, **kargs: similarityCoef(*args, **kargs),
        }[algorithm](*args, **kargs)
        return result

    def exportArcData(self, filename):
        """
        Creates an ESRI shapefile from a clusterPy's layer.
        
        :param filename: shape file name to create, without ".shp"
        :type filename: string 

        **Examples** ::
        
            import clusterpy
            china = clusterpy.importArcData("clusterpy/data_examples/china")
            china.exportArcData("china")
        """
        print "Writing ESRI files"
        shpWriterDis(self.areas, filename, self.shpType)
        self.exportDBFY(filename)
        print "ESRI files created"

    def exportDBFY(self, fileName, *args):    
        """Exports the database file

        :param fileName: dbf file name to create, without ".dbf"
        :type fileName: string 
        :param args: variables subset to be exported
        :type args: tuple 

        **Examples** ::

            import clusterpy
            clusterpy.importArcData("clusterpy/data_examples/china")
            china.exportDBFY("china")
        """
        print "Writing DBF file"
        if args != ():
            Y = self.getVars(self, *args) 
            fieldNames = args
        else:
            Y = self.Y
            fieldNames = self.fieldNames
        fieldspecs = []
        types = Y[0] 
        for i in types:
            itype = str(type(i))
            if 'str' in itype:
                fieldspecs.append(('C', 10, 0))
            else:
                fieldspecs.append(('N', 10, 3))
        records = range(len(Y))
        for i in xrange(len(Y)):
            if len(fieldNames) == 2:
                records[i] = []
                records[i] = records[i] + Y.values()[i]
            else:
                records[i] = []
                records[i] = records[i] + Y.values()[i]
        dbfWriter(fieldNames, fieldspecs, records, fileName + '.dbf')
        print "Done"

    def exportCSVY(self, fileName, *args):
        """Exports layers data on .csv file

        :param fileName: csv file name to create, without ".csv"
        :type fileName: string 
        :param args: variables subset to be exported
        :type args: tuple 

        **Examples** ::

            import clusterpy
            china = clusterpy.importArcData("clusterpy/data_examples/china")
            china.exportCSVY("ChinaCSV")
        """
        print "Writing CSV files"
        if args != ():
            Y = self.getVars(self, *args) 
            fieldNames = args
        else:
            Y = self.Y
            fieldNames = self.fieldNames
        records = Y.values()
        csvWriter(fileName, fieldNames, records)
        print "Done"

    def exportGALW(self, fileName, wtype='rook', idVariable='ID'):
        """        
        Exports the contiguity W matrix on a gal file

        :param fileName: gal file name to create, without ".gal"
        :type fileName: string 
        :keyword wtype: w type to export, default is 'rook'
        :type wtype: string 
        :keyword idVariable: id variable fieldName, default is 'ID'
        :type idVariable: string  

        **Example 1**        
        Exporting rook matrix  ::

            import clusterpy
            china = clusterpy.importArcData("clusterpy/data_examples/china")
            china.exportGALW("chinaW", wtype='rook')

        **Example 2**        
        Exporting queen matrix  ::

            import clusterpy
            china = clusterpy.importArcData("clusterpy/data_examples/china")
            china.exportGALW("chinaW", wtype='queen')

        **Example 3**        
        Exporting queen matrix based on a variable different from ID  ::

            import clusterpy
            california = clusterpy.importArcData("clusterpy/data_examples/CA_Polygons")
            california.exportGALW("californiaW", wtype='queen',idVariable="MYID")

        **Example 3**        
        Exporting a customW matrix imported from a GWT file::

            import clusterpy
            china = clusterpy.importArcData("clusterpy/data_examples/china")
            china.customW = clusterpy.importGWT("clusterpy/data_examples/china_gwt_658.193052")
            china.exportGALW("chinaW", wtype='custom')
        """
        print "Writing GAL file"
        if wtype == 'rook':
            nw = self.Wrook
        elif wtype == 'queen':
            nw = self.Wqueen
        elif wtype == 'custom':
            nw = self.customW
        else:
            raise NameError("W type is not valid")
        idvar = self.getVars(idVariable)
        dict2gal(nw,idvar,fileName)

    def exportCSVW(self, fileName, wtype='rook', idVariable='ID', standarize=False):
        """
        Exports the nth contiguity W matrix on a csv file

        :param wDict: Contiguity dictionary 
        :type wDict: dictionary
        :param idVar: Data dictionary with the id field to be used
        :type idVar: dictionary
        :param fileName: gal file name to create, without ".gal"
        :type fileName: string 
        :keyword standarize: True to standardize the variables.
        :type standarize: boolean  

        **Examples 1**        
        Writing rook matrix to a csv ::

            import clusterpy
            china = clusterpy.importArcData("clusterpy/data_examples/china")
            china.exportCSVW("chinaW", wtype='rook')

        **Examples 2**        
        Writing rook matrix to a csv ::

            import clusterpy
            china = clusterpy.importArcData("clusterpy/data_examples/china")
            china.exportCSVW("chinaW", wtype='queen')

        """
        print "Writing CSV file"
        if wtype == 'rook':
            nw = copy.deepcopy(self.Wrook)
        elif wtype == 'queen':
            nw = copy.deepcopy(self.Wqueen)
        elif wtype == 'custom':
            nw = copy.deepcopy(self.customW)
        else:
            raise NameError("W type is not valid")
        w = copy.deepcopy(nw)
        idvar = self.getVars(idVariable)
        dict2csv(nw,idvar,fileName,standarize)

    def exportOutputs(self, filename):
        """Exports outputs of the last executed algorithm to a csv file. If no
        algorithm has been ran, you wil get an error message.

        :param filename: csv file name to create, without ".csv"
        :type filename: string 

        **Examples** ::

            import clusterpy
            china = clusterpy.importArcData("clusterpy/data_examples/china")
            china.cluster('geoSom', ['Y1991'], 10, 10, alphaType='quadratic', fileName="oLayer", dissolve=1)
            china.exportOutputs("outputs")
        """
        f = open(filename, 'w')
        #try:
        print "Writing outputs to the CSV"
        key0 = 'none'
        cont = 0
        while key0 == 'none' or key0 == "r2aRoot" or key0 == "r2a":
            key0 = self.outputCluster.keys()[cont]
            cont += 1
        headers = self.outputCluster[key0].keys()
        line = ''
        for header in headers:
            line +=  header + ';'
        f.write(line[0: -1] + '\n')
        for key in self.outputCluster.keys():
            line = ''
            for header in headers:
                if (key != 'r2a' and key != 'r2aRoot'):
                    line += str(self.outputCluster[key][header]) + ';'  
            f.write(line[0: -1] + '\n')
        print "Outputs successfully exported"
        #except:
        #    raise NameError("No algorithm has been run")
        f.close()


    def exportRegions2area(self, filename):
        """export region2area results

        :param filename: csv file name to create, without ".csv"
        :type filename: string 

        **Examples** ::

            import clusterpy
            china = clusterpy.importArcData("clusterpy/data_examples/china")
            china.exportRegions2area('region2area')
        """
        print "Writing region2areas"
        f = open(filename, 'w')
        data = self.getVars(self.outputCluster.keys())
        for area in data.keys():
            line = str(area) + ';'
            regions = data[area]
            for region in regions:
                line += str(region) + ';'  
            f.write(line[0: -1] + '\n')
        f.close()
        print "region2areas successfully saved"

    def transport(self, xoffset, yoffset):
        """
        This function transports all the coordinates of a layer object on the 
        given offsets.

        :param xoffset: length of the translation to be made on the x coordinates
        :type xoffset: float
        :param yoffset: length of the translation to be made on the y coordinates
        :type yoffset: float

        **Examples** ::

            import clusterpy
            clusterpy.importArcData("clusterpy/data_examples/china")
            china.transport(100, 100)
        """
        print "Changing coordinates"
        transportLayer(self, xoffset, yoffset)
        print "Done"
        
    def expand(self, xproportion, yproportion):
        """
        This function scales the layer width and height according to inputs 
        proportions  

        :param xproportion: proportion to scale x
        :type xproportion: float
        :param yproportion: proportion to scale y
        :type yproportion: float
        
        **Example** ::

            import clusterpy
            china = clusterpy.importArcData("clusterpy/data_examples/china")
            china.expand(100, 100)
        """
        print "Changing coordinates"
        expandLayer(self, xproportion, yproportion)
        print "Done"

    def getGeometricAreas(self):
        """
        This function calculates the geometric area for the polygons of
        a map and returns it as a dictionary.

        For computational efficiency it's recommended to store the results
        on the layer database using the addVariable layer function.
        
        **Example** ::

            import clusterpy
            china = clusterpy.importArcData("clusterpy/data_examples/china")
            china.getGeometricAreas()
        """
        return getGeometricAreas(self)

    def getCentroids(self):
        """Centroid calculation

        This function calculates the centroids for the polygons of
        a map and returns it as a dictionary with the
        coordinates of each area.

        For computational efficiency it's recommended to store the results
        on the layer database using the addVariable layer function.
        
        **Example** ::

            import clusterpy
            china = clusterpy.importArcData("clusterpy/data_examples/china")
            china.getCentroids()
        """
        return getCentroids(self)
        
    def getBbox(self):
        """
        this function returns the boundingbox of the layer layer object.

        **Example** ::
        
            import clusterpy
            china = clusterpy.importArcData("clusterpy/data_examples/china")
            china.getBbox()
        """

        if self.bbox == []:
            self.bbox = getBbox(self)
        return self.bbox


    def _defBbox(self):
        if self.bbox == []:
            self.bbox = getBbox(self)

    def topoStats(self,regular=False):
        if self.tStats == []:
            self.nWrook = noFrontiersW(self.Wrook,self.Wqueen,self.areas)
            M_n, m_n, mu1, mu2, a1, s, eig = topoStatistics(self.Wrook,self.nWrook,regular=regular)
            self.tStats = [M_n,m_n,mu1,mu2,a1,s,eig]
        return self.tStats
