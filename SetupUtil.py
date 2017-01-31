import argparse
import csv
import os

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


def readHSV():
    with open('HsvValues.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter='=')

        keys = []
        values = []

        for row in readCSV:
            key = row[0]
            value = row[1]

            keys.append(key)
            values.append(value)

    return keys, values


'''Set up windows and trackbars'''


def setUpWindowsAndTrackbars():
    key, value = readHSV()

    '''Create a window for the trackbars'''
    cv2.namedWindow("Trackbars", cv2.WINDOW_NORMAL)

    '''Create trackbars to filter image'''
    cv2.createTrackbar("huelower", "Trackbars", int(value[key.index('huelower')]), 180, do_nothing)
    cv2.createTrackbar("hueupper", "Trackbars", int(value[key.index('hueupper')]), 180, do_nothing)

    cv2.createTrackbar("huelower", "Trackbars", int(value[key.index('satlower')]), 255, do_nothing)
    cv2.createTrackbar("hueupper", "Trackbars", int(value[key.index('satupper')]), 255, do_nothing)

    cv2.createTrackbar("vallower", "Trackbars", int(value[key.index('vallower')]), 255, do_nothing)
    cv2.createTrackbar("valupper", "Trackbars", int(value[key.index('valupper')]), 255, do_nothing)


def writeHSV():
    key, value = readHSV()

    print(key)

    with open('HsvValues.csv', mode='w') as csvfile:
        writeCSV = csv.writer(csvfile, delimiter='=')

        for string in key:
            writeCSV.writerow(string + '=' + cv2.getTrackbarPos(string, "Trackbars"))


def checkkeypressed():
    '''If q key is pressed then we quit'''
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        return True
