import cv2

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
    angletofirsttarget = get_angle(frameForAngle, firstLargestContour)
    angletofirsttarget = round(angletofirsttarget, 2)

    '''Calculate the angle to the second target'''
    angletosecondtarget = get_angle(frameForAngle, secondLargestContour)
    angletosecondtarget = round(angletosecondtarget, 2)

    '''Calculate the middle by finding the mean'''
    angle_to_middle = (angletofirsttarget + angletosecondtarget) / 2

    return angle_to_middle
