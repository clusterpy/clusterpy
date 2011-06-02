# encoding: latin2
"""clusterPy Output methods
"""
__author__ = "Juan C. Duque, Alejandro Betancourt"
__credits__ = "Copyright (c) 2009-10 Juan C. Duque"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"
__all__ = ['shpWriterDis', 'dbfWriter', 'csvWriter']
    
import struct 
from datetime import datetime
import itertools
from componentsIO import *
# shpWriterDis
# shpWriter
# shpWriter2
# dbfWriter
# csvWriter

def shpWriterDis(areas, fileName, type='polygon'):
    """Shapefile writer dispatcher
    
    :param areas: geometry of the layer to be exported.
    :type areas: list
    :param fileName: name of the shape file that will be generated.
    :type fileName: string
    :param type: layer geometry type, default is polygon. 
    :type type: string

    **Examples:**

    >>> china.shpWriterDis(china.areas, "china")
    """
    if type == 'polygon':
        shpWriter2(areas, fileName, type=5)
    elif type == 'line':
        shpWriter2(areas, fileName, type=3)
    elif type == 'point':
        shpWriter(areas, fileName, type=1)
        
    

def shpWriter(areas, fileName, type=1):
    """This function creates a shapefile and a shx file from a clusterPy 
    list of points.
    
    :param areas: list of points.
    :type areas: list
    :param fileName: the name of the shapefile which will be created(without .shp).
    :type fileName: string
    """
    f = open(fileName + '.shp', "wb")
    g = open(fileName + '.shx', "wb")
    N = len(areas)
    linea = ''
    areaValues = ''
    allX = []
    allY = []
    oldOffset = 50 
    shxOffset = 0
    linea2 = ''
    for i,ar in enumerate(areas):
        numPoints = 0
        X = []
        Y = []
        puntos = ''
        parts = ''
        for pa in ar:
            numPoints = numPoints + len(pa)
            for j in pa:
                puntos = puntos+ struct.pack('<d', j[0]) + struct.pack('<d', j[1])
                X.append(j[0])
                Y.append(j[1])
                allX.append(j[0])
                allY.append(j[1])
        if len(X) > 0:
            Xmin = min(X)
            Ymin = min(Y)
            Xmax = max(X)
            Ymax = max(Y)
        else:
            Xmin = 0
            Ymin = 0
            Xmax = 0
            Ymax = 0
        numParts = len(ar)
        areaValues = struct.pack('<i', type) + struct.pack('<d', Xmin) + struct.pack('<d',
                    Ymin) + struct.pack('<d', Xmax) + struct.pack('<d', Ymax) + struct.pack('<i',
                    numParts) + struct.pack('<i', numPoints) + parts  + puntos
        varLength = (len(areaValues)/2)
        contentLength = struct.pack('>l', varLength)
        shxOffset = shxOffset + oldOffset
        oldOffset = varLength + 4
        id = struct.pack('>l', i + 1)
        id = struct.pack('>l', i + 1)
        linea = linea + id + contentLength + areaValues
        linea2 = linea2 + struct.pack('>l', shxOffset) + struct.pack('>l', oldOffset - 4) 
    Xmin = min(allX)
    Ymin = min(allY)
    Xmax = max(allX)
    Ymax = max(allY)
    Zmin = 0
    Zmax = 0
    Mmin = 0
    Mmax = 0
    flength = (len(linea) + 100)/2
    header1 = struct.pack('>l', 9994) + struct.pack('>l', 0) * 5 + struct.pack('>l', flength) + struct.pack('<l', 
                    1000) + struct.pack('<l', type) + struct.pack('<d', Xmin) + struct.pack('<d', 
                    Ymin) + struct.pack('<d', Xmax) + struct.pack('<d', Ymax) + struct.pack('<d', Zmin) + struct.pack('<d', 
                    Zmax) + struct.pack('<d', Mmin) + struct.pack('<d', Mmax)
    header2 = struct.pack('>l', 9994) + struct.pack('>l', 0) * 5 + struct.pack('>l', (len(linea2) + 100)/2) + struct.pack('<l',
                    1000) + struct.pack('<l', type) + struct.pack('<d', Xmin) + struct.pack('<d', Ymin) + struct.pack('<d', 
                    Xmax) + struct.pack('<d', Ymax) + struct.pack('<d', Zmin) + struct.pack('<d', Zmax) + struct.pack('<d', 
                    Mmin) + struct.pack('<d', Mmax)
    f.write(header1)
    f.write(linea)
    g.write(header2)
    g.write(linea2)
    f.close 
    g.close  

def shpWriter2(areas, fileName, type=5):
    """This function creates a shapefile and a shx file from a clusterPy 
    list of polygons or lines.
    
    :param areas: list of areas
    :type areas: list
    :param fileName: name of the shape file which will be created (without the .shp)
    :type fileName: string
    :param type: 5 to polygons or 3 to polylines
    :type type: Integer
    """
    f = open(fileName + '.shp', "wb")
    g = open(fileName + '.shx', "wb")
    N = len(areas)
    linea = ''
    areaValues = ''
    allX = []
    allY = []
    oldOffset = 50
    shxOffset = 0
    linea2 = ''
    for i,ar in enumerate(areas):
        numPoints = 0
        X = []
        Y = []
        puntos = ''
        parts = ''
        for pa in ar:
            parts = parts + struct.pack('<i', numPoints)
            numPoints = numPoints + len(pa)
            for j in pa:
                puntos = puntos + struct.pack('<d', j[0]) + struct.pack('<d', j[1])
                X.append(j[0])
                Y.append(j[1])
                allX.append(j[0])
                allY.append(j[1])
        if len(X) > 0:
            Xmin = min(X)
            Ymin = min(Y)
            Xmax = max(X)
            Ymax = max(Y)
        else:
            Xmin = 0
            Ymin = 0
            Xmax = 0
            Ymax = 0
        numParts = len(ar)
        areaValues = struct.pack('<i', type) + struct.pack('<d', Xmin) + struct.pack('<d', Ymin) + struct.pack('<d', 
                        Xmax) + struct.pack('<d', Ymax) + struct.pack('<i', numParts) + struct.pack('<i', 
                        numPoints) + parts + puntos
        varLength = (len(areaValues) / 2)
        contentLength = struct.pack('>l', varLength)
        shxOffset = shxOffset + oldOffset
        oldOffset = varLength + 4
        id = struct.pack('>l', i + 1)
        id = struct.pack('>l', i + 1)
        linea = linea + id + contentLength + areaValues
        linea2 = linea2 + struct.pack('>l', shxOffset) + struct.pack('>l', oldOffset - 4) 
    Xmin = min(allX)
    Ymin = min(allY)
    Xmax = max(allX)
    Ymax = max(allY)
    Zmin = 0
    Zmax = 0
    Mmin = 0
    Mmax = 0
    flength = (len(linea) + 100) / 2
    header1 = struct.pack('>l', 9994) + struct.pack('>l', 0) * 5 + struct.pack('>l', flength) + struct.pack('<l', 
                        1000) + struct.pack('<l', type) + struct.pack('<d', Xmin) + struct.pack('<d', Ymin) + struct.pack('<d', 
                        Xmax) + struct.pack('<d', Ymax) + struct.pack('<d', Zmin) + struct.pack('<d', Zmax) + struct.pack('<d', 
                        Mmin) +  struct.pack('<d', Mmax)
    header2 = struct.pack('>l', 9994) + struct.pack('>l', 0) * 5 + struct.pack('>l', (len(linea2) + 100) / 2) + struct.pack('<l',
                        1000) + struct.pack('<l', type) + struct.pack('<d', Xmin) + struct.pack('<d', Ymin) + struct.pack('<d', 
                        Xmax) + struct.pack('<d', Ymax) + struct.pack('<d', Zmin) + struct.pack('<d', Zmax) + struct.pack('<d', 
                        Mmin) + struct.pack('<d', Mmax)
    f.write(header1)
    f.write(linea)
    g.write(header2)
    g.write(linea2)
    f.close
    g.close  
    
def dbfWriter(fieldnames, fieldspecs, records, fileName):
    """Export a .dbf file with layer data

    :param Fieldnames: names of the fields (list of strings), should be no longer than ten characters each and not include ''\\x00.''
    :type Fieldnames: list
    :param Fieldspecs: specifications of the fields (List of tuples in this form (type, size, deci)) size is the field width, deci is the number of decimal places in the object and type could be:
    :type Fieldspecs: list

        * C for ascii character data
        * M for ascii character memo data (real memo fields not supported)
        * D for datetime objects
        * N for ints or decimal objects
        * L for logical values 'T', 'F', or '?'
    
    :type Records: list
    :param Records: Data values.
    """
    f = open(fileName, "wb")
    ver = 3
    now = datetime.now()
    yr, mon, day = now.year - 1900, now.month, now.day
    numrec = len(records)
    numfields = len(fieldspecs)
    lenheader = numfields * 32 + 33
    lenrecord = sum(field[1] for field in fieldspecs) + 1
    hdr = struct.pack('<BBBBLHH20x', ver, yr, mon, day, numrec, lenheader, lenrecord)
    f.write(hdr)
    for name, (typ, size, deci) in itertools.izip(fieldnames, fieldspecs):
        name = name.ljust(11, '\x00')
        fld = struct.pack('<11sc4xBB14x', name, typ, size, deci)
        f.write(fld)
    f.write('\r')
    for record in records:
        f.write(' ')
        for (typ, size, deci), value in itertools.izip(fieldspecs, record):
            if typ == "N":
                value = (("%." + str(size) + "f") % value)[0: size].rjust(size, ' ') 
            elif typ == 'D':
                value = value.strftime('%Y%m%d')
            elif typ == 'L':
                value = str(value)[0].upper()
            else:
                value = str(value)[: size].ljust(size, ' ')
            assert len(value) == size
            f.write(value)
    f.write('\x1A')
    f.close()

def csvWriter(filename, headers, data):
    """Export csvFile with layer data

    :param filename: csv file name to be created.
    :type filename: string
    :param headers: layer field names.
    :type headers: list
    :param data: data values.
    :type data: list
    """
    f = open(filename + '.csv', 'w')
    linea = ''
    for i in headers:
        linea += str(i) + ','
    f.write(linea[0: -1] + '\n')
    for i in data:
        linea = ''
        for j in i:
            linea += str(j) + ','  
        f.write(linea[0: -1] + '\n')
    f.close()

