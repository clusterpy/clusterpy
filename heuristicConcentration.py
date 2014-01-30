import clusterpy
import sys
from operator import itemgetter
import numpy as nm
import time as tm
from gurobipy import *

from toolboxes.cluster.componentsAlg.distanceFunctions import distanceA2AEuclideanSquared

#create layer
# rho = [0.9,0.5,0.2]
# for r in rho:
	# for j in range(1,11):
		# lay = clusterpy.createGrid(5,5)
		# lay.generateData("SAR","rook",1,r)	
		# lay.exportArcData("hc"+str(5*5)+"-"+str(r)+"-"+str(j))
		
# numReg = [3, 5, 7]
# numRho = [0.2, 0.5, 0.9]
#import itertools
#exp=list(itertools.product(numRho, numReg, range(1,11)))

conseq = int(sys.argv[1])

exp=[(0.2, 3, 1), (0.2, 3, 2), (0.2, 3, 3), (0.2, 3, 4), (0.2, 3, 5),
 (0.2, 3, 6), (0.2, 3, 7), (0.2, 3, 8), (0.2, 3, 9), (0.2, 3, 10),
 (0.2, 5, 1), (0.2, 5, 2), (0.2, 5, 3), (0.2, 5, 4), (0.2, 5, 5), 
 (0.2, 5, 6), (0.2, 5, 7), (0.2, 5, 8), (0.2, 5, 9), (0.2, 5, 10),
 (0.2, 7, 1), (0.2, 7, 2), (0.2, 7, 3), (0.2, 7, 4), (0.2, 7, 5),
 (0.2, 7, 6), (0.2, 7, 7), (0.2, 7, 8), (0.2, 7, 9), (0.2, 7, 10),
 (0.5, 3, 1), (0.5, 3, 2), (0.5, 3, 3), (0.5, 3, 4), (0.5, 3, 5), 
 (0.5, 3, 6), (0.5, 3, 7), (0.5, 3, 8), (0.5, 3, 9), (0.5, 3, 10),
 (0.5, 5, 1), (0.5, 5, 2), (0.5, 5, 3), (0.5, 5, 4), (0.5, 5, 5), 
 (0.5, 5, 6), (0.5, 5, 7), (0.5, 5, 8), (0.5, 5, 9), (0.5, 5, 10), 
 (0.5, 7, 1), (0.5, 7, 2), (0.5, 7, 3), (0.5, 7, 4), (0.5, 7, 5), (0.5, 7, 6),
 (0.5, 7, 7), (0.5, 7, 8), (0.5, 7, 9), (0.5, 7, 10), (0.9, 3, 1), (0.9, 3, 2),
 (0.9, 3, 3), (0.9, 3, 4), (0.9, 3, 5), (0.9, 3, 6), (0.9, 3, 7), (0.9, 3, 8), 
 (0.9, 3, 9), (0.9, 3, 10), (0.9, 5, 1), (0.9, 5, 2), (0.9, 5, 3), (0.9, 5, 4),
 (0.9, 5, 5), (0.9, 5, 6), (0.9, 5, 7), (0.9, 5, 8), (0.9, 5, 9), (0.9, 5, 10), 
 (0.9, 7, 1), (0.9, 7, 2), (0.9, 7, 3), (0.9, 7, 4), (0.9, 7, 5), (0.9, 7, 6), 
 (0.9, 7, 7), (0.9, 7, 8), (0.9, 7, 9), (0.9, 7, 10)]

tup = exp[conseq]
rho = tup[0]
p = tup[1]
inst = tup[2]

lay = clusterpy.importArcData("HCinstances/hc25-"+str(rho)+"-"+str(inst))

# #QUITAR
# y=lay.Y
# w=lay.Wrook

# start = tm.time()

# # Number of areas
# n = len(y)

# # Region iterator
# numR = range(p)

# # Area iterator
# numA = range(n)

# Wr=w

# z = {}
# for i in numA:
	# z[i] = y[i][1]


# d = nm.zeros(shape = (n,n))
# for i in numA:
	# for j in numA:
		# d[i,j]=distanceA2AEuclideanSquared([[z[i]],[z[j]]])[0][0]
	

# #-----------------------------------
# try: 
# # Create the new model
	# m=Model("pRegions")

	# # Create variables

	# # t_ij

	# t={(i,j):m.addVar(vtype=GRB.BINARY,name="t_"+str([i,j])) for i in numA for j in numA if i<j}
	
	# # f_ijk
	# # amount of flow from area i to j in region k
	# f={(i,j,k):m.addVar(vtype=GRB.SEMICONT,name="f_"+str([i,j,k])) for i in numA for j in Wr[i] for k in numA}
		
	# # y_ik
	# # 1 if areas i included in region k
	# # 0 otherwise
	# y = []
	# for i in numA:
		# y_i = []
		# for k in numA:
			# y_i.append(m.addVar(vtype=GRB.BINARY,name="y_"+str([i,k])))
		# y.append(y_i)

	# # w_ik
	# # 1 if areas i is chosen as a sink
	# # 0 otherwise
	# w = []
	# for i in numA:
		# w_i = []
		# for k in numA:
			# w_i.append(m.addVar(vtype=GRB.BINARY,name="w_"+str([i,k])))
		# w.append(w_i)
		  
	# # Integrate new variables
	# m.update()

	# # Objective function

	# temp = []
	# for i in numA:
		# # Total heterogeneity
		# for j in numA:
			# if i<j:
				# temp.append(d[i][j]*t[i,j])

	# m.setObjective(quicksum(temp), GRB.MINIMIZE)

	# # Constraints 1
	# for i in numA:
		# temp = []
		# for k in numR:
			# temp.append(y[i][k])
		# m.addConstr(quicksum(temp)==1,"c1_"+str([i]))
						
	# # Constraints 2		
	# for i in numA:
		# for k in numR:
			# m.addConstr(w[i][k]<=y[i][k],"c2_"+str([i,k]))
		
	# # Constraints 3		
	# for k in numR:
		# temp = []
		# for i in numA:
			# temp.append(w[i][k])
		# m.addConstr(quicksum(temp) == 1,"c3_"+str([k]))

	# # Constraints 4, 5
	# for k in numR:
		# for i in numA:
			# for j in Wr[i]:
				# m.addConstr(f[i,j,k]<=y[i][k]*(n-p),"c4_"+str([i,j,k]))
				# m.addConstr(f[i,j,k]<=y[j][k]*(n-p),"c5_"+str([i,j,k]))
	
	# # Constraints 6 
	# for k in numR:
		# for i in numA:
			# temp = []
			# for j in Wr[i]:
				# temp.append(f[i,j,k]-f[j,i,k])
			# m.addConstr(quicksum(temp)>=y[i][k]-(n-p)*w[i][k],"c6_"+str([i,k]))				


	# # Constraints 7
	# for i in numA:
		# for j in numA:
			# if i<j:
				# for k in numR:
					# m.addConstr(t[i,j]>=y[i][k]+y[j][k]-1,"c7_"+str([i,j,k]))	
	
	# m.update()
	
	# m.setParam('LogFile', 'HC-'+str(p)+'-'+str(rho)+'-'+str(inst))
	# #m.params.timeLimit = 14400 #4 HORAS
	# m.optimize()
	   
	# time = tm.time()-start
	
	# # for v in m.getVars():
		# # if v.x >0:
			# # print v.varName, v.x
	
	# # output = { "objectiveFunction": m.objVal,
		# # "bestBound": m.objBound,
		# # "running time": time,
		# # "algorithm": "pRegionsExact",
		# # "regions" : 'none',#len(sol),
		# # "r2a": 'none',#sol,
		# # "p": p,
		# # "distanceType" :  "EuclideanSquared",
		# # "distanceStat" : "None",
		# # "selectionType" : "None",
		# # "ObjectiveFunctionType" : "None"} 
	# # print "Done"
	# #return output
	
	# f = open("HC-"+str(p)+"-"+str(rho)+"-"+str(inst)+".txt","w")
	# f.write(str(m.numVars)+"  "+str(m.numConstrs)+"  "+str(time)+" "+str(m.objVal))
	# f.close()
	
			
# except GurobiError:
	# print 'Error reported'
	

n=25
numA = range(n)

heu=[]
for iter in range(30):

	lay.cluster('azpTabu', ['SAR1'], p)
	azpTexp=lay.fieldNames[-1]
	output=lay.outputCluster[azpTexp]
	sol = output["r2a"]

	t={(i,j):0 for i in numA for j in numA if i<j}
	num = list(numA)
	while num:
		i = num[0]
		f = num.remove(i)
		for j in range(i+1,n):
			if sol[i]==sol[j]: #same region
				t[i,j] = 1
	
	result = {'OF':output['objectiveFunction'],'t':t,'time':output["runningTime"],'sol':sol}
	heu.append(result)

heuSort = sorted(heu, key=lambda k: k['OF'])

f = open ("AZPtabuExp.txt", "w")
for j in range(len(heuSort)):	
	f.write(str(heuSort[j])+'\n')
f.close()

#volver un string como un diccionario: http://stackoverflow.com/questions/988228/converting-a-string-to-dictionary
# import ast
# ast.literal_eval("{'muffin' : 'lolz', 'foo' : 'kitty'}")

#import pdb; pdb.set_trace()

# sorted(d.items(), key=itemgetter(1))
# print t, len(t)
