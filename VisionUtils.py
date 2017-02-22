import cv2
import numpy as np
import math


tiltAngle = 0
'''Calculate the centroid of the contour'''
def calculate_centroid(contour):
    moment = cv2.moments(contour)
    if moment["m00"] > 0:
        center_x = int(moment["m10"] / moment["m00"])
        center_y = int(moment["m01"] / moment["m00"])
    else:
        center_x = 0
        center_y = 0

    return center_x, center_y

'''Find the angle to turn'''
def get_angle_gear(frames, contour):
    height, width, channel = frames.shape
    center_x, center_y = calculate_centroid(contour)

    pixel_offset = width / 2 - center_x
    angle_offset = 73 * pixel_offset / width

    return angle_offset

'''This finds the center of the two contours'''
def find_center(contour1, contour2):
    center_x1, center_y1 = calculate_centroid(contour1)
    center_x2, center_y2 = calculate_centroid(contour2)
    return (center_x1 + center_x2) / 2

def preprocessImage(image, greenLower, greenUpper):
    '''Convert the frame to the hsv color-space'''
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    blurred_image = cv2.bilateralFilter(hsv_image, 9, 75, 75)

    '''Creates a mask for the color green'''
    mask = cv2.inRange(blurred_image, greenLower, greenUpper)

    kernel = np.ones((3, 3), np.uint8)
    #kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2), anchor=1)

    maskRemoveNoise = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    maskCloseHoles = cv2.morphologyEx(maskRemoveNoise, cv2.MORPH_CLOSE, kernel, iterations=2)

    '''Erode and dilate the mask to remove blobs'''
    mask = cv2.erode(maskCloseHoles, kernel, iterations=2)
    mask = cv2.dilate(mask, kernel, iterations=2)

    return mask


def findAndSortContourArea(contours):
    area_array = []

    '''Fill the array with contour areas'''
    for i, j in enumerate(contours):
        area = cv2.contourArea(j)
        area_array.append(area)

    '''Sort the array based on contour area'''
    sortedArray = sorted(zip(area_array, contours), key=lambda x: x[0], reverse=True)

    return sortedArray


def calculateAngleToCenterOfContour(frameForAngle, firstLargestContour, secondLargestContour):
    '''Find the angle to first target and round it'''
    angletofirsttarget = get_angle_gear(frameForAngle, firstLargestContour)
    angletofirsttarget = round(angletofirsttarget, 2)

    '''Calculate the angle to the second target'''
    angletosecondtarget = get_angle_gear(frameForAngle, secondLargestContour)
    angletosecondtarget = round(angletosecondtarget, 2)

    '''Calculate the middle by finding the mean'''
    angle_to_middle = (angletofirsttarget + angletosecondtarget) / 2

    return angle_to_middle

def aspectRatioOfGear(w, h):
    ''' returns true if the rectangle is
    of the correct aspect ratio and false if not.'''
    return w / h >= 1.5 / 5 and w / h <= 3.5 / 5

def percentFilled(w, h, cnt):
    ''' returns if the contour occupies at least 70% of the area of it's bounding rectangle '''
    return cv2.contourArea(cnt) >= 0.7 * w * h

def find_distance(x1,y1,x2,y2):
    root = math.sqrt(  ((x2 - x1) ** 2) + ((y2 - y1) ** 2)  )
    rootInt = int(root)
    return rootInt

def findDistanceToTarget(width):
    # note that the width is multiplied by 2 because of resolution change on the image
    # this change allows the new resolution to fit with the correct model
    distance = (44.139 * math.exp((-0.012 * (2 * width)))) + 1 - float((tiltAngle / 10))
    return distance

def findAngle(distance):
    angle = (.1183*(distance **2 ) - (3.468 * distance) + 69.203)
    return angle