# encoding: latin2
"""P-regions
"""
__author__ = "Juan C. Duque"
__credits__ = "Copyright (c) 2009-11 Juan C. Duque"
__license__ = "New BSD License"
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
import numpy as nm
try:
    from gurobipy import *
except ImportError:
    pass
import time as tm

from toolboxes.cluster.componentsAlg.distanceFunctions import distanceA2AEuclideanSquared


__all__ = ['execMinpOrder']


def execMinpOrder(y, w, threshold=1, conseq='none'):
	"""Min-p-regions model (Order formulation)

	The min-p-regions model, devised by [Duque_...2014]_ ,
	clusters a set of geographic areas into the minimum number of homogeneous
	regions such that the value of a spatially extensive regional attribute is
	above a predefined threshold value. In clusterPy we measure heterogeneity as
	the within-cluster sum of squares from each area to the attribute centroid
	of its cluster. ::   
	
		layer.cluster('minpOrder',vars,<threshold>,<wType>,<std>,<dissolve>,<dataOperations>)

	:keyword vars: Area attribute(s) (e.g. ['SAR1','SAR2','POP'])  
	:type vars: list
    :keyword threshold: Minimum value of the constrained variable at regional level. Default value threshold = 100.
    :type threshold: integer
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
	'mode','range','first','last','numberOfAreas. By default just 
	ID variable is added to the dissolved map."""

	print "Running min-p-regions model (Duque 2014)"
	print "Order formulation"
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

	z = {}
	l = {} #spatially extensive attribute
	for i in numA:
		z[i] = y[i][0]
		l[i] = y[i][1]
		
		
		
	d = nm.zeros(shape = (n,n))
	for i in numA:
		for j in numA:
			d[i,j]=distanceA2AEuclideanSquared([[z[i]],[z[j]]])[0][0]

		
	# h: scaling factor
	temp = 0
	for i in numA:
		for j in numA:
			if i<j:
				temp += d[i][j]
	h = 1+ nm.floor(nm.log(temp))


	#-----------------------------------
	try: 
	# Create the new model
		m=Model("maxpRegions")
		
		#tol=1e-5

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
		temp1 = []
		temp2 = []
		for i in numA:
			# Number of regions
			for k in numA:
				temp1.append(x[i][k][0])
			# Total heterogeneity
			for j in numA:
				temp2.append(d[i][j]*t[i][j])

		m.setObjective((10**float(h))*quicksum(temp1)+quicksum(temp2), GRB.MINIMIZE)

		# Constraints 1
		for k in numA:
			temp = []
			for i in numA:
				temp.append(x[i][k][0])
			m.addConstr(quicksum(temp)<=1,"c1_"+str([k,0]))
			
			
		# Constraints 2		
		for i in numA:
			temp = []
			for k in numA:
				for c in numO:
					temp.append(x[i][k][c]) #+= x[i][k][c]
			m.addConstr(quicksum(temp) == 1,"c2_"+str([i]))
			#m.addConstr(quicksum(temp) >= 1-tol,"c2_"+str([i]))
			
		# Constraints 3		
		for i in numA:
			for k in numA:
				for c in range(1,q):
					temp = []
					for j in w[i]:
						temp.append(x[j][k][c-1])
					#m.addConstr(x[i][k][c]-quicksum(temp) <= tol,"c3_"+str([i,k,c]))
					m.addConstr(x[i][k][c]-quicksum(temp) <= 0,"c3_"+str([i,k,c]))
		
		# Constraints 4
		for i in numA:
			for j in numA:
				if i!=j:
					for k in numA:
						temp = []
						for c in numO:
							temp.append(x[i][k][c]+x[j][k][c])
						#m.addConstr(quicksum(temp)-t[i][j]-t[j][i]-1 <= tol,"c4_"+str([i,j,k]))				
						m.addConstr(quicksum(temp)-t[i][j]-t[j][i]-1 <= 0,"c4_"+str([i,j,k]))				

		# Constraints 5
		for i in numA:
			for j in numA:
				m.addConstr(t[i][j]+t[j][i]<= 1,"c5_"+str([i,j]))

		# Constraints 6
		for i in numA:
			for j in numA:
				m.addConstr(t[i][j]*(l[i]-l[j])>= 0,"c6_"+str([i,j]))

		# Constraints 7
		for i in numA:
			for j in numA:
				m.addConstr(t[i][j]*threshold>= t[i][j]*(l[i]-l[j]),"c7_"+str([i,j]))	
		
		
		m.update()

		#To reduce memory use
		m.setParam('Nodefilestart',0.1)
		#m.setParam('OutputFlag',False)
		#m.setParam('IntFeasTol', tol)
		m.setParam('LogFile', 'minpO-'+str(conseq)+'-'+str(n)+'-'+str(threshold))
		m.params.timeLimit = 10800#1800
			

		m.optimize()
		 
		time = tm.time()-start

		sol = [0 for u in numA]
		
		reg= []
		for i in numA:
			for k in numA:
				for c in numO:
					if x[i][k][c].x==1:
						#if the region cannot be found
						if reg.count(k)==0:
							reg.append(k)
		p=len(reg)
		
			
		for v in m.getVars():
			if v.x >0:
				print v.varName, v.x
				
		#import pdb; pdb.set_trace()
		  
		#print "p:", regID
		#print 'FINAL SOLUTION:', sol
		#print 'FINAL OF:', m.objVal
		#print "running time", time
		output = { "objectiveFunction": m.objVal,
			"bestBound": m.objBound,
			"running time": time,
			"algorithm": "minpOrder",
			"regions" : 'none',#len(sol),
			"r2a": 'none',#sol,
			"p": p,
			"distanceType" :  "EuclideanSquared",
			"distanceStat" : "None",
			"selectionType" : "None",
			"ObjectiveFunctionType" : "None"} 
		print "Done"
		return output
				
	except GurobiError:
		print 'Error reported'



