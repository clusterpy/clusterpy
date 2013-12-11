# encoding: latin2
""" Exporting contiguity matrix in different formats
"""
__author__ = "Juan C. Duque, Alejandro Betancourt"
__credits__ = "Copyright (c) 2010-11 Juan C. Duque"
__license__ = "New BSD License"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"
__all__ = ['dict2gal']

from os import path

# dict2gal

def dict2gal(wDict,idvar,fileName):
    """
    Exports the contiguity W matrix on a gal file

    :param wDict: Contiguity dictionary 
    :type wDict: dictionary
    :param idVar: Data dictionary with the id field to be used
    :type idVar: dictionary
    :param fileName: gal file name to create, without ".gal"
    :type fileName: string 

    **Example 1**        
    Exporting rook matrix  ::

        import clusterpy
        china = clusterpy.importArcData("clusterpy/data_examples/china")
        china.exportGALW("chinaW", wtype='rook')

    **Example 2**        
    Exporting queen matrix  ::

        import clusterpy
        china = clusterpy.importArcData("clusterpy/data_examples/china")
        china.exportGALW("chinaW", wtype='queen')

    **Example 3**        
    Exporting queen matrix based on a variable different from ID  ::

        import clusterpy
        california = clusterpy.importArcData("clusterpy/data_examples/CA_Polygons")
        california.exportGALW("californiaW", wtype='queen',idVariable="MYID")

    **Example 3**        
    Exporting a customW matrix imported from a GWT file::

        import clusterpy
        china = clusterpy.importArcData("clusterpy/data_examples/china")
        china.customW = clusterpy.importGWT("clusterpy/data_examples/china_gwt_658.193052")
        china.exportGALW("chinaW", wtype='custom')
    """
    print "Writing GAL file"
    fout = open(fileName + ".gal","w")
    fout.write("".join(["0 ",str(len(idvar))," ",fileName,"\n"]))
    for id in wDict:
        numberOfNeighbs = len(wDict[id])
        line = "".join([str(int(idvar[id][0]))," ",str(int(numberOfNeighbs)),"\n"])
        fout.write(line)
        line = []
        for n in wDict[id]:
            line.append(str(int(idvar[n][0])) + " ")
        line = "".join(line + ["\n"])  
        fout.write(line)
    print "GAL successfully created"
    fout.close()


def dict2csv(wDict,idvar,fileName,standarize=False):
    """
    Exports the nth contiguity W matrix on a csv file

    :param wDict: Contiguity dictionary 
    :type wDict: dictionary
    :param idVar: Data dictionary with the id field to be used
    :type idVar: dictionary
    :param fileName: gal file name to create, without ".gal"
    :type fileName: string 
    :keyword standarize: True to standardize the variables.
    :type standarize: boolean  

    **Examples 1**        
    Writing rook matrix to a csv ::

        import clusterpy
        china = clusterpy.importArcData("clusterpy/data_examples/china")
        china.exportCSVW("chinaW", wtype='rook')

    **Examples 2**        
    Writing rook matrix to a csv ::

        import clusterpy
        china = clusterpy.importArcData("clusterpy/data_examples/china")
        china.exportCSVW("chinaW", wtype='queen')
    """
    fieldNames = [str(idvar[x][0]) for x in idvar]
    fieldNames = [""] + fieldNames
    fout = open(fileName + ".csv","w")
    line = ",".join(fieldNames)
    fout.write(line + "\n")
    data = []
    nAreas = len(wDict.keys())
    for i in wDict:
        data.append([fieldNames[i+1]] + [0]*nAreas)
        ne = len(wDict[i])
        for j in wDict[i]:
            if standarize:
                data[i][j + 1] = 1 / float(ne)
            else:
                data[i][j + 1] = 1
        line = [str(x) for x in data[i]]
        line = ",".join(line)
        fout.write(line + "\n")
    print "CSV successfully created"
