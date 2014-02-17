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

import numpy as nm
try:
    from gurobipy import *
except ImportError:
    pass
import time as tm
from toolboxes.cluster.componentsAlg.distanceFunctions import distanceA2AEuclideanSquared


__all__ = ['execPregionsExact']


def execPregionsExact(y, w, p=2,rho='none', inst='none', conseq='none'):

    #EXPLICAR QUÉ ES EL P-REGIONS
    """P-regions model

    The p-regions model, devised by [Duque_Church_Middleton2009]_, 
	clusters a set of geographic areas into p spatially contiguous 
	regions while minimizing within cluster heterogeneity.
    In Clusterpy, the p-regions model is formulated as a mixed 
	integer-programming (MIP) problem and solved using the 
	Gurobi optimizer. ::
	
    #CÓMO CORRERLO layer.cluster(...)
		layer.cluster('pRegionsExact',vars,<p>,<wType>,<std>,<dissolve>,<dataOperations>)

    :keyword vars: Area attribute(s) (e.g. ['SAR1','SAR2','POP'])  
    :type vars: list
    :keyword p: Number of spatially contiguous regions to be generated. Default value p = 2.
	:type p: integer
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

    # print "Running p-regions model  (Duque, Church and Middleton, 2009)"
    # print "Number of areas: ", len(y) 
    # print "Number of regions: ", p, "\n"
	#import pdb; pdb.set_trace()
    start = tm.time()

	# PARAMETERS
	
    # Number of areas
    n = len(y)
    l=n-p

    # Area iterator
    numA = range(n)

    d={}
    temp=range(n-1)
    for i in temp:
        list1=[]
    	for j in numA:
            if i<j:
                list1.append(distanceA2AEuclideanSquared([y[i],y[j]])[0][0])
        d[i]=list1

#-----------------------------------
    try: 
	
		# CONSTRUCTION OF THE MODEL
		
		# Tolerance to non-integer solutions
		tol = 1e-5 #min value: 1e-9
				
	
		# Create the new model
		m=Model("pRegions")

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

		# x_ij
		# 1 if arc between adjacent areas i and j is selected for a tree graph
		# 0 otherwise
		x = []
		for i in numA:
			x_i=[]
			for j in numA:
				x_i.append(m.addVar(vtype=GRB.BINARY,name="x_"+str([i,j])))
			x.append(x_i)
			
		# u_i
		# Order assigned to each area i in a tree
		u = []
		for i in numA:
			#u.append(m.addVar(lb=1-tol, ub=n-p-tol, vtype=GRB.INTEGER,name="u_"+str(i)))
			u.append(m.addVar(lb=1, vtype=GRB.INTEGER,name="u_"+str(i)))

			  
		# Integrate new variables
		m.update()
	
		# Objective function

		of=0
		for i in numA:
			for j in range(i+1,n):
				of+=t[i][j]*d[i][j-i-1]
	
		m.setObjective(of, GRB.MINIMIZE)

		# Constraints 1, 5, 6
		temp = 0
		for i in numA:
			for j in w[i]:
				temp += x[i][j]
				#m.addConstr(x[i][j]-t[i][j]<=tol,"c5_"+str([i,j]))
				m.addConstr(x[i][j]-t[i][j]<=0,"c5_"+str([i,j]))
				#m.addConstr(u[i]-u[j]+(n-p)*x[i][j]+(n-p-2)*x[j][i]<=(l-tol-1),"c6_"+str([i,j]))
				m.addConstr(u[i]-u[j]+(n-p)*x[i][j]+(n-p-2)*x[j][i]<=(l-1),"c6_"+str([i,j]))
 		
		#m.addConstr(temp == l-tol,"c1")
		m.addConstr(temp == l,"c1")

		# Constraint 2
		i = 0
		for x_i in x:
			temp =[]
			for j in w[i]:
				temp.append(x_i[j])
			#m.addConstr(quicksum(temp) <=1-tol, "c2_"+str(i))
			m.addConstr(quicksum(temp) <=1, "c2_"+str(i))
			i += 1

		# Constraints 3, 4
		for i in numA:
			for j in numA:
				if i!=j:
					#m.addConstr(t[i][j]-t[j][i]<=tol,"c4_"+str([i,j]))
					m.addConstr(t[i][j]-t[j][i]==0,"c4_"+str([i,j]))
					for em in numA:
						if em!=j:
							#m.addConstr(t[i][j]+t[i][em]-t[j][em]<=1-tol,"c3_"+str([i,j,em]))
							m.addConstr(t[i][j]+t[i][em]-t[j][em]<=1,"c3_"+str([i,j,em]))
		
		
		#Constraint REDUNDANTE
		for i in numA:
			for j in numA:
				if i!=j:	
					m.addConstr(x[i][j]+x[j][i]<=1,"c3_"+str([i,j,em]))
		
		m.update()

					
		#Writes the .lp file format of the model
		#m.write("test.lp")
		#To reduce memory use
		#m.setParam('Threads',1)
		# To disable optimization output
		#m.setParam('OutputFlag',False)
		#m.setParam('ScaleFlag',0)
		# To set the tolerance to non-integer solutions
		m.setParam('IntFeasTol', tol)
		m.setParam('LogFile', 'E-'+str(conseq)+'-'+str(n)+'-'+str(p)+'-'+str(rho)+'-'+str(inst))
		m.params.timeLimit = 1800
		m.optimize()
		
		#do IIS
		# print 'The model is infeasible; computing IIS'
		# m.computeIIS()
		# print '\nThe following constraint(s) cannot be satisfied:'
		# for c in m.getConstrs():
			# if c.IISConstr:
				# print c.constrName
			   
		time = tm.time()-start
   				
		# for v in m.getVars():
			# if v.x >0:
				# print v.varName, v.x
		  		
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
		
		# print 'FINAL SOLUTION:', sol
		# print 'FINAL OF:', m.objVal
		# print 'FINAL bound:', m.objBound
		# print 'GAP:', m.MIPGap
		# print "running time", time
		output = { "objectiveFunction": m.objVal,
			"bestBound": m.objBound,
			"running time": time,
			"algorithm": "pRegionsExact",
			#"regions" : len(sol),
			"r2a": "None",#sol,
			"distanceType" :  "EuclideanSquared",
			"distanceStat" : "None",
			"selectionType" : "None",
			"ObjectiveFunctionType" : "None"} 
		print "Done"
		return output
                
    except GurobiError:
        print 'Error reported'
		




		
	
    

