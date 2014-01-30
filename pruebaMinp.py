import clusterpy
import sys

# python laura.py conseq
conseq = int(sys.argv[1])
# numArea = [3,4,5,6,7,8] 
# numThres = [2,5]
# import itertools
# exp =list(itertools.product(numArea, numThres, range(1,3)))

exp = [(3, 2, 1), (3, 2, 2), (3, 5, 1), (3, 5, 2), (4, 2, 1), 
		(4, 2, 2), (4, 5, 1), (4, 5, 2), (5, 2, 1), (5, 2, 2), 
		(5, 5, 1), (5, 5, 2), (6, 2, 1), (6, 2, 2), (6, 5, 1), 
		(6, 5, 2), (7, 2, 1), (7, 2, 2), (7, 5, 1), (7, 5, 2), 
		(8, 2, 1), (8, 2, 2), (8, 5, 1), (8, 5, 2)]

tup = exp[conseq]
area = tup[0]
thres = tup[1]
form = tup[2] #formulation

lay = clusterpy.importArcData("minpInstances/minp"+str(area*area))

#generate .txt file
if form==1: #Order

	f = open(str(conseq)+"-"+str(area)+"-"+str(thres)+"-O"+".txt","w")
	f.write(str(area*area)+" "+str(thres)+" O ")
	f.close()

	# Order formulation
	lay.cluster('minpOrder',['SAR1', 'Uniform2'],threshold=thres, conseq=conseq)

	minpExp1=lay.fieldNames[-1]
	output1=lay.outputCluster[minpExp1]
	f = open(str(conseq)+"-"+str(area)+"-"+str(thres)+"-O"+".txt","a")
	f.write(str(output1["bestBound"])+"  "+str(output1["objectiveFunction"])+"  "+str(output1["running time"])+"  "+str(output1["p"])+" ")
	f.close()
else: #Flow

	f = open(str(conseq)+"-"+str(area)+"-"+str(thres)+"-F"+".txt","w")
	f.write(str(area*area)+" "+str(thres)+" F ")
	f.close()

	# Flow formulation
	lay.cluster('minpFlow',['SAR1', 'Uniform2'],threshold=thres, conseq=conseq)


	minpExp2=lay.fieldNames[-1]
	output2=lay.outputCluster[minpExp2]
	f = open(str(conseq)+"-"+str(area)+"-"+str(thres)+"-F"+".txt","a")
	f.write(str(output2["bestBound"])+"  "+str(output2["objectiveFunction"])+"  "+str(output2["running time"])+"  "+str(output2["p"])+" ")
	f.close()


	
	
	
# create layer

#import pdb; pdb.set_trace()
# for i in area:
	# for j in instance:
		# lay = clusterpy.createGrid(i,i)
		# lay.generateData("SAR","rook",1,0.8)	
		# lay.generateData('Uniform', 'rook', 1, 10, 20)	
		# lay.exportArcData("minp"+str(i*i)+"-"+str(j))

# lay = clusterpy.createGrid(i,i)
# lay.generateData("SAR","rook",1,0.8)	
# lay.generateData('Uniform', 'rook', 1, 10, 20)	
# lay.exportArcData("minp"+str(i*i)+"-"+str(j))




