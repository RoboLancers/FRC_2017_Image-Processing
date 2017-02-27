import math

import cv2
import numpy as np

BOILER_HEIGHT = 88.5
CAMERA_HEIGHT = 31.5  # 21.5


def calculate_centroid(contour):
    moment = cv2.moments(contour)
    if moment["m00"] > 0:
        center_x = int(moment["m10"] / moment["m00"])
        center_y = int(moment["m01"] / moment["m00"])
    else:
        center_x = 0
        center_y = 0

    return center_x, center_y


def get_angle_to_gear(frames, contour):
    height, width, channel = frames.shape
    center_x, center_y = calculate_centroid(contour)

    pixel_offset = width / 2 - center_x
    angle_offset = 73 * pixel_offset / width

    return angle_offset


def find_center(contour1, contour2):
    center_x1, center_y1 = calculate_centroid(contour1)
    center_x2, center_y2 = calculate_centroid(contour2)
    return (center_x1 + center_x2) / 2


def preprocess_image(image, green_lower, green_upper):
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    blurred_image = cv2.bilateralFilter(hsv_image, 9, 75, 75)

    '''Creates a mask for the color green'''
    mask = cv2.inRange(blurred_image, green_lower, green_upper)

    kernel = np.ones((3, 3), np.uint8)

    maskRemoveNoise = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    maskCloseHoles = cv2.morphologyEx(maskRemoveNoise, cv2.MORPH_CLOSE, kernel, iterations=2)

    mask = cv2.erode(maskCloseHoles, kernel, iterations=2)
    mask = cv2.dilate(mask, kernel, iterations=2)

    return mask


def findAndSortContourArea(contours):
    area_array = []

    for i, j in enumerate(contours):
        area = cv2.contourArea(j)
        area_array.append(area)

    sortedArray = sorted(zip(area_array, contours), key=lambda x: x[0], reverse=True)

    return sortedArray


def calculateAngleToCenterOfContour(frame_for_angle, first_largest_contour, second_largest_contour):
    # Find the angle to first target and round it
    angle_to_first_target = get_angle_to_gear(frame_for_angle, first_largest_contour)
    angle_to_first_target = round(angle_to_first_target, 2)

    angle_to_second_target = get_angle_to_gear(frame_for_angle, second_largest_contour)
    angle_to_second_target = round(angle_to_second_target, 2)

    angle_to_middle = (angle_to_first_target + angle_to_second_target) / 2

    return angle_to_middle


def aspectRatioOfGear(w, h):
    """ returns true if the rectangle is
    of the correct aspect ratio and false if not."""
    return w / h >= 1.5 / 5 and w / h <= 3.5 / 5


def percentFilled(w, h, cnt):
    """ returns if the contour occupies at least 70% of the area of it's bounding rectangle """
    return cv2.contourArea(cnt) >= 0.7 * w * h


def degreesAboveCamera(boundingY):
    return ((480 - boundingY) / 480) * 38.5


def distanceFromBoilerCamera(degrees):
    return (BOILER_HEIGHT - CAMERA_HEIGHT) / math.sin(math.radians(degrees + 21.75))
