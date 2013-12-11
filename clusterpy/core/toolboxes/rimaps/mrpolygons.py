import numpy

def polarPolygon2cartesian(polarPolygon):
    polygon = []
    for nr,point in enumerate(polarPolygon):
        polygon.append([polarPolygon[nr][1]*numpy.cos(polarPolygon[nr][0]),
                        polarPolygon[nr][1]*numpy.sin(polarPolygon[nr][0])])
    return polygon

def transportPolygonGeometry(polygon,angle,dx,dy,multx,multy):
    newPolygon = []
    for p in polygon:
        rotx = (p[0]*numpy.cos(angle) - p[1]*numpy.sin(angle))*multx
        roty = (p[0]*numpy.sin(angle) + p[1]*numpy.cos(angle))*multy
        transx = dx - rotx
        transy = dy - roty
        point = (transx,transy)
        newPolygon += [point]
    return newPolygon

def scalePolygon(angles,ratios,scale):
    ratios = [x*scale for x in ratios]
    return angles,ratios



def transportPolygon(polygon,center,pointa=0):
    if center <> 0 or pointa <> 0:
        A = pointa
        dx = center[0]
        dy = center[1]
        transx = A[0]-center[0]
        transy = A[1]-center[1]
        if transy >= 0 and transx >= 0:
            multx = -1
            multy = -1
        elif transy >= 0 and transx < 0:
            multx = 1
            multy = 1
        elif transy < 0 and transx < 0:
            multx = 1
            multy = 1
        else:
            multx = -1
            multy = -1
        if transx==0 and transy!=0:
            t = numpy.pi/float(2)
        else:
            t = numpy.arctan(transy/float(transx))
        polygon = transportPolygonGeometry(polygon,t,dx,dy,multx,multy)
    return polygon


def mrpolygon(alp,sigma,mu=10,X_0=10,dt=0.001,nPoints=30):
    """Creates a mean reverting polygon (MR-Polygon)

    :param alp: mean reverting speed to be used in the stochastic process 
    :type alp: float
    :param alp: noise gain of the stochastic process 
    :type alp: float
    :param mu: mean value of the mean reverting process 
    :type mu: float
    :param X_0: initial value of the mean reverting process
    :type X_0: Float
    :param dt: delta time of the mean reverting process
    :type dt: Float
    :param nPoints: number of points in which the MR-Polygon is sampled
    :type nPoints: integer

    :rtype: List of 6 elements with the stochastic process, the original and the sampled polygon
    :return: List
    """
    X1 = [X_0]
    X1e = [X_0]
    t = dt
    a = [0]
    r = [X_0]
    sr = []
    sa = []
    times = [0]
    dim = []
    times = [0]
    lengthPolar = 0
    lengthCarte = 0
    while t < 2*numpy.pi:
        bt = numpy.random.normal()
        X1.append(X1[-1] + alp*(mu - X1[-1])*dt + sigma*numpy.sqrt(dt)*bt)
        l = (dt**2 + (X1[-2]-X1[-1])**2)**0.5
        alpha = numpy.arccos((2*r[-1]**2 - dt**2)/float(2*r[-1]**2)) # phi_1
        beta = (numpy.pi - alpha)/float(2)
        #beta = numpy.arcsin(r[-1]*numpy.sin(alpha)/float(dt)) # phi_2
        if X1[-1] >= X1[-2]: #phi_3
            betap = numpy.pi - beta
        else:
            betap = beta
        psi = numpy.arcsin(dt*numpy.sin(betap)/float(l)) #phi_4
        phi = numpy.pi - betap - psi #phi_5
        rtp = l*numpy.sin(phi)/float(numpy.sin(betap))
        if alpha + a[-1] >= 2*numpy.pi:
            r.append(r[0])
            a.append(numpy.pi*2)
            distance = abs(r[0] - r[-1])
            lengthCarte += distance
            lengthPolar += distance
        else:
            if X1[-1] >= X1[-2]:
                sign = "+"
                r.append(r[-1] + rtp)
            else:
                sign = "-"
                if r[-1] - rtp <= 1:
                    r.append(1)
                else:
                    r.append(r[-1] - rtp)
            a.append(a[-1] + alpha)
            distance = (r[-2]**2 + r[-1]**2 - 2*r[-2]*r[-1]*numpy.cos(alpha))**0.5
            lengthCarte += l
            lengthPolar += distance
        times.append(t)
        t = a[-1]
    realPoints = len(a)
    step = int(realPoints/(nPoints-1))
    for cont in range(realPoints):
        if cont%step == 0:
            sr.append(r[cont])
            sa.append(a[cont])
    if sa[-1] != a[-1]:
        sa.append(a[-1])
        sr.append(r[-1])
    return a, r, sa, sr, times, X1
