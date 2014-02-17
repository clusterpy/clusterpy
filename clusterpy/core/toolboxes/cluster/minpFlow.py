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
import numpy as nm
try:
    from gurobipy import *
except ImportError:
    pass
import time as tm

from toolboxes.cluster.componentsAlg.distanceFunctions import distanceA2AEuclideanSquared


__all__ = ['execMinpFlow']


def execMinpFlow(y, w, threshold=1, conseq='none'):
	"""Min-p-regions model (Flow formulation)

	The min-p-regions model, devised by [Duque_...2014]_ ,
	clusters a set of geographic areas into the minimum number of homogeneous
	regions such that the value of a spatially extensive regional attribute is
	above a predefined threshold value. In clusterPy we measure heterogeneity as
	the within-cluster sum of squares from each area to the attribute centroid
	of its cluster.  ::
	
		layer.cluster('minpFlow',vars,<threshold>,<wType>,<std>,<dissolve>,<dataOperations>)

	:keyword vars: Area attribute(s) (e.g. ['SAR1','SAR2','POP'])  
	:type vars: list
    :keyword threshold: Minimum value of the constrained variable at regional level. Default value threshold = 100.
    :type threshold: integer
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
	'mode','range','first','last','numberOfAreas. By default just
	ID variable is added to the dissolved map.
	"""

	print "Running max-p-regions model (Duque, Anselin and Rey, 2010)"
	print "Exact method"
	print "Number of areas: ", len(y) 
	print "threshold value: ", threshold
	
	start = tm.time()

	# Number of areas
	n = len(y)

	# Area iterator
	numA = range(n)
	
	Wr=w
	
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

		# Create variables

		# t_ij
		# 1 if areas i and j belongs to the same region
		# 0 otherwise
		# t = []
		# for i in numA:
			# t_i = []
			# for j in numA:
				# t_i.append(m.addVar(vtype=GRB.BINARY,name="t_"+str([i,j])))
			# t.append(t_i)
		t={(i,j):m.addVar(vtype=GRB.BINARY,name="t_"+str([i,j])) for i in numA for j in numA if i!=j}
		
		# f_ijk
		# amount of flow from area i to j in region k
		f={(i,j,k):m.addVar(vtype=GRB.SEMICONT,name="f_"+str([i,j,k])) for i in numA for j in Wr[i] for k in numA}
		# f = []
		# for i in numA:
			# f_i=[]
			# for j in Wr[i]: 
				# f_ij=[]
				# for k in numA:
					# f_ij.append(m.addVar(vtype=GRB.SEMICONT,name="f_"+str([i,j,k])))
				# f_i.append(f_ij)
			# f.append(f_i)
			
		# y_ik
		# 1 if areas i included in region k
		# 0 otherwise
		y = []
		for i in numA:
			y_i = []
			for k in numA:
				y_i.append(m.addVar(vtype=GRB.BINARY,name="y_"+str([i,k])))
			y.append(y_i)

		# w_ik
		# 1 if areas i is chosen as a sink
		# 0 otherwise
		w = []
		for i in numA:
			w_i = []
			for k in numA:
				w_i.append(m.addVar(vtype=GRB.BINARY,name="w_"+str([i,k])))
			w.append(w_i)
			  
		# Integrate new variables
		m.update()

		# Objective function

		temp1 = []
		temp2 = []
		for i in numA:
			# Number of regions
			for k in numA:
				temp1.append(w[i][k])
			# Total heterogeneity
			for j in numA:
				if i!=j:
					temp2.append(d[i][j]*t[i,j])

		m.setObjective((10**float(h))*quicksum(temp1)+quicksum(temp2), GRB.MINIMIZE)

		# Constraints 1
		for i in numA:
			temp = []
			for k in numA:
				temp.append(y[i][k])
			m.addConstr(quicksum(temp)==1,"c1_"+str([i]))
			
		# m.addConstr(w[4][0]==1)
		# m.addConstr(f[3][4][0]==1)
					
		# Constraints 2		
		for i in numA:
			for k in numA:
				m.addConstr(w[i][k]<=y[i][k],"c2_"+str([i,k]))
			
		# Constraints 3		
		for k in numA:
			temp = []
			for i in numA:
				temp.append(w[i][k])
			m.addConstr(quicksum(temp) <= 1,"c3_"+str([k]))

		# Constraints 4, 5
		for k in numA:
			for i in numA:
				for j in Wr[i]:
					m.addConstr(f[i,j,k]<=y[i][k]*n,"c4_"+str([i,j,k]))
					m.addConstr(f[i,j,k]<=y[j][k]*n,"c5_"+str([i,j,k]))
		
		# Constraints 6 
		for k in numA:
			temp1 = []
			temp2 = []
			for i in numA:
				temp1.append(w[i][k])
				for j in Wr[i]:
					temp2.append(f[i,j,k])
			m.addConstr(quicksum(temp2)<=quicksum(temp1)*(n*1.0/2)*(n+1),"c6_"+str([k]))				


		# Constraints 7
		for i in numA:
			for k in numA:
				temp1=[]
				temp2 = []
				for j in Wr[i]:
					temp1.append(f[i,j,k])
					temp2.append(f[j,i,k])
					#temp1.append(f[i][j][k])
					#temp2.append(f[j][i][k])
				m.addConstr(y[i][k]-n*w[i][k]-quicksum(temp1)+quicksum(temp2)<=0 ,"c7_"+str([i,k]))				

		# Constraints 8
		for i in numA:
			for j in numA:
				if i!=j:
					for k in numA:
						m.addConstr(y[i][k]+y[j][k]-1-t[i,j]-t[j,i]<=0,"c8_"+str([i,j,k]))	
		
		# Constraints 9
		for i in numA:
			for j in numA:
				if i!=j:
					m.addConstr(-t[i,j]*(l[i]-l[j])<=0,"c9_"+str([i,j]))	
			
		# Constraints 10
		for i in numA:
			for j in numA:
				if i!=j:
					m.addConstr(t[i,j]*(l[i]-l[j])-t[i,j]*threshold<=0,"c10_"+str([i,j]))
		
		m.update()


		#To reduce memory use
		m.setParam('Nodefilestart',0.1)
		#m.setParam('OutputFlag',False)
		m.params.timeLimit = 10800#1800
		m.setParam('LogFile', 'minpF-'+str(conseq)+'-'+str(n)+'-'+str(threshold))
		
		
		m.optimize()
		   
		time = tm.time()-start
		

		reg= []
		for i in numA:
			for k in numA:
				if y[i][k].x==1:
					#if the region cannot be found
					if reg.count(k)==0:
						reg.append(k)
		p=len(reg)
		
		
		for v in m.getVars():
			if v.x >0:
				print v.varName, v.x

				
		#print "p:", regID
		#print 'FINAL SOLUTION:', sol
		# print 'FINAL OF:', m.objVal
		# print "running time", time
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



