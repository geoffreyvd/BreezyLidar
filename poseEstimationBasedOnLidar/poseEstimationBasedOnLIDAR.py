#!/usr/bin/env python3

#apt-get install python3-tk
from math import sin, cos, radians, atan, atan2, pi, fabs, sqrt
from time import time, sleep, ctime
from splitAndMerge import splitAndMerge
from mockLIDAR import URGMocker, READ_FROM_SERIAL, READ_FROM_FILE
from lidarVisualiser import lidarVisualiser
from lidarAndCanvasConfig import lidarAndCanvasConfig
from pixhawkWrapper import pixhawk
# TODO, use numpy instead of python list

class URGPlotter():
    '''
    UGRPlotter extends tk.Frame to plot Lidar scans.
    '''
    
    def __init__(self):
        '''
        Takes no args.  Maybe we could specify colors, lidar params, etc.
        '''
        self.previousWalls = None

        #test
        self.listOfYaw = []
        self.listOfImuYaw = []
        self.listOfYawLR =[]
        
        self.config = lidarAndCanvasConfig()
        self.mocker = URGMocker(READ_FROM_SERIAL)
        self.pixhawk4 = pixhawk()
        self.lidarVisualiser = lidarVisualiser(self.config)
        self.splitAndMerge = splitAndMerge(self.config, self.lidarVisualiser)
        
    def run(self):
        '''
        Call this when you're ready to run.
        '''        
        # Record start time and initiate a count of scans for testing
        self.start_sec = time()

        while True:
            plotter._task()    
            sleep(0.01)    

    def _quit(self):
        elapsed_sec = time() - self.start_sec
        scanCount = self.mocker.getCount()
        showCount = self.lidarVisualiser.getShowCount()
        print('%d scans    in %f sec = %f scans/sec' % (scanCount, elapsed_sec, scanCount/elapsed_sec))
        print('%d displays in %f sec = %f displays/sec' % (showCount, elapsed_sec, showCount/elapsed_sec))
        self.pixhawk4.closeParallelProcess()
        exit(0)

    def _task(self):
        # The only thing here that has to happen is setting the lengh of the line, by setting a new endpoint for the line 
        # x = cos * scanPointDistance, y = sin * scanPointDistance
        scandata = self.mocker.getScan()
        if scandata:
            lengthList = len(self.listOfYaw)
            startTimeIteration = time()
            # print("[{}], {}".format(startTimeIteration - self.start_sec, lengthList))
            self.lidarVisualiser.plotScanDataPointsAsLines(scandata)
            i = 0
            firstValidPoint = -1
            while i == 0:
                firstValidPoint += 1
                i = scandata[firstValidPoint]
            
            i = 0
            lastValidPoint = 681
            while i == 0:
                lastValidPoint -= 1
                i = scandata[lastValidPoint]

            extractedLines = self.splitAndMerge.extractLinesFrom2dDatapoints(scandata, firstValidPoint, lastValidPoint)
            #TODO merge lines
            #The routine uses a standard statistical method, called Chi2- test, to compute a Mahalanobis distance between each pair
            # of line segments based on already computed covariance matrices of line parameters. If 2 line segments have statistical
            # distance less than a threshold, they are merged. T
            walls = self.splitAndMerge.extractWallsFromLines(extractedLines)

            walls[0].refinedRadian, walls[0].refinedDistance = self.splitAndMerge.refineWallParameters(walls, scandata)

            self.calculateYaw(walls)

            #TODO match corner points to previous iteration (by lookign at similar distance and angle)

            self.previousWalls = walls
            self.lidarVisualiser.updateGUI()
            #sleep(0) #test purpose
            #print(time() - startTimeIteration)

            if lengthList % 100 == 0 and lengthList> 0:
                #print("linear regression, average yaw error: {}".format(sum(self.listOfYawLR)/lengthList))
                print("no linear regression, yaw error: {}".format(sum(self.listOfYaw)))
                print("IMU yaw error: {}".format(sum(self.listOfImuYaw)))
                self._quit()
        
    def calculateYaw(self, walls):
        #print("radians: {}, distance: {}".format(walls[0].perpendicularRadian,walls[0].perpendicularDistance))
        #TODO teken de lr lijn, volgens mij is het dikke poep
        #print("LR, radians: {}, distance: {}".format(walls[0].refinedRadian,walls[0].refinedDistance))
        yaw = self.pixhawk4.getImuYawDisplacement()

        if self.previousWalls is not None and yaw is not None:
            wallMapping = []
            estimatedWalls = []
            #estimated walls = add yaw to all walls from previous iteraiton
            for i in range(0, 6):
                #TODO 1) check whetehr it has to be plus or minus yaw
                #TODO 2) check whether perpendicularDistance negative and positive has impact on this
                estimatedWalls.append(self.previousWalls[i].perpendicularRadian + yaw)
                # TODO distance + imu translation
                smallestYawDiff = 9999
                smallestYawDiffIndex = -1
                for j in range(0, 6):
                    #substract current wall angles and distances from estimated wall angles and distances
                    yawDiff = abs(estimatedWalls[i] - walls[j].perpendicularRadian)
                    if yawDiff < smallestYawDiff:
                        smallestYawDiff = yawDiff
                        smallestYawDiffIndex = j
                #take the smallest difference, and if smaller than a certain threshhold, the 2 walls match
                if smallestYawDiffIndex != -1 and smallestYawDiff < 6:
                    #threshold based on IMU uncertainty/error after 100ms?
                    wallMapping.append((i, smallestYawDiffIndex))
            
            averageYaw = 0
            for map in wallMapping:
                averageYaw += self.previousWalls[map[0]].perpendicularRadian - walls[map[1]].perpendicularRadian            
            if len(wallMapping) != 0:
                averageYaw /= len(wallMapping)
                yaw0 = self.previousWalls[wallMapping[0][0]].perpendicularRadian - walls[wallMapping[0][1]].perpendicularRadian 
                #print("yaw angle: {}, last index: {}".format(yaw0*180/pi, walls[0].index2))
                self.listOfYaw.append(yaw0)
                self.listOfImuYaw.append(yaw)
                # #refinedradian has to be defined for different mapping aswell
                # yawLR = self.previousWalls[0].refinedRadian - walls[0].refinedRadian
                # print("yaw angle LR: {}".format(yawLR*180/pi))
                # self.listOfYawLR.append(yawLR)
            else:
                print("no mapping found!! unable to provide yaw estimate")
                
    # daarna mogelijke manier:
	# -aan de hand van VICON ofzo de positie estimate doorgeven aan de FCU (zodat hij zich zel kan corrigeren)
	# -set local position om te vliegen
	# -set 

# Instantiate and pop up the window
if __name__ == '__main__':
    
    plotter = URGPlotter()
    
    plotter.run()
