import urllib
import numpy as np

from MultithreadVideoStream import MultithreadVideoStream
from SetupUtil import *
from VisionUtils import *


def polygon(c, epsil):
    """Remove concavities from a contour and turn it into a polygon."""
    hull = cv2.convexHull(c)
    epsilon = epsil * cv2.arcLength(hull, True)
    goal = cv2.approxPolyDP(hull, epsilon, True)
    return goal

'''Create threaded video stream'''
#camera = MultithreadVideoStream('http://10.3.21.2:1180/?action=stream').start()
camera = MultithreadVideoStream(0).start()

args = parsearguments()

nt = setUpNetworkTables()

MIN_PERIMETER = 50

focal_length = 887.9928588867188

hsv_values = readHSV()

while True:

    greenLower = np.array([int(hsv_values[0][1]), int(hsv_values[2][1]), int(hsv_values[4][1])])
    greenUpper = np.array([int(hsv_values[1][1]), int(hsv_values[3][1]), int(hsv_values[5][1])])

    '''Read frame from thread camera'''
    frame = camera.read()

    '''Copy the frame just in case'''
    frameCopy = frame.copy()

    '''Process the image to get a mask'''
    mask = preprocessImage(frameCopy, greenLower, greenUpper)

    '''Find the contour in the mask'''
    contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

    contours = [x for x in contours if not cv2.arcLength(x, True) < MIN_PERIMETER]

    '''Only if we find both contours do we continue'''
    if len(contours) > 1:

        sortArray = findAndSortContourArea(contours=contours)

        '''Find the largest contour'''
        first_largest_contour = max(contours, key=cv2.contourArea)

        '''Find the nth largest contour [n-1][1] only if there is more than one contour
           So here we find the second largest'''
        second_largest_contour = sortArray[1][1]

        goal = polygon(first_largest_contour, 0.01)

        cv2.drawContours(mask, [goal], 0, (255, 0, 0), 5)

        ellipse = cv2.fitEllipse(first_largest_contour)
        cv2.ellipse(frame, ellipse, (0, 255, 0), 2)

        (x, y), radius = cv2.minEnclosingCircle(first_largest_contour)
        center = (int(x), int(y))
        radius = int(radius)
        cv2.circle(frame, center, radius, (0, 255, 0), 2)

        x, y, w, h = cv2.boundingRect(first_largest_contour)
        x1, y1, w1, h1 = cv2.boundingRect(second_largest_contour)

        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        if (w > h and w1 > h1):
            print("Boiler")
            print(str(distance_to_camera(4, h)))

    else:
        putInNetworkTable(nt, 'Angle to Boiler', 'Not Detected')

    if args["display"] > 0:
        '''Shows the images to the screen'''
        cv2.imshow("Frame", frame)
        cv2.imshow("Mask Frame", mask)

        if checkkeypressed():
            break

'''Clean up the camera and close all windows'''
#camera.release()
cv2.destroyAllWindows()
