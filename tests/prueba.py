import clusterpy

instance = clusterpy.createGrid(10, 10)
instance.generateData("SAR", 'rook', 1, 0.9)
instance.cluster('azpTabu', ['SAR1'], 15)

azpTexp=instance.fieldNames[-1]
output=instance.outputCluster[azpTexp]
sol = output["r2a"]
n=100
numA = range(n)
t={(i,j):0 for i in numA for j in numA if i<j}
#import pdb; pdb.set_trace()
num = list(numA)
while num:
	i = num[0]
	f = num.remove(i)
	for j in range(i+1,n):
		if sol[i]==sol[j]: #same region
			t[i,j] = 1
import pdb; pdb.set_trace()