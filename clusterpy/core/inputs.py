# encoding: latin2
"""clusterPy input methods
"""
__author__ = "Juan C. Duque, Alejandro Betancourt"
__credits__ = "Copyright (c) 2009-10 Juan C. Duque"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"
__all__ = ['new','load','importArcData','createPoints','createHexagonalGrid',
           'createGrid','importDBF','importCSV','importShape','importGWT','rimap']
    
import struct
import cPickle
import re
from contiguity import weightsFromAreas, fixIntersections
from layer import Layer
try:
    import Polygon
except:
    pass
    print "Irregular maps creator is not available because Polygon is not installed"
else:
    try:
        import scipy
    except:
        pass
        print "Irregular maps creator is not available because scipy is not installed"
    else:
        from toolboxes import rimap as rim

# INDEX
# new
# load
# importArcData
# createPoints
# createGrid
# importShape
# readShape
# readPoints
# readPolylines
# readPolygons
# importDBF
# importGWT

def rimap(n,N=30,alpha=[0.01,0.3],sigma=[1.1,1.4],dt=0.1,pg=0.01,pu=0.05,su=0.315,boundary=""):
    """Creates an irregular maps

        :param n: number of areas 
        :type n: integer
        :param N: number of points sampled from each irregular polygon (MR-Polygon) 
        :type N: integer
        :param alpha: min and max value to sampled alpha; default is (0.1,0.5)
        :type alpha: List
        :param sigma: min and max value to sampled sigma; default is (1.2,1.5)
        :type sigma: List
        :param dt: time delta to be used to create irregular polygons (MR-Polygons)
        :type dt: Float
        :param pg: parameter to define the scaling factor of each polygon before being introduced as part of the irregular map
        :type pg: Float
        :param pu: parameter to define the probability of increase the number of areas of each polygon before being introduced into the irregular map
        :type pu: Float
        :param su: parameter to define how much is increased the number of areas of each polygon before being introduced into the irregular map
        :type su: Float
        :param boundary: Initial irregular boundary to be used into the recursive irregular map algorithm
        :type boundary: Layer

        :rtype: Layer
        :return: RI-Map instance 

        **Examples** ::

            import clusterpy
            lay = clusterpy.rimap(1000)
            lay.exportArcData("rimap_1000")
    """

    rm = rim.rimap(n,N,alpha,sigma,dt,pg,pu,su,boundary)
    areas = rm.carteAreas
    areas = fixIntersections(areas)
    Wqueen,Wrook, = weightsFromAreas(areas)
    layer = Layer()
    layer.areas = areas
    layer.Wqueen = Wqueen
    layer.Wrook = Wrook
    layer.shpType = 'polygon'
    layer.name = "rimap_" + str(len(areas))
    layer.fieldNames = ["Id","nw"]
    layer.Y = {}
    for i in Wrook:
        layer.Y[i] = [i,len(Wrook[i])]
    return layer

def new():
    """Creates an empty Layer

    **Description**

    Use this function to create an empty layer. This allows the user
    to create his own maps.

    :rtype: Layer (new empty Layer)

    **Examples** ::

        import clusterpy
        lay = clusterpy.new()

    """
    print "Creating new layer"
    layer = Layer()
    print "Done"
    return layer
    

def load(filename):
    """Load a ClusterPy project (<file>.CP)
    
    :param filename: filename without extension 
    :type filename: string
    :rtype: Layer
    :return: CP project 

    **Description**

    With clusterPy you can save your layer objects on a .cp file, 
    which can be reopened in the future using this function.
    
    **Examples** ::

        import clusterpy
        lay = clusterpy.new()
        lay.save("lay")
        layer = clusterpy.load("lay")
    """
    print "Loading cp project"
    f = open(filename + '.cp', 'r') 
    layer = cPickle.load(f)
    f.close()
    print "Done"
    return layer

def importArcData(filename):
    """Creates a new Layer from a shapefile (<file>.shp)
    
    :param filename: filename without extension 
    :type filename: string
    :rtype: Layer (CP project)

    **Description**

    `ESRI <http://www.esri.com/>`_ shapefile is a binary file used to
    save and transport maps. During the last times it has become
    the most used format for the spatial scientists around the world.

    On clusterPy's "data_examples" folder you can find some shapefiles. To
    load a shapefile in clusterPy just follow the example bellow.

    **Example** ::

        import clusterpy
        china = clusterpy.importArcData("clusterpy/data_examples/china")

    """
    layer = Layer()
    layer.name = filename.split('/')[-1]
    print "Loading " + filename + ".dbf"
    data, fields, specs = importDBF(filename + '.dbf')
    print "Loading " + filename + ".shp"
    if fields[0] != "ID":
        fields = ["ID"] + fields
        for y in data.keys():
            data[y] = [y] + data[y]
    layer.fieldNames = fields
    layer.Y = data
    layer.areas, layer.Wqueen, layer.Wrook, layer.shpType = importShape(filename + '.shp')
    layer._defBbox()
    print "Done"
    return layer

def createPoints(nRows, nCols, lowerLeft=(0,0), upperRight=(100,100)):
    """Creates a new Layer with uniformly distributed points in space

    :param nRows: number of rows
    :type nRows: integer
    :param nCols: number of cols
    :type nCols: integer
    :param lowerLeft: lower-left corner coordinates; default is (0,0)
    :type lowerLeft: tuple or none 
    :param upperRight: upper-right corner coordinates; default is (100,100)
    :type upperRight: tuple or none
    :rtype: Layer (new points layer)

    **Description**

    The example below shows how to create a point-based regular grids with clusterPy. 
    
    **Examples**
    
    Creating a grid of ten by ten points.::

        import clusterpy
        points = clusterpy.createPoints(10, 10)
    


    Creating a grid of ten by ten points on the bounding box (0,0,100,100). ::

        import clusterpy
        points = clusterpy.createPoints(10, 10, lowerLeft=(0, 0), upperRight=(100, 100))

    """
    print "Creating points"
    yMin = lowerLeft[1]
    yMax = upperRight[1]
    xMin = lowerLeft[0]
    xMax = upperRight[0]
    nyPoints = nRows
    nxPoints = nCols
    areaHeight = float(yMax - yMin) / nRows
    areaWidth = float(xMax - xMin) / nCols
    N = nyPoints*nxPoints
    Y = {}
    acty = yMax
    actx = xMin
    map = []
    verticalBorderAreas = []
    cont = 0
    for i in range(N):
        Y[i] = [i]
    for i in range(nyPoints):
        nexty = acty - areaHeight
        for j in range(nxPoints):
            nextx = actx + areaWidth
            point = (actx + areaWidth / float(2), acty - areaHeight / float(2))
            area = [point]
            map.append([area])
            actx = nextx
            Y[cont].extend([point[0],point[1]])
            cont = cont + 1
        acty = nexty
        actx = xMin
    layer = Layer()
    layer.Y = Y
    layer.fieldNames = ['ID','X','Y']
    layer.areas = map
    layer.shpType = 'point'
    layer.name = 'root'
    layer._defBbox()
    print "Done"
    return layer

def createHexagonalGrid(nRows, nCols, lowerLeft=(0,0), upperRight=(100,100)):
    """Creates a new Layer with a hexagonal regular lattice
    
    :param nRows: number of rows
    :type nRows: integer
    :param nCols: number of columns
    :type nCols: integer
    :type lowerLeft: tuple or none, lower-left corner coordinates; default is (0,0) 
    :type upperRight: tuple or none, upper-right corner coordinates; default is (100,100)
    :rtype: Layer new lattice 

    **Description**

    Regular lattices are widely used in both theoretical and empirical
    applications in Regional Science. The example below shows how easy 
    the creation of this kind of maps is using clusterPy.
    
    **Examples**

    Create a grid of ten by ten points.::

        import clusterpy
        points = clusterpy.createGrid(10,10)
    

    Create a grid of ten by ten points on the bounding box (0,0,100,100).::

        import clusterpy
        points = clusterpy.createGrid(10, 10, lowerLeft=(0, 0), upperRight=(100, 100))
    """
    print "Creating grid"
    rowHeight = (upperRight[1] - lowerLeft[1])/float(nRows)
    colStep = rowHeight/float(2)
    N = nRows*nCols
    areas = []
    for row in range(nRows):
        actx = lowerLeft[0]
        for col in range(nCols):
            if col != 0:
                actx += 2*colStep
            if col%2 == 1:
                y0 = lowerLeft[1] + rowHeight*row - 2*rowHeight/float(2)
                y1 = lowerLeft[1] + rowHeight*row - rowHeight/float(2)
                y2 = lowerLeft[1] + rowHeight*row
            else:
                y0 = lowerLeft[1] + rowHeight*row - rowHeight/float(2)
                y1 = lowerLeft[1] + rowHeight*row
                y2 = lowerLeft[1] + rowHeight*row + rowHeight/float(2)
            x0 = actx
            x1 = actx + colStep
            x2 = actx + 2*colStep
            x3 = actx + 3*colStep
            pol = [(x0,y1),(x1,y2),(x2,y2),
                   (x3,y1),(x2,y0),(x1,y0),
                   (x0,y1)]
            areas.append([pol])
    Y = {}
    for i in range(N):
        Y[i]=[i]
    layer = Layer()
    layer.Y = Y
    layer.fieldNames = ['ID']
    layer.areas = areas
    layer.Wqueen, layer.Wrook, = weightsFromAreas(layer.areas)
    layer.shpType = 'polygon'
    layer.name = 'root'
    layer._defBbox()
    print "Done"
    return layer

def createGrid(nRows, nCols, lowerLeft=None, upperRight=None):
    """Creates a new Layer with a regular lattice
    
    :param nRows: number of rows
    :type nRows: integer
    :param nCols: number of columns
    :type nCols: integer
    :type lowerLeft: tuple or none, lower-left corner coordinates; default is (0,0) 
    :type upperRight: tuple or none, upper-right corner coordinates; default is (100,100)
    :rtype: Layer new lattice 

    **Description**

    Regular lattices are widely used in both theoretical and empirical
    applications in Regional Science. The example below shows how easy 
    the creation of this kind of maps is using clusterPy.
    
    **Examples**

    Create a grid of ten by ten points.::

        import clusterpy
        points = clusterpy.createGrid(10,10)
    

    Create a grid of ten by ten points on the bounding box (0,0,100,100).::

        import clusterpy
        points = clusterpy.createGrid(10, 10, lowerLeft=(0, 0), upperRight=(100, 100))
    """
    print "Creating grid"
    if lowerLeft != None and upperRight != None:
        ymin = lowerLeft[1]
        ymax = upperRight[1]
        xmin = lowerLeft[0]
        xmax = upperRight[0]
        areaHeight = float(ymax - ymin) / nRows
        areaWidth = float(xmax - xmin) / nCols
    else:
        ymin = 0
        xmin = 0
        xmax = 10*nCols
        ymax = 10*nRows
        areaHeight = 10
        areaWidth = 10
    nyPoints = nRows
    nxPoints = nCols
    N = nyPoints*nxPoints
    Y = {}
    acty = ymax
    actx = xmin
    map = []
    wr = {}
    wq = {}
    # Creating the wr matrix writh towrer criterium
    disAreas = [0, nxPoints - 1, (N-nxPoints), N - 1]
    wr[0] = [1, nyPoints]
    wr[nxPoints - 1] = [nxPoints - 2, 2 * nxPoints - 1]
    wr[N - nxPoints] = [N - nxPoints - nxPoints, N - nxPoints + 1]
    wr[N - 1] = [N - 2, N - 1 - nxPoints]
    wq[0] = [1, nxPoints, nxPoints + 1]
    wq[nxPoints - 1] = [nxPoints - 2, nxPoints + nxPoints - 1,
            nxPoints + nxPoints - 2]
    wq[N - nxPoints] = [N - nxPoints - nxPoints, N - nxPoints + 1,
            N - nxPoints - nxPoints + 1]
    wq[N - 1] = [N - 2, N - 1 - nxPoints, N - 1 - nxPoints - 1]
    verticalBorderAreas = []
    for i in range(1, nxPoints - 1): #Asigning the neighborhood of the corner Areas
        wr[i * nxPoints] = [i * nxPoints - nxPoints, i * nxPoints + 1,
                i * nxPoints + nxPoints]
        wr[nxPoints * i + nxPoints - 1] = [nxPoints * i - 1,
                nxPoints * i + nxPoints - 2, nxPoints * i + 2 * nxPoints - 1]
        wq[i * nxPoints] = [i * nxPoints - nxPoints, i * nxPoints - nxPoints + 1,
                i * nxPoints + 1,i * nxPoints + nxPoints, i * nxPoints + nxPoints + 1]
        wq[nxPoints * i + nxPoints - 1] = [nxPoints * i - 1, nxPoints * i - 2,
                nxPoints * i + nxPoints - 2, nxPoints * i + 2 * nxPoints - 1,
                nxPoints * i + 2 * nxPoints - 2]
        disAreas = disAreas + [i * nxPoints, nxPoints * i + nxPoints - 1]
    disAreas = disAreas + range(1, nxPoints - 1) + range((N - nxPoints) + 1, N - 1)
    for i in range(1, nxPoints - 1): # Asigning the neighborhood of the side Areas
        wr[i]=[i - 1, i + nxPoints, i + 1]
        wq[i]=[i - 1, i + nxPoints - 1, i + nxPoints, i + nxPoints + 1, i + 1]
    for i in  range((N - nxPoints) + 1, N - 1):
        wr[i]=[i - 1, i - nxPoints, i + 1]
        wq[i]=[i - 1, i - nxPoints - 1, i - nxPoints, i - nxPoints + 1, i + 1]
    cont = 0
    for i in range(nyPoints): #Creating de clusterPy areas
        nexty = acty - areaHeight
        for j in range(nxPoints):
            nextx = actx + areaWidth
            x1 = tuple([actx, acty])
            x2 = tuple([nextx, acty])
            x3 = tuple([nextx, nexty])
            x4 = tuple([actx, nexty])
            x5 = tuple([actx, acty])
            area = [x1, x2, x3, x4, x5]
            map.append([area])
            actx = nextx
            if cont not in disAreas: # Asigning the rest of the neighborhoods
                wr[cont]=[cont - 1, cont - nxPoints, cont + 1, cont + nxPoints]
                wq[cont]=[cont - 1, cont - nxPoints - 1, cont - nxPoints,
                        cont - nxPoints + 1, cont + 1, cont + nxPoints - 1,
                        cont + nxPoints, cont + nxPoints + 1]
            cont = cont + 1
        acty = nexty
        actx = xmin
    for i in range(N):
        Y[i]=[i]
    layer = Layer()
    layer.Y = Y
    layer.fieldNames = ['ID']
    layer.areas = map
    layer.Wrook = wr
    layer.Wqueen = wq
    layer.Wqueen, layer.Wrook, = weightsFromAreas(layer.areas)
    layer.shpType = 'polygon'
    layer.name = 'root'
    layer._defBbox()
    print "Done"
    return layer

def importShape(shapefile):
    """Reads the geographic information stored in a shape file and returns
    them in python objects.
    
    :param shapefile: path to shapefile including the extension ".shp"
    :type shapefile: string
    :rtype: tuple (coordinates(List), Wqueen(Dict), Wrook(Dict)).

    **Example** ::

        import clusterpy
        chinaAreas = clusterpy.importShape("clusterpy/data_examples/china.shp")
    """

    INFO, areas = readShape(shapefile)
    if INFO['type'] == 5:
        Wqueen, Wrook = weightsFromAreas(areas)
        shpType = 'polygon'
    elif INFO['type'] == 3:
        shpType = 'line'
        Wrook = {}
        Wqueen = {}
    elif INFO['type'] == 1:
        shpType = 'point'
        Wrook = {}
        Wqueen = {}
    return areas, Wqueen, Wrook, shpType

def readShape(filename):
    """ This function automatically detects the type of the shape and then reads an ESRI shapefile of polygons, polylines or points.

    :param filename: name of the file to be read
    :type filename: string
    :rtype: tuple (information about the layer and areas coordinates). 
    """
    fileObj=open(filename, 'rb')
    fileObj.seek(32, 1)
    shtype = struct.unpack('<i', fileObj.read(4))[0]
    if shtype == 1: # Points
        INFO, areas = readPoints(fileObj)
    elif shtype == 3: #PolyLine
        INFO, areas = readPolylines(fileObj)
    elif shtype == 5: #Polygon
        INFO, areas = readPolygons(fileObj)
    fileObj.close()
    return INFO, areas

def readPoints(bodyBytes):
    """This function reads an ESRI shapefile of points.

    :param bodyBytes: bytes to be processed
    :type bodyBytes: string
    :rtype: tuple (information about the layer and area coordinates).
    """
    INFO = {}
    INFO['type'] = 1
    AREAS = []
    id = 0
    bb0 = struct.unpack('>d', bodyBytes.read(8))[0]
    bb1 = struct.unpack('>d', bodyBytes.read(8))[0]
    bb2 = struct.unpack('>d', bodyBytes.read(8))[0]
    bb3 = struct.unpack('>d', bodyBytes.read(8))[0]
    bb4 = struct.unpack('>d', bodyBytes.read(8))[0]
    bb5 = struct.unpack('>d', bodyBytes.read(8))[0]
    bb6 = struct.unpack('>d', bodyBytes.read(8))[0]
    bb7 = struct.unpack('>d', bodyBytes.read(8))[0]
    while bodyBytes.read(1) <> "":
        bodyBytes.seek(11, 1)
        x = struct.unpack('<d', bodyBytes.read(8))[0]
        y = struct.unpack('<d', bodyBytes.read(8))[0]
        area = [x, y] 
        AREAS = AREAS + [[[tuple(area)]]]
    return INFO, AREAS

def readPolylines(bodyBytes):
    """This function reads a ESRI shape file of lines.

    :param bodyBytes: bytes to be processed
    :type bodyBytes: string
    :rtype: tuple (information about the layer and areas coordinates). 
    """
    INFO = {}
    INFO['type'] = 3
    AREAS=[]
    id = 0
    pos = 100
    bb0 = struct.unpack('>d', bodyBytes.read(8))[0]
    bb1 = struct.unpack('>d', bodyBytes.read(8))[0]
    bb2 = struct.unpack('>d', bodyBytes.read(8))[0]
    bb3 = struct.unpack('>d', bodyBytes.read(8))[0]
    bb4 = struct.unpack('>d', bodyBytes.read(8))[0]
    bb5 = struct.unpack('>d', bodyBytes.read(8))[0]
    bb6 = struct.unpack('>d', bodyBytes.read(8))[0]
    bb7 = struct.unpack('>d', bodyBytes.read(8))[0]
    while bodyBytes.read(1) <> "":
        bodyBytes.seek(7, 1)
        bodyBytes.seek(36, 1)
        nParts = struct.unpack('<i', bodyBytes.read(4))[0]
        nPoints = struct.unpack('<i', bodyBytes.read(4))[0]
        r = 1
        parts = []
        while r <= nParts:
            parts += [struct.unpack('<i', bodyBytes.read(4))[0]]
            r += 1
        ring = []
        area = []
        l = 0
        while l < nPoints:
            if l in parts[1:]:
                area += [ring]
                ring = []
            x = struct.unpack('<d', bodyBytes.read(8))[0]
            y = struct.unpack('<d', bodyBytes.read(8))[0]
            l += 1
            ring = ring + [(x, y)]
        area += [ring]
        AREAS = AREAS + [area]
        id += 1
    return INFO, AREAS

def readPolygons(bodyBytes):
    """This function reads an ESRI shape file of polygons.

    :param bodyBytes: bytes to be processed
    :type bodyBytes: string
    :rtype: tuple (information about the layer and areas coordinates). 
    """
    INFO = {}
    INFO['type'] = 5
    AREAS = []
    id = 0
    pos = 100
    parts = []
    bb0 = struct.unpack('>d', bodyBytes.read(8))[0]
    bb1 = struct.unpack('>d', bodyBytes.read(8))[0]
    bb2 = struct.unpack('>d', bodyBytes.read(8))[0]
    bb3 = struct.unpack('>d', bodyBytes.read(8))[0]
    bb4 = struct.unpack('>d', bodyBytes.read(8))[0]
    bb5 = struct.unpack('>d', bodyBytes.read(8))[0]
    bb6 = struct.unpack('>d', bodyBytes.read(8))[0]
    bb7 = struct.unpack('>d', bodyBytes.read(8))[0]
    while bodyBytes.read(1) <> "":# 100 bytes for header
        area = []
        bodyBytes.seek(7, 1)
        bodyBytes.seek(36, 1)
        numParts = struct.unpack('<i', bodyBytes.read(4))[0]
        numPoints = struct.unpack('<i', bodyBytes.read(4))[0]
        parts = []
        for i in range(numParts):
            parts += [struct.unpack('<i', bodyBytes.read(4))[0]]
        ring = []
        for i in range(numPoints):
            if i in parts and i <> 0:
                area.append(ring)
                ring = []
                x = struct.unpack('<d', bodyBytes.read(8))[0]
                y = struct.unpack('<d', bodyBytes.read(8))[0]
                ring += [(x, y)]
            else:
                x = struct.unpack('<d', bodyBytes.read(8))[0]
                y = struct.unpack('<d', bodyBytes.read(8))[0]
                ring += [(x, y)]
        area.append(ring)
        AREAS.append(area)
    return INFO, AREAS

def importDBF(filename):
    """Get variables from a dbf file.
    
    :param filename: name of the file (String) including ".dbf"
    :type filename: string
    :rtype: tuple (dbf file Data, fieldNames and fieldSpecs).

    **Example** ::

        import clusterpy
        chinaData = clusterpy.importDBF("clusterpy/data_examples/china.dbf")
    """
    Y = {}
    fieldNames = []
    fieldSpecs = []
    fileBytes = open(filename, 'rb')
    fileBytes.seek(4, 1)
    numberOfRecords = struct.unpack('i', fileBytes.read(4))[0]
    firstDataRecord = struct.unpack('h', fileBytes.read(2))[0]
    lenDataRecord = struct.unpack('h', fileBytes.read(2))[0]
    fileBytes.seek(20, 1)
    while fileBytes.tell() < firstDataRecord - 1:
        name = ''.join(struct.unpack(11 * 'c', fileBytes.read(11))).replace("\x00", "")
        typ = ''.join(struct.unpack('c', fileBytes.read(1)))
        fileBytes.seek(4, 1)
        siz = struct.unpack('B', fileBytes.read(1))[0]
        dec = struct.unpack('B', fileBytes.read(1))[0]
        spec = (typ, siz, dec)
        fieldNames += [name]
        fieldSpecs += [spec]
        fileBytes.seek(14, 1)
    fileBytes.seek(1, 1)
    Y = {}
    for nrec in range(numberOfRecords):
        record = fileBytes.read(lenDataRecord)
        start = 0
        first = 0
        Y[nrec] = []
        for nf, field in enumerate(fieldSpecs):
            l = field[1] + 1
            dec = field[2]
            end = start + l + first
            value = record[start: end]
            while value.find("  ") <> -1:
                value = value.replace("  ", " ")
            if value.startswith(" "):
                value = value[1:]
            if value.endswith(" "):
                value = value[:-1]
            if field[0] in ["N", "F", "B", "I", "O"]:
                if dec == 0:
                    value = int(float(value))
                else:
                    value = float(value)
            start = end
            first = -1
            Y[nrec] += [value]
    return (Y, fieldNames, fieldSpecs)

def importCSV(filename,header=True,delimiter=","):
    """Get variables from a csv file.
    
    :param filename: name of the file (String)
    :type filename: string
    :param header: Boolean, which is True if the csv have headers.
    :type header: Boolean or None

    :rtype: tuple (csv file Data, fieldnames).

    **Example** ::

        import clusterpy
        chinaData = clusterpy.importCSV("clusterpy/data_examples/china.csv")
    """
    f = open(filename)
    fields = [c[:-1].strip().rsplit(delimiter) for c in f.readlines()]
    f.close()
    if fields[-1][0] == "":
        fields = fields[:-1]
    nc = len(fields[0])
    Y = {}
    if header:
        fieldnames = fields[0]
        for i, c in enumerate(fields[1:]):
            appY = []
            for x in c:
                try:
                    appY.append(float(x))
                except:
                    appY.append(x)
            Y[i] = appY
    else:
        fieldnames = ['VAR' + str(i) for i in range(nc)]
        for i, c in enumerate(fields):
            appY = []
            for x in c:
                try:
                    appY.append(float(x))
                except:
                    appY.append(x)
            Y[i] = appY
    return (Y, fieldnames)



def importGWT(filename,initialId=1):
    """Get the a neighborhood structure from a GWT file.
    
    :param filename: name of the file (String)
    :type filename: string
    :param initialId: First id of the areas.
    :type initialId: integer 

    :rtype: contiguity dictionary.

    **Example 1** Storing a GWT neighborhood structure into a layer
    object::

        import clusterpy
        china = clusterpy.importArcData("clusterpy/data_examples/china")
        china.customW = clusterpy.importGWT("clusterpy/data_examples/china_gwt_658.193052.gwt")

    """
    finp = open(filename)
    finp.readline()
    w = {}
    reg = re.compile(r"(\d+)\s(\d+)\s+(\d+.\d*)")
    for line in finp:
        items = reg.match(line.strip())
        if items:
            id = int(items.group(1))
            neigh = int(items.group(2))
            if w.has_key(id - initialId):
                w[id - initialId].append(neigh - initialId)
            else:
                w[id - initialId] = [neigh - initialId]
        else:
            raise NameError("File structure is not from a GWT file")
    return w        


    
