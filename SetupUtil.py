import argparse
import csv
import os

import cv2
from networktables import NetworkTable


# noinspection PyUnusedLocal
def do_nothing(x):
    pass


def parse_arguments():
    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--display", type=int, default=-1,
                    help="Whether or not frames should be displayed")
    ap.add_argument("-p", "--print", type=int, default=-1,
                    help="Whether or not math should be printed")
    return vars(ap.parse_args())


def setUpCamera(device_port):
    # Sets all the camera values manually
    os.system("uvcdynctrl -s 'Exposure, Auto' 3 -d video" + str(device_port))
    os.system("uvcdynctrl -s Brightness 62 -d video" + str(device_port))
    os.system("uvcdynctrl -s Contrast 4 -d video" + str(device_port))
    os.system("uvcdynctrl -s Saturation 79 -d video" + str(device_port))
    os.system("uvcdynctrl -s 'White Balance Temperature, Auto' 0 -d video" + str(device_port))
    os.system("uvcdynctrl -s 'White Balance Temperature' 4487 -d video" + str(device_port))
    os.system("uvcdynctrl -s 'Sharpness' 25 -d video" + str(device_port))


def setUpNetworkTables():
    # Start network tables and connect to roboRio
    NetworkTable.setIPAddress('10.3.21.2')
    NetworkTable.setClientMode()
    NetworkTable.initialize()

    '''Gets the table called jetson'''
    nt = NetworkTable.getTable('jetson')

    # while not nt.isConnected():
    # time.sleep(.1)

    return nt


def putInNetworkTable(network_table, key, value):
    if network_table.isConnected():
        network_table.putString(key, value)


def check_key_pressed():
    # If q key is pressed then we quit
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        return True


def setUpWindowsAndTrackbars():
    all_values = readHSV()

    '''Create a window for the trackbars'''
    cv2.namedWindow("Trackbars", cv2.WINDOW_NORMAL)

    '''Create trackbars to filter image'''
    for row in all_values:
        cv2.createTrackbar(row[0], "Trackbars", int(row[1]), 255, do_nothing)


def readHSV():
    all_values = []

    with open('HsvValues.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            all_values.append(row)

    return all_values


def writeHSV():
    all_values = readHSV()

    with open('HsvValues.csv', 'w') as file:
        writer = csv.writer(file)

        for row in all_values:
            writer.writerow((row[0], cv2.getTrackbarPos(row[0], "Trackbars")))
