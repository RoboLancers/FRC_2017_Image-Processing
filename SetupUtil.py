import argparse
import os
import csv
import cv2

from networktables import NetworkTable

'''Required for trackbars'''
def do_nothing(x):
    pass


def parsearguments():
    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--display", type=int, default=-1,
                    help="Whether or not frames should be displayed")
    ap.add_argument("-p", "--printangle", type=int, default=-1,
                    help="Whether or not angle should be printed")
    return vars(ap.parse_args())


def setUpCamera():
    '''Sets all the camera values manually'''
    os.system("uvcdynctrl -s 'Exposure, Auto' 3")
    os.system("uvcdynctrl -s Brightness 62")
    os.system("uvcdynctrl -s Contrast 4")
    os.system("uvcdynctrl -s Saturation 79")
    os.system("uvcdynctrl -s 'White Balance Temperature, Auto' 0")
    os.system("uvcdynctrl -s 'White Balance Temperature' 4487")
    os.system("uvcdynctrl -s 'Sharpness' 25")


def setUpNetworkTables():
    '''Start network tables and connect to roboRio'''
    NetworkTable.setIPAddress('10.3.21.2')
    NetworkTable.setClientMode()
    NetworkTable.initialize()

    '''Gets the table called jetson'''
    return NetworkTable.getTable('jetson')


def putInNetworkTable(networkTable, key, value):
    if networkTable.isConnected():
        networkTable.putString(key, value)

def checkkeypressed():
    '''If q key is pressed then we quit'''
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        return True

def setUpWindowsAndTrackbars():

    allValues = readHSV()

    '''Create a window for the trackbars'''
    cv2.namedWindow("Trackbars", cv2.WINDOW_NORMAL)

    '''Create trackbars to filter image'''
    for row in allValues:
        cv2.createTrackbar(row[0], "Trackbars", int(row[1]), 255, do_nothing)

def readHSV():
    allValues = []

    with open('HsvValues.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            allValues.append(row)

    return allValues

def writeHSV():
    allValues = readHSV()

    with open('HsvValues.csv', 'w') as file:
        writer = csv.writer(file)

        for row in allValues:
            writer.writerow((row[0], cv2.getTrackbarPos(row[0], "Trackbars")))