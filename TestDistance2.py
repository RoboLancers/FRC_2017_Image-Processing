import cv2
import numpy as np
import math

from MultithreadVideoStream import MultithreadVideoStream
from SetupUtil import *
from VisionUtils import *


def frameYPxToDegrees(yCoor):
    CAMERA_FRAME_PX_WIDTH = 640
    CAMERA_VIEWING_ANGLE_X = 38.5
    CAMERA_FOCAL_LENGTH_X = CAMERA_FRAME_PX_WIDTH / (2 * math.tan(math.radians(CAMERA_VIEWING_ANGLE_X / 2)))
    return math.degrees(math.atan(yCoor / CAMERA_FOCAL_LENGTH_X))


def yInFrameToDegreesFromHorizon(height):
    CAMERA_TILT_ANGLE = 0
    return CAMERA_TILT_ANGLE - frameYPxToDegrees(height)


def getDistanceToBoiler(y):
    BOILER_TARGET_HEIGHT = 83.0
    CAMERA_Y = 31.0
    angle = yInFrameToDegreesFromHorizon(y)
    return (BOILER_TARGET_HEIGHT - CAMERA_Y) / math.tan(math.radians(angle))

#Shooter Camera 41 degrees up
camera = MultithreadVideoStream(0).start()
args = parsearguments()
nt = setUpNetworkTables()
hsv_values = readHSV()

greenLower = np.array([int(hsv_values[0][1]), int(hsv_values[2][1]), int(hsv_values[4][1])])
greenUpper = np.array([int(hsv_values[1][1]), int(hsv_values[3][1]), int(hsv_values[5][1])])

while True:
    frame = camera.read()
    print("Height: ", np.size(frame, 0))
    print("Width: ", np.size(frame, 1))

    mask = preprocessImage(frame, greenLower, greenUpper)

    contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    contours = [x for x in contours if not cv2.arcLength(x, True) < 50]

    if len(contours) > 1:

        sortArray = findAndSortContourArea(contours=contours)

        firstContour = max(contours, key=cv2.contourArea)
        secondContour = sortArray[1][1]

        x, y, w, h = cv2.boundingRect(firstContour)
        x1, y1, w1, h1 = cv2.boundingRect(secondContour)

        if w > h:
            #Actual Distance 171
            #print(getDistanceToBoiler(((y + h)/2 + (y1 + h1)/2) /2))
            print(getDistanceToBoiler(((x + w) / 2 + (x1 + w1) / 2) / 2))
            print("Boiler")

    if args["display"] > 0:
        cv2.imshow("Frame", frame)
        cv2.imshow("mask", mask)

        if checkkeypressed():
            break

camera.release()
cv2.destroyAllWindows
