# encoding: latin2
"""dissolveData
"""
__author__ = "Juan C. Duque, Alejandro Betancourt, Juan Sebastian Marín"
__credits__ = "Copyright (c) 2010-11 Juan C. Duque"
__license__ = "New BSD License"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"
__all__ = ['dissolveData']

import numpy

#X = {'BELS':['sum','first','last'],'T78-98':['med','mean','mode','range'],'AVGBELS':['meanDesv','stdDesv','numberOfAreas'],'Y1978':['min','max']}
def dissolveData(fieldnames, Y, region, X):
    """
    This function dissolve a data Dictionary(Y) according to a
    region2areas vector (region). The results are based on the
    functions given in de dictionary (X) which has the structure
    shown bellow.

    >>> X = {}
    >>> X[variableName1] = [function1, function2,....]
    >>> X[variableName2] = [function1, function2,....]

    Where functions are string which represents the name of the 
    functions to be used on the given variableNames, functions 
    could be,'sum','mean','min','max','meanDesv','stdDesv','med',
    'mode','range','first','last','numberOfAreas. The algorithm
    also receives a list of variablesNames (fieldnames).

    :param Y: Data dictionary
    :type Y: dictionary
    :param region: regions2area list
    :type region: list
    :param X: Functions to be used for a specif variable
    :type X: dictionary 
    :param fieldnames: Variable names of data dictionary.
    :type fieldnames: list 
    :rtype: tuple (newData(Dictionary of new variables),newFieldNames(newVariables names))
    """
    i = 2
    filter1 = [] 
    filter2 = [] 
    j = 0
    count = 0
    fields = [] 
    for i in range(2, len(fieldnames)):
        if X.has_key(fieldnames[i]):
            fields.append(i)
    i = 0
    k = 0
    while ((i < len(region)) and (count < len(region))):
        if region[i] == j:
            k = 0
            for k in range(len(fields)):
                filter1.append(Y[i][fields[k]])
            count += 1
        if i == (len(region) - 1):
            filter2.append(filter1)
            filter1 = []
            j += 1
            i = -1
        else:
            if count == len(region) - 1:
                filter2.append(filter1)
        i += 1
    i = 0
    j = 0
    variables = []
    auxiliar1 = []
    auxiliar2 = []
    k = 0
    for i in range(len(filter2)):
        k = 0
        auxiliar1 = []
        for k in range(len(X.keys())):
            j = k
            variables = []
            while j <= len(filter2[i]) - len(X.keys()) + k:
                variables.append(filter2[i][j])
                j += len(X.keys())
            auxiliar1.append(variables)
        auxiliar2.append(auxiliar1)
    l = 0
    m = 0
    tempNewY =[]
    newFieldNames = []
    newFieldNames.append('ID')
    for l in range(len(X.keys())):
        m = 0
        for m in range (len(X[X.keys()[l]])):
            operation = X[X.keys()[l]][m]
            if operation == 'sum':
                tempNewY.append(sumLists(auxiliar2, fields.index(fieldnames.index(X.keys()[l]))))
                newFieldNames.append(X.keys()[l] + '_Sum')
            elif operation == 'mean':
                tempNewY.append(meanLists(auxiliar2, fields.index(fieldnames.index(X.keys()[l]))))
                newFieldNames.append(X.keys()[l] + '_Mean')
            elif operation == 'min':
                tempNewY.append(minimum(auxiliar2, fields.index(fieldnames.index(X.keys()[l]))))
                newFieldNames.append(X.keys()[l] + '_Min')
            elif operation == 'max':
                tempNewY.append(maximum(auxiliar2, fields.index(fieldnames.index(X.keys()[l]))))
                newFieldNames.append(X.keys()[l] + '_Max')
            elif operation == 'meanDesv':
                tempNewY.append(meanDesv(auxiliar2, fields.index(fieldnames.index(X.keys()[l]))))
                newFieldNames.append(X.keys()[l] + '_MeanDesv')
            elif operation == 'stdDesv':
                tempNewY.append(stdDesv(auxiliar2, fields.index(fieldnames.index(X.keys()[l]))))
                newFieldNames.append(X.keys()[l] + '_StdDesv')
            elif operation == 'med':
                tempNewY.append(median(auxiliar2, fields.index(fieldnames.index(X.keys()[l]))))
                newFieldNames.append(X.keys()[l] + '_Med')
            elif operation == 'mode':
                tempNewY.append(mode(auxiliar2, fields.index(fieldnames.index(X.keys()[l]))))
                newFieldNames.append(X.keys()[l] + '_Mode')
            elif operation == 'range':
                tempNewY.append(rangeRegion(auxiliar2, fields.index(fieldnames.index(X.keys()[l]))))
                newFieldNames.append(X.keys()[l] + '_Range')
            elif operation == 'first':
                tempNewY.append(findFirstLast(auxiliar2, fields.index(fieldnames.index(X.keys()[l])), 'first'))
                newFieldNames.append(X.keys()[l] + '_First')
            elif operation == 'last':
                tempNewY.append(findFirstLast(auxiliar2, fields.index(fieldnames.index(X.keys()[l])), 'last'))
                newFieldNames.append(X.keys()[l] + '_Last')
            elif operation == 'numberOfAreas':
                tempNewY.append(numberAreas(region))
                newFieldNames.append(X.keys()[l] + '_AreasPerRegion')
            else :
                raise NameError("The selected operation (%s) is not defined" % operation)
    i = 0
    j = 0
    newData = {}
    if tempNewY != []:
        for i in range(len(tempNewY[0])):
            f = [i]
            j = 0
            for j in range(len(tempNewY)):
                f.append(tempNewY[j][i])
            newData[i] = f
    else:
        for i in range(len(set(region))):
            newData[i] = [i]

    return newData, newFieldNames

def sumLists(alist, number):
    """
    This function returns the sums of values in a specified index (number)
    in each sublist. 
    
    :param alist: Data list
    :type alist: list
    :param number: The index that represents what element of each sublist should be summed 
    :type number: integer
    :rtype: list (sums of values of each region).
    """
    i = 0
    j = 0
    sum1 = 0
    results = []
    for i in range(len(alist)):
        j = 0
        sum1 = 0
        for j in range(len(alist[i][number])):
            sum1 += alist[i][number][j]
        results.append(sum1)
    return results

def meanLists(alist, number):
    """
    This function returns the mean of values in a specified index (number)
    in each sublist. 
    
    :param alist: Data list
    :type alist: list
    :param number: The index that represents what element of each sublist should be taken into account when calculating the mean.
    :type number: integer
    :rtype: list (means of values of each region).
    """
    i = 0
    j = 0
    k = 0
    mean = 0
    sum1 = 0
    results = []
    for i in range(len(alist)):
        j = 0
        sum1 = 0
        for j in range(len(alist[i][number])):
            sum1 += alist[i][number][j]
        mean = (float)(sum1)/len(alist[i][number])
        results.append(mean)
    return results
    
def mode(alist, number):
    """
    This function returns the mode of the values in a specified index (number)
    in each sublist. 

    :param alist: Data list
    :type alist: list
    :param number: The index that represents what element of each sublist should be taken into account when calculating the mode 
    :type number: integer
    :rtype: list (mode of values of each region).
    """
    i = 0
    j = 0
    k = 0
    mode = 0
    results = []
    temp = 0
    counttemp = 0
    countmode = 0
    multimodal = 0
    modal = True
    for i in range(len(alist)) :
        j = 0
        mode = 0
        countmode = 0
        multimodal = 0
        for j in range(len(alist[i][number])) :
            temp = alist[i][number][j]
            counttemp = 0
            k = 0
            for k in range(len(alist[i][number])):
                if alist[i][number][k] == temp :
                    counttemp += 1
            if counttemp > countmode :
                countmode = counttemp
                mode = temp
            elif counttemp >= countmode :
                multimodal += 1
        if 1 == countmode :
            modal = False
            print("Warning: A variable doesn't has mode")
        else :
            if (multimodal - countmode) > 0 :
                print("Warning: Multi-modal in variable")
        results.append(mode)
    if modal == True :
        return results
    else :
        return '--'
	
def minimum(alist, number):
    """
    This function returns the minimum of the values in a specified index (number)
    in each sublist. 

    :param alist: Data list
    :type alist: list
    :param number: The index that represents what element of each sublist should be taken into account when getting the minimum 
    :type number: integer
    :rtype: list (Minimum of values of each region).
    """
    i = 0
    j = 0
    results = []
    temp = []
    for i in range(len(alist)):
        j = 0
        temp = []
        for j in range(len(alist[i][number])):
            temp.append(alist[i][number][j])
        results.append(min(temp))
    return results

def median(alist, number):
    """
    This function returns the median of the values in a specified index (number)
    in each sublist. 

    :param alist: Data list
    :type alist: list
    :param number: The index that represents what element of each sublist should be taken into account when calculating the median 
    :type number: integer
    :rtype: list (Median of values of each region).
    """
    i = 0
    j = 0
    results = []
    temp = []
    median = 0.0
    for i in range(len(alist)):
        j = 0
        temp = []
        for j in range(len(alist[i][number])):
            temp.append(alist[i][number][j])
        temp.sort()
        if len(temp)%2 == 0 :
            median = (temp[len(temp) / 2] + temp[len(temp) / 2 - 1]) / 2.0
        else :
            median = (int)(temp[len(temp) / 2])
        results.append(median)
    return results
    
def maximum(alist, number):
    """
    This function returns the maximum of the values in a specified index (number)
    in each sublist.

    :param alist: Data list
    :type alist: list
    :param number: The index that represents what element of each sublist should be taken into account when getting the maximum 
    :type number: int
    :rtype: list (Median of values of each region)
    """
    i = 0
    j = 0
    results = []
    temp = []
    for i in range(len(alist)):
        j = 0
        temp = []
        for j in range(len(alist[i][number])):
            temp.append(alist[i][number][j])
        results.append(max(temp))
    return results
    
def stdDesv(alist, number):
    """
    This function returns the standard deviation of the values
    in a specified index (number) in each sublist.

    :param alist: Data list
    :type alist: list
    :param number: The index that represents what element of each sublist should be taken into account when calculating the standard deviation 
    :type number: int
    :rtype: list (Standard deviation of values of each region).
    """
    i = 0
    j = 0
    sum1 = 0
    results = []
    meanList = meanLists(alist, number)
    for i in range(len(alist)) :
        j = 0
        sum1 = 0
        for j in range(len(alist[i][number])) :
            sum1 += (alist[i][number][j] - meanList[i]) ** 2
        results.append(((float(sum1)) / (len(alist[i][number]) - 1)) ** 0.5)
    return results

def meanDesv(alist, number) :
    """
    This function returns the mean deviation of the values
    in a specified index (number) in each sublist.

    :param alist: Data list
    :type alist: list
    :param number: The index that represents what element of each sublist should be taken into account when calculating the mean deviation 
    :type number: int
    :rtype: list (Mean deviation of values of each region)
    """
    i = 0
    j = 0
    sum1 = 0
    results = []
    meanList = meanLists(alist, number)
    for i in range(len(alist)) :
        j = 0
        sum1 = 0
        for j in range(len(alist[i][number])) :
            sum1 += abs(alist[i][number][j] - meanList[i])
        results.append((float(sum1)) / (len(alist[i][number])))
    return results

def numberAreas(region):
    """
    This function gets the number of areas in each region

    :param region: Region information
    :type region: list
    """
    j = 0
    i = 0
    areasRegion = []
    count = 0
    count1 = 0
    while ((i < len(region)) and (count < len(region))) :
        if j == region[i] :
            count += 1
            count1 += 1
        if i == len(region) - 1:
            areasRegion.append(count1)
            count1  = 0
            j += 1
            i = -1
        else:
            if count == len(region) - 1:
                areasRegion.append(count1 + 1)
        i += 1
    return areasRegion
    
def findFirstLast(alist, number, position):
    """
    This funcion finds the first or the last value (position) of a list 
    in the given index(number) depending on the user's choice.

    :param alist: Data list
    :type alist: list
    :param number: An specified index
    :type number: int
    :param position: can be either 'first' or 'last'
    :type position: string
    :rtype: list (First or the last value for each region)
    """
    i = 0
    results = []
    temposition = 0
    if position == 'first':
        for i in range(len(alist)):
            temposition = alist[i][number][0]
            results.append(temposition)
        return results
    elif position == 'last':
        for i in range(len(alist)):
            k = len(alist[i][number]) - 1
            temposition = alist[i][number][k]
            results.append(temposition)
        return results
    else:
        raise NameError("The operation is not defined")

    for i in range(len(alist)):
        temposition = alist[i][number][j]
        results.append(temposition)
    return results

def rangeRegion(alist, number):
    """
    This function calculates the difference between the maximum and 
    minimum values of a variable for each region. 

    :param alist: Data list
    :type alist: list
    :param number: The index that represents what element of each sublist should be taken into account when calculating the range.
    :type number: int
    :rtype: list (Maximum difference between values of each region)
    """
    i = 0
    maximum1 = []
    minimum1= []
    range1 = 0
    maximum1 = maximum(alist, number)
    minimum1 = minimum(alist, number)
    results = []
    for i in range(0, len(maximum1)):
        range1 = maximum1[i] - minimum1[i]
        results.append(range1)
    return results
