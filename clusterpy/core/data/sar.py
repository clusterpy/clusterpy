# encoding: latin2
"""SAR data module
"""
__author__ = "Juan C. Duque, Alejandro Betancourt"
__credits__ = "Copyright (c) 2010-11 Juan C. Duque"
__license__ = "New BSD License"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"
__all__ = ['generateSAR']

import numpy

def generateSAR(w, num, r):
    """
    This function generates n simulated SAR variables with the same parameters for all features.

    :param w: contiguity matrix
    :type w: dictionary
    :param num: number of variables to be simulated
    :type num: integer
    :param r: rho parameter for the process
    :type r: float
    :rtype: dictionary (generated data).
    
    **Examples** 

    Generating a float SAR variable for China with an autoregressive
    coefficient of 0.7
    
    >>> import clusterpy
    >>> china = clusterpy.importArcData("clusterpy/data_examples/china")
    >>> china.generateData("SAR", 'rook', 1, 0.7)

    Generating a integer SAR variable for China with an autoregressive
    coefficient of 0.7

    >>> import clusterpy
    >>> china = clusterpy.importArcData("clusterpy/data_examples/china")
    >>> china.generateData("SAR", 'rook', 1, 0.7, integer=1)
    """
    W = standarizeW(w)[1]
    a = SAR(W, rho=r)
    data = a.realization(n=num)
    Y = {}
    for i in w.keys():
        Y[i] = list(data[i])
    return Y


class DGP:
    """Abstract data generating process model"""

    def __init__(self, w, rho=0.0, meanY=None, sig2=1.0, M=0.0):
        self.dgp = "DGP"
        self.w = w
        self.n = len(w)
        self.sig2 = sig2
        self.sig = numpy.sqrt(sig2)
        self.M = M
        if meanY:
            self.meanY = meanY
        else:
            self.meanY = numpy.zeros((self.n, self.n))
        self.omega()
        self.chol()
        self.corrmat()

    def summary(self):
        print "Spatial DGP: %s; size: %d; sig2: %.2f; rho: %.2f"%(self.dgp, self.n, self.sig2,
                self.rho)
        #print "n is %d"%self.n

    def omega(self):
        print 'build spatial component of vcv matrix'

    def chol(self):
        self.cvcv = numpy.linalg.cholesky(self.vcv)
    
    def corrmat(self):
        s = numpy.sqrt(numpy.diag(self.vcv))
        cmat = numpy.outer(s, s)
        self.ccmat = self.vcv / cmat

    def realization(self, n=1):
        e = numpy.random.normal(0, self.sig, (self.n, n))
        return numpy.dot(self.cvcv, e + self.M)

class SAR(DGP):
    """Simultaneous autoregressive process"""

    def __init__(self, w, rho=0.0, meanY=None, sig2=1.0, M=0.0):
        self.rho = rho
        DGP.__init__(self, w, rho,meanY,sig2=sig2, M=M)
        self.dgp ="SAR"
        self.w = w
        self.M = M
    def omega(self):
        A = numpy.eye(self.n) - self.rho * self.w 
        AI = numpy.linalg.inv(A)
        self.vcv = (self.sig2+self.M ** 2) * numpy.dot(AI, numpy.transpose(AI))

def standarizeW(WCP):
    """
    This function transforms a W contiguity dictionary to a standardized W matrix.

    :param WCP: W dictionary of clusterPy
    :type WCP: dictionary
    :rtype: tuple (W matrix, Ws standarized matrix)
    """
    keys = WCP.keys()
    na = len(keys)
    nW = numpy.zeros((na,na))
    nWs = numpy.zeros((na,na))
    for i in WCP.keys():
        nn = len(WCP[i])
        for j in WCP[i]:
            nW[i][j] = 1
            nWs[i][j] = 1 / float(nn)
    return nW, nWs
