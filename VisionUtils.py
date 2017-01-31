import cv2
import os
from networktables import NetworkTable
import re

'''Required for trackbars'''
def do_nothing(x):
    pass

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

'''Calculate the centroid of the contour'''
def calculate_centroid(contour):
    moment = cv2.moments(contour)
    if moment["m00"] != 0:
        center_x = int(moment["m10"] / moment["m00"])
        center_y = int(moment["m01"] / moment["m00"])
    else:
        center_x = 0
        center_y = 0

    return center_x, center_y

'''Find the angle to turn'''
def get_angle(frames, contour):
    height, width, channel = frames.shape
    center_x, center_y = calculate_centroid(contour)

    pixel_offset = width / 2 - center_x
    angle_offset = 73 * pixel_offset / width
    angle_offset -= 3.5

    return angle_offset

'''This finds the center of the two contours'''
def find_center(contour1, contour2):
    center_x1, center_y1 = calculate_centroid(contour1)
    center_x2, center_y2 = calculate_centroid(contour2)
    return (center_x1 + center_x2) / 2

'''Set up windows and trackbars'''
def setUpWindowsAndTrackbars():
    '''Create a window for the trackbars'''
    cv2.namedWindow("Trackbars", cv2.WINDOW_NORMAL)

    '''Create trackbars to filter image'''
    cv2.createTrackbar("Hue Lower", "Trackbars", 0, 180, do_nothing)
    cv2.createTrackbar("Hue Upper", "Trackbars", 180, 180, do_nothing)

    cv2.createTrackbar("Saturation Lower", "Trackbars", 0, 255, do_nothing)
    cv2.createTrackbar("Saturation Upper", "Trackbars", 255, 255, do_nothing)

    cv2.createTrackbar("Value Lower", "Trackbars", 0, 255, do_nothing)
    cv2.createTrackbar("Value Upper", "Trackbars", 255, 255, do_nothing)

def preprocessImage(image, greenLower, greenUpper):
    '''Convert the frame to the hsv color-space'''
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    '''Creates a mask for the color green'''
    mask = cv2.inRange(hsv_image, greenLower, greenUpper)

    '''Blurs the image for easier filtering and less noise'''
    blurred_image = cv2.bilateralFilter(mask,9,75,75)

    '''Erode and dilate the mask to remove blobs'''
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    return mask