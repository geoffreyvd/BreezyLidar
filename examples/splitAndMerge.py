#!/usr/bin/env python3
from inspect import getargspec
from math import sqrt, pi, cos, sin, atan

class AutoInit(type):
  def __new__(meta, classname, supers, classdict):
    classdict['__init__'] = autoInitDecorator(classdict['__init__'])
    return type.__new__(meta, classname, supers, classdict)

def autoInitDecorator (toDecoreFun):
  def wrapper(*args):
    
    # ['self', 'first_name', 'last_name', 'birth_date', 'sex', 'address']
    argsnames = getargspec(toDecoreFun)[0]
    
    # the values provided when a new instance is created minus the 'self' reference
    # ['Jonh', 'Doe', '21/06/1990', 'male', '216 Caledonia Street']
    argsvalues = [x for x in args[1:]]
    
    # 'self' -> the reference to the instance
    objref = args[0]
    
    # setting the attribute with the corrisponding values to the instance
    # note I am skipping the 'self' reference
    for x in argsnames[1:]:
     	objref.__setattr__(x,argsvalues.pop(0))
    
  return wrapper

class extractedLine(metaclass=AutoInit):
    '''
    line notation class
    '''
    refinedRadian = 0
    refinedDistance = 0
                #(x1,y1,x2,y2,index1,index2,amountOfDataPoints, perpendicularRadian)

    def __init__(self, x1, y1, x2, y2, x1Raw, y1Raw, x2Raw, y2Raw, index1, index2, amountOfDataPoints, perpendicularDistance, perpendicularRadian):
        pass

def calculatePerpendicularLine(x1Raw, y1Raw, x2Raw, y2Raw):
        diffX = x2Raw - x1Raw
        diffY = y2Raw - y1Raw
        slope = 0
        if diffX != 0:
            #step 1 see papier for uitwerking - calculate slope
            slope = diffY / diffX
            #step 2 - calculate perpendicular angle from origon to line
            perpendicularRadian = -atan(slope)
            #step 3 calculate perpendicular distance from origon to line
            perpendicularDistance = (y1Raw-slope*x1Raw)/sqrt(slope*slope+1)            
        elif diffY > 0:
            #als de slope infinite is (de twee punt coordinaten staan op dezelfde x waarde)
            perpendicularDistance = x2Raw
            perpendicularRadian = 0
        else:
            perpendicularDistance = x2Raw
            perpendicularRadian = pi
        # print("perpendicular Angle: {}, Distance: {}".format(perpendicularAngle, perpendicularDistance))
        # print("slope: {}".format(slope))
        return perpendicularRadian, perpendicularDistance

#total least fitting
def linearRegression(listX, listY):
    n = len(listX)
    #1 calculate mean of x and y
    xTotal = 0
    yTotal = 0
    for i in range(n):
        xTotal+=listX[i]
        yTotal+=listY[i]
    xMean = xTotal/n
    yMean = yTotal/n
    #2. calculate angle
    sumOfCovariance = 0
    sumOfDiffToModel = 0
    for i in range(n):
        errorX = listX[i]-xMean
        errorY = listY[i]-yMean
        sumOfCovariance += errorX*errorY
        sumOfDiffToModel += (errorY**2 - errorX**2)
    perpendicularRadian = 0.5*atan((-2*sumOfCovariance)/sumOfDiffToModel)
     
    #3. r = xMean x cos(angle) + yMean x sin(angle)
    perpendicularDistance = xMean * cos(perpendicularRadian) + yMean * sin(perpendicularRadian)
    return perpendicularRadian, perpendicularDistance