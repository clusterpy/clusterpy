# encoding: latin2
"""P-regions
"""
__author__ = "Juan C. Duque"
__credits__ = "Copyright (c) 2009-11 Juan C. Duque"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"

#import copy
#import numpy
#import time as tm
#from componentsAlg import AreaManager
#from componentsAlg import BasicMemory
#from componentsAlg import RegionMaker

#QUITAR
#import clusterpy
import numpy as nm
from gurobipy import *
import time as tm

from componentsAlg.distanceFunctions import distanceA2AEuclideanSquared


#__all__ = ['execMaxpExact']


#def execPregionsExact(y, w, p, vars):
#threshold
#def execMaxpExact(y, w, threshold=100.0):

#EXPLICAR QUÉ ES EL maxP-REGIONS
"""Max-p-regions model (Tabu) 

The max-p-regions model, devised by [Duque_Anselin_Rey2010]_ ,
clusters a set of geographic areas into the maximum number of homogeneous
regions such that the value of a spatially extensive regional attribute is
above a predefined threshold value. In clusterPy we measure heterogeneity as
the within-cluster sum of squares from each area to the attribute centroid
of its cluster.    #CÓMO CORRERLO layer.cluster(...)
layer.cluster('pRegionsExact',vars,p=2,<wType>,<std>,<dissolve>,<dataOperations>)

:keyword vars: Area attribute(s) (e.g. ['SAR1','SAR2','POP'])  
:type vars: list
:keyword p: Number of spatially contiguous regions to be generated. Default value p = 2.
:keyword wType: Type of first-order contiguity-based spatial matrix: 'rook' or 'queen'. Default value wType = 'rook'. 
:type wType: string
:keyword std: If = 1, then the variables will be standardized.
:type std: binary
:keyword dissolve: If = 1, then you will get a "child" instance of the layer that contains the new regions. Default value = 0. Note: Each child layer is saved in the attribute layer.results. The first algorithm that you run with dissolve=1 will have a child layer in layer.results[0]; the second algorithm that you run with dissolve=1 will be in layer.results[1], and so on. You can export a child as a shapefile with layer.result[<1,2,3..>].exportArcData('filename')
:type dissolve: binary
:keyword dataOperations: Dictionary which maps a variable to a list of operations to run on it. The dissolved layer will contains in it's data all the variables specified in this dictionary. Be sure to check the input layer's fieldNames before use this utility.
:type dataOperations: dictionary

The dictionary structure must be as showed bellow.

>>> X = {}
>>> X[variableName1] = [function1, function2,....]
>>> X[variableName2] = [function1, function2,....]

Where functions are strings which represents the name of the 
functions to be used on the given variableName. Functions 
could be,'sum','mean','min','max','meanDesv','stdDesv','med',
'mode','range','first','last','numberOfAreas. By deffault just
ID variable is added to the dissolved map.
"""

# Create grid of 3x3
lay = clusterpy.createGrid(3,3)#(3,3)

# Generate var from SAR
lay.generateData("SAR","rook",1,0.7)
lay.generateData('Uniform', 'rook', 1, 10, 15)


# y OJO USAR SOLO ATRIBUTOS QUE SON
var = lay.getVars(["SAR1"])

# Threshold
threshold = 130
# Spatially extensive attribute value of area i
l = lay.getVars(["Uniform2"])

# "N_i", Set of areas adjacent to area i --> AS A DICTIONARY
w = lay.Wrook

# Layer info
y = lay.Y

print "Running max-p-regions model (Duque, Anselin and Rey, 2010)"
print "Exact method"
print "Number of areas: ", len(y) 
print "threshold value: ", threshold

    
start = tm.time()

# Number of areas
n = len(y)
q = n-1

# Area iterator
numA = range(n)
# Order iterator
numO = range(q)

d={}
temp=range(n-1)
for i in temp:
	list1=[]
	for j in numA:
		if i<j:
			#list1.append(distanceA2AEuclideanSquared([y[i],y[j]])[0][0])
			list1.append(distanceA2AEuclideanSquared([vars[i],vars[j]])[0][0])
	d[i]=list1
	
# h: scaling factor
temp = 0
for i in numA:
	for j in numA:
		if i<j:
			temp += d[i][j]
h = 1+ floor(log(temp))


#-----------------------------------
try: 
# Create the new model
	m=Model("maxpRegions")

	# Create variables

	# t_ij
	# 1 if areas i and j belongs to the same region
	# 0 otherwise
	t = []
	for i in numA:
		t_i = []
		for j in numA:
			t_i.append(m.addVar(vtype=GRB.BINARY,name="t_"+str([i,j])))
		t.append(t_i)

	# x_ikc
	# 1 if area i is assigned to region k in order c
	# 0 otherwise
	x = []
	for i in numA:
		x_i=[]
		for k in numA:
			x_ik=[]
			for c in numO:
				x_ik.append(m.addVar(vtype=GRB.BINARY,name="x_"+str([i,k,c])))
			x_i.append(x_ik)
		x.append(x_i)
		  
	# Integrate new variables
	m.update()

	# Objective function

	of=0
	temp1 = 0
	temp2 = 0
	for i in numA:
		# Number of regions
		for k in numA:
			temp1 += x[i][k][0]
		# Total heterogeneity
		for j in range(i+1,n):
			temp2 += t[i][j]*d[i][j-i-1]

	m.setObjective(temp1*(10**h)+temp2, GRB.MINIMIZE)

	# Constraints 1
	for k in numA:
		temp = 0
		for i in numA:
			temp += x[i][k][0]
		m.addConstr(temp<=1,"c1_"+str([k,0]))
		
		
	# Constraints 2		
	for i in numA:
		temp = []
		for k in numA:
			for c in numO:
				temp.append(x[i][k][c]) #+= x[i][k][c]
		m.addConstr(quicksum(temp) == 1,"c2_"+str([i]))
		
	# Constraints 3		
	for i in numA:
		for k in numA:
			for c in numO:
				temp = []
				for j in w[i]:
					temp.append(x[j][k][c-1])
				m.addConstr(x[i][k][c]-quicksum(temp) <= 0,"c3_"+str([i,k,c]))
	
	# Constraints 4
	for i in numA:
		for j in numA:
			for k in numA:
				temp = []
				for c in numO:
					temp.append(x[i][k][c]+x[j][k][c])
				m.addConstr(quicksum(temp) - t[i][j] -1 <= 0,"c4_"+str([i,j,k]))				

	# Constraints 5
	for i in numA:
		for j in numA:
			m.addConstr(t[i][j]*(l[i]-l[j])>= 0,"c5_"+str([i,j]))				

	# Constraints 6
	for i in numA:
		for j in numA:
			m.addConstr(t[i][j]*threshold>= t[i][j]*(l[i]-l[j]),"c6_"+str([i,j]))	
							
	m.update()

	#Writes the .lp file format of the model
	m.write("test.lp")

	#To reduce memory use
	#import pdb; pdb.set_trace()
	m.setParam('Nodefilestart',0.1)
	#m.setParam('OutputFlag',False)

	m.optimize()
   
	time = tm.time()-start

	# sol = [0 for k in numA]
	# num = list(numA)
	# regID=0 #Number of region
	# while num:
		# area = num[0]
		# sol[area]=regID
		# f = num.remove(area)
		# for j in numA:
			# if t[area][j].x>=1-tol:#==1:
				# sol[j] = regID
				# if num.count(j)!=0:
					# b = num.remove(j)
		# regID += 1
		
	for v in m.getVars():
		if v.x >0:
			print v.varName, v.x
	  
	#print "p:", regID
	#print 'FINAL SOLUTION:', sol
	print 'FINAL OF:', m.objVal
	print "running time", time
	# output = { "objectiveFunction": m.objVal,
		# "running time": time,
		# "algorithm": "pRegionsExact",
		# "regions" : len(sol),
		# "r2a": sol,
		# "distanceType" :  "EuclideanSquared",
		# "distanceStat" : "None",
		# "selectionType" : "None",
		# "ObjectiveFunctionType" : "None"} 
	# print "Done"
	# return output
			
except GurobiError:
	print 'Error reported'



