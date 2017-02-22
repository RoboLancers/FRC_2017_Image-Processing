import urllib
import numpy as np

from MultithreadVideoStream import MultithreadVideoStream
from SetupUtil import *
from VisionUtils import *


FRAME_X = 640
FRAME_Y = 480
FOV_ANGLE = 59.02039664
DEGREES_PER_PIXEL = FOV_ANGLE / FRAME_X
FRAME_CX = 320
FRAME_CY = 240

def calc_horiz_angle(error):
    """Calculates the horizontal angle from pixel error"""
    return error * DEGREES_PER_PIXEL


def is_aligned(angle_to_turn):
    """Check if shooter is aligned and ready to shoot."""
    if 1 > angle_to_turn > -1:
        return True
    else:
        return False

def report_command(error):
    """Testing - show robot commands in terminal."""
    if 1 > error > -1:
        print("X Aligned")
    else:
        if error > 10:
            print("Turn Right")
        elif error < -10:
            print("Turn Left")


def report_y(cy):
    """Report state of y to terminal."""
    # Maybe useful but not necessary if you have a nice set shooter angle
    if FRAME_CY + 10 > cy > FRAME_CY - 10:
        print("Y Aligned")
    else:
        if cy > FRAME_CY + 10:
            print("Aim Lower")
        elif cy < FRAME_CY - 10:
            print("Aim Higher")

'''Create threaded video stream'''
camera = MultithreadVideoStream('http://10.3.21.2:1180/?action=stream').start()
#camera = MultithreadVideoStream(0).start()

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
    #print(str(frame))

    while frame is None:
        frame = camera.read()

    '''Process the image to get a mask'''
    mask = preprocessImage(frame, greenLower, greenUpper)

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

        x, y, w, h = cv2.boundingRect(first_largest_contour)
        x1, y1, w1, h1 = cv2.boundingRect(second_largest_contour)

        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.rectangle(frame, (x1, y1), (x1 + w1, y1+ h1), (0,0,255), 2)

        if w > h and w1 > h1:
            #angleToTarget = calculateAngleToCenterOfContour(frame, first_largest_contour, second_largest_contour)
            # print(str(abs(y1-y)))
            # distance = (abs(y1-y)-21.43)/-0.09384
            # print(str(distance))

            cx, cy = calculate_centroid(first_largest_contour)

            # calculate error in degrees
            error = cx - FRAME_CX
            angleToTarget = calc_horiz_angle(error)
            print("ANGLE TO TURN " + str(angleToTarget))

            # check if shooter is aligned
            aligned = is_aligned(angleToTarget)
            print("ALIGNED " + str(aligned))

            report_command(error)
            report_y(cy)

            if args["printangle"] > 0:
                print(angleToTarget)

            putInNetworkTable(nt, "Angle To Boiler", str(angleToTarget))

    else:
        putInNetworkTable(nt, 'Angle To Boiler', 'Not Detected')

    if args["display"] > 0:
        '''Shows the images to the screen'''
        cv2.imshow("Frame", frame)
        cv2.imshow("Mask Frame", mask)

        if checkkeypressed():
            break

'''Clean up the camera and close all windows'''
camera.release()
cv2.destroyAllWindows()
