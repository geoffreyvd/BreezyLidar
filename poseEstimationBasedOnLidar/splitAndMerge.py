#!/usr/bin/env python3
from inspect import getargspec
from math import sin, cos, radians, atan, atan2, pi, fabs, sqrt, pow
from operator import attrgetter, methodcaller

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
            if perpendicularDistance < 0:
                perpendicularDistance = abs(perpendicularDistance)
                if perpendicularRadian > 0:
                    perpendicularRadian = -pi + perpendicularRadian
                else:
                    perpendicularRadian = pi + perpendicularRadian

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

def assignScoreToWall(amountOfDataPoints, length):
    return (pow(amountOfDataPoints, 1.3) * pow((round(length/20) + 1), 1.3))

def matchWallsWithNewIteration():
    return 0

def mergeCollinearlines(walls):
    isNewWall = True
    while isNewWall == True:
        isNewWall = False
        for wall in walls:
            collinearLines = [wall]
            for wall2 in walls:
                if wall != wall2:
                    diffAngle = abs(wall.perpendicularRadian - wall2.perpendicularRadian) 
                    diffDistance = abs(wall.perpendicularDistance - wall2.perpendicularDistance) 
                    #merge threshhold
                    if diffAngle < 0.033 and diffDistance < 33:
                        collinearLines.append(wall2)
            if len(collinearLines) > 1:
                newWall = concatenateWalls(collinearLines)
                walls[:] = [item for item in walls if not item in collinearLines]
                walls.append(newWall)
                isNewWall = True
                break
    return walls
        
def concatenateWalls(collinearLines):
    smallestIndex = 1000
    biggestIndex = 0
    amountOfDataPoints = 0
    for line in collinearLines:
        if line.index1 < smallestIndex:
            smallestIndex = line.index1
            smallestLine = line
        if line.index2 > biggestIndex:
            biggestIndex = line.index2
            biggestLine = line
        amountOfDataPoints += line.amountOfDataPoints
    perpendicularRadian, perpendicularDistanceRaw = calculatePerpendicularLine(smallestLine.x1Raw, 
        smallestLine.y1Raw, biggestLine.x2Raw, biggestLine.y2Raw)
    length = sqrt(pow(biggestLine.x2Raw-smallestLine.x1Raw, 2) + pow(biggestLine.y2Raw -smallestLine.y1Raw, 2))
    score = assignScoreToWall(amountOfDataPoints, length)
    newWall = extractedLine(smallestLine.x1, smallestLine.y1, biggestLine.x2, biggestLine.y2, smallestLine.x1Raw, 
        smallestLine.y1Raw, biggestLine.x2Raw, biggestLine.y2Raw, smallestIndex, biggestIndex, 
        amountOfDataPoints, perpendicularDistanceRaw, perpendicularRadian, length, score)
    return newWall    
    
#super class which can be inherited to use constructor parameter names as class variable names
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

    def __init__(self, x1, y1, x2, y2, x1Raw, y1Raw, x2Raw, y2Raw, index1, index2, 
    amountOfDataPoints, perpendicularDistance, perpendicularRadian, length, score):
        pass

class splitAndMerge():
    def __init__(self, config, lidarvisualiser):
        self.config = config
        self.lidarVisualiser = lidarvisualiser
        self.thresholdScore = 35000
    
    # lets calculate the corner points - split and merge
    def extractLinesFrom2dDatapoints(self, scandata, first, last):
        x1Raw = self.config.sinRaw[first] * scandata[first]
        y1Raw = self.config.cosRaw[first] * scandata[first]
        x2Raw = self.config.sinRaw[last] * scandata[last]
        y2Raw = self.config.cosRaw[last] * scandata[last]

        firstPointX, firstPointY = self.lidarVisualiser.applyScaleToPoint(x1Raw, y1Raw)   
        lastPointX, lastPointY = self.lidarVisualiser.applyScaleToPoint(x2Raw, y2Raw)  

        # #test purposes - draw blue line from first point to last point
        # self.lidarVisualiser.plotSplitLine(firstPointX, firstPointY, lastPointX, lastPointY)

        #calculate distance and angle to line drawn through first and last point
        perpendicularRadian, perpendicularDistanceRaw = calculatePerpendicularLine(x1Raw, y1Raw, x2Raw, y2Raw)

        # #test purpose - draw perpendicular line with green 
        # self.lidarVisualiser.plotPerpendicularLines(perpendicularDistance, perpendicularRadian)    

        largestDistance = 0
        indexLargestDistance = 0
        missingDataCount = 0
        for i in range(first +1, last):
            if scandata[i] != 0:
                # math step 4 on paper, calculate distance from each point to perpendicular line
                distance = fabs(scandata[i] * cos(perpendicularRadian - self.config.scanRadians[i]) - perpendicularDistanceRaw)
                if distance > largestDistance:
                    indexLargestDistance = i
                    largestDistance = distance
            else:
                missingDataCount+=1

        #threshhold for detecting new corner point (in mm)
        if largestDistance >30:
            # # test purpose - draw largest distance line in red
            # self.lidarVisualiser.plotLargestDistance(indexLargestDistance)
            
            #recursively check for new corner points
            listOfWalls = self.extractLinesFrom2dDatapoints(scandata, first, indexLargestDistance)
            listOfWalls.extend(self.extractLinesFrom2dDatapoints(scandata, indexLargestDistance, last))
        else:
            #(x1,y1,x2,y2,index1,index2,amountOfDataPoints,perpendicularDistance, perpendicularRadian)
            length = sqrt(pow(x2Raw-x1Raw, 2) + pow(y2Raw -y1Raw, 2))
            amountOfDataPoints = last-first-missingDataCount+1
            score = assignScoreToWall(amountOfDataPoints, length)
            listOfWalls = [extractedLine(firstPointX, firstPointY, lastPointX, lastPointY, x1Raw, y1Raw, x2Raw, y2Raw,
                first, last, amountOfDataPoints, perpendicularDistanceRaw, perpendicularRadian, length, score)]
        return listOfWalls

    def extractWallsFromLines(self, extractedLines):
        #TODO best filter for wall selection: one that has the most data points, and length is long
        extractedLines = sorted((l for l in extractedLines if l.score > self.thresholdScore), reverse=True, key=attrgetter('score')) 
        self.lidarVisualiser.plotWalls(extractedLines)
        return extractedLines
    
    def refineWallParameters(self, walls, scandata):
        listX = []
        listY = []
        for i in range(walls[0].index1, walls[0].index2+1):
            listX.append(scandata[i] * self.config.sinRaw[i])
            listY.append(scandata[i] * self.config.cosRaw[i])
        return linearRegression(listX, listY)