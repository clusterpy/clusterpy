import copy
import numpy
from scipy.sparse import dok_matrix, linalg

def topoStatistics(W,nWrook,regular=False):
    frontiers = list(set(W.keys()) - set(nWrook.keys()))
    nw = []
    areas_nngs = {}
    wSparse = dok_matrix((len(W),len(W)))
    n1 = 0
    for w in W:
        n1 += len(W[w])
        for j in W[w]:
            wSparse[w,j] = 1
    try:
        eig = max(linalg.eigsh(wSparse,2)[0])
    except:
        eig = -9999

    for w in nWrook:
        nw += [len(W[w])]
        if nw[-1] != 0:
            if areas_nngs.has_key(nw[-1]):
                areas_nngs[nw[-1]].append(w)
            else:
                areas_nngs[nw[-1]] = [w]
    # Calulating second moment of P(n)
    mu2 = 0
    mu1 = numpy.mean(nw)
    mu2 = numpy.var(nw)
    m = {}
    p = {}
    for n in areas_nngs:
        # mean average neighbors of areas wich are neighbor of an area with n neighbors
        mean = 0
        # number of areas wich are neighbor of areas areas with n neighbors
        nareas_n = 0
        for a in areas_nngs[n]:
            if a not in frontiers:
                neighs = W[a]
                for a1 in neighs:
                    mean += len(W[a1])
                    nareas_n += 1
        mean = mean/float(nareas_n)
        m[n] = mean
        p[n] = len(areas_nngs[n])/float(len(nWrook))
    X1 = []
    X2 = []
    Y = []
    Y2 = []
    for n in m:
        for k in areas_nngs[n]:
            X1.append(1)
            X2.append(n)
            Y.append(n*m[n])
            Y2.append((n**2)*m[n])
    X = numpy.matrix(zip(X1,X2))
    Y = numpy.matrix(Y)
    sparseness = n1/float(len(W)**2-len(W))
    if regular:
        a1 = 0
        a2 = 0
        a3 = 0
        mu2 = 0
    else:
        B = (X.transpose()*X)**(-1)*X.transpose()*Y.transpose()
        a1 = (mu1*(mu2+numpy.mean(Y)) - numpy.mean(Y2))/float(mu2)
        a2 = (B[0] - mu2)/mu1 #ESTE NO DA
        a3 = -1*(B[1] -mu1)
    return max(nw), min(nw), numpy.mean(nw),mu2,a1,sparseness,eig

def stepFrontiers(firstArea,desiredEnd,unusedNeighbors,Wrook,Wqueen,deep):
    if deep == 2:
        unusedNeighbors.append(desiredEnd)
    availableMovements = list(set(Wrook[firstArea]).intersection(set(unusedNeighbors)))

    result = False
    if len(availableMovements) == 0:
        return firstArea == desiredEnd, unusedNeighbors
    else:
        uN = unusedNeighbors
        for i in availableMovements:
            if i == desiredEnd:
                return True, unusedNeighbors
            unusedNeighborsR = copy.deepcopy(unusedNeighbors)
            unusedNeighborsR.remove(i)
            res,unusedNeighborsR = stepFrontiers(i,desiredEnd,unusedNeighborsR,Wrook,Wqueen,deep+1)
            uN = set(uN).intersection(set(unusedNeighborsR))
            result = res or result
            if result:
                break
        return result, uN    

def noFrontiersW(Wrook,Wqueen,areas):
    def nAvailableMovements(uN,area):
        availableMovements = list(set(Wrook[area]).intersection(set(uN)))
        if len(Wrook[area]) == 2:
            return 0
        return len(availableMovements)
    
    nWrook = copy.deepcopy(Wrook)
    candidates = []
    for area in Wrook:
        interior = False
        unusedNeighbors = copy.deepcopy(Wqueen[area])
        unusedNeighbors.sort(key=lambda x: nAvailableMovements(unusedNeighbors,x))
        unusedNeighbors.reverse()
        while len(unusedNeighbors) > 0:
            initialArea = unusedNeighbors.pop(0)
            actArea = initialArea
            if len(Wqueen[area]) >= 2 and nAvailableMovements(unusedNeighbors,actArea) >= 1:
                int, uN = stepFrontiers(actArea,initialArea,unusedNeighbors,Wrook,Wqueen,0)
                unusedNeighbors = list(set(uN).intersection(set(unusedNeighbors)))
                if initialArea in unusedNeighbors:
                    unusedNeighbors.remove(initialArea)
                interior = interior or int
            
            elif len(Wqueen[area]) == 1 and nAvailableMovements(unusedNeighbors,actArea) == 0:
                try:
                    interior = Polygon(Polygon(areas[actArea][0]).exterior).contains(Polygon(areas[area][0]))
                except:
                    interior = True
                if interior == True:
                    break
            elif len(Wqueen[area]) >= 2 and nAvailableMovements(unusedNeighbors,actArea) == 0:
                if initialArea in unusedNeighbors:
                    unusedNeighbors.remove(initialArea)
            else:
                if initialArea in unusedNeighbors:
                    unusedNeighbors.remove(initialArea)
            if interior:
                break
        if not interior:
            nWrook.pop(area)
    return nWrook
