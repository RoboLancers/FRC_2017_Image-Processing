import cv2
import numpy as np
from networktables import NetworkTable
import os
from VisionUtils import *


'''Set up the lifecam manually'''
setUpCamera()

'''Setup the network table and assign it to nt'''
nt = setUpNetworkTables()

#setUpWindowsAndTrackbars()

camera = cv2.VideoCapture(0)

#Set size to be smaller
#camera.set(3, 160)
#camera.set(4, 120)

while True:
    '''Define both the lower and upper boundary of the ball tracking'''
    greenLower = np.array([cv2.getTrackbarPos("Hue Lower", "Trackbars"), cv2.getTrackbarPos("Saturation Lower", "Trackbars"), cv2.getTrackbarPos("Value Lower", "Trackbars")])
    greenUpper = np.array([cv2.getTrackbarPos("Hue Upper", "Trackbars"), cv2.getTrackbarPos("Saturation Upper", "Trackbars"), cv2.getTrackbarPos("Value Upper", "Trackbars")])
    #greenLower = np.array([48,103,135])
    #greenUpper = np.array([137,225,255])

    '''Read the frame from the camera'''
    grabbed, frame = camera.read()

    mask = preprocessImage(frame, greenLower, greenUpper)

    '''Find the contour in the mask'''
    contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

    '''Create an array to hold all contour area'''
    area_array = []

    '''Only if we find a contour do we continue'''
    if len(contours) > 0:
        '''Find the largest contour'''
        first_largest_contour = max(contours, key=cv2.contourArea)

        '''Draws the contours on the mask'''
        cv2.drawContours(frame, first_largest_contour, -1, (255, 0, 0), 2)

        '''Fill the array with contour areas'''
        for i, j in enumerate(contours):
            area = cv2.contourArea(j)
            area_array.append(area)

        '''Sort the array based on contour area'''
        sortedArray = sorted(zip(area_array, contours), key=lambda x: x[0], reverse=True)

        '''Set the angle to targets to be 0 initially'''
        angletofirsttarget = 0
        angletosecondtarget = 0

        '''Find the angle to first target'''
        angletofirsttarget = get_angle(frame, first_largest_contour)

        '''Round it to 2 decimal places for easier computation'''
        angletofirsttarget = round(angletofirsttarget, 2)

        '''Checks to see if we have 2 contours'''
        if len(contours) > 1:

            '''Find the nth largest contour [n-1][1] only if there is more than one contour
               So here we find the second largest'''
            second_largest_contour = sortedArray[1][1]

            '''Draw the contour on the frame'''
            cv2.drawContours(frame, second_largest_contour, -1, (255,0,0), 2)

            '''Calculate the angle to the second target'''
            angletosecondtarget = get_angle(frame, second_largest_contour)

            '''Round the angle to 2 decimal places for easier computation'''
            angletosecondtarget = round(angletosecondtarget, 2)

        '''Calculate the middle by finding the mean'''
        average_angle_to_middle = (angletofirsttarget + angletosecondtarget)/2

        '''Convert it to a string to print'''
        average_middle_string = str(average_angle_to_middle)

        '''Prints the angle'''
        print(average_middle_string)

        '''Checks to see if network table is connected'''
        if nt.isConnected() and average_angle_to_middle != 36 and average_angle_to_middle != 32.5:
            '''If it is then we put the angle as a string'''
            nt.putString('angletogoal', average_middle_string)
    else:
        '''Checks to see if network table is connected'''
        if nt.isConnected():
            '''If no contour is detected then we put not detected'''
            nt.putString('angletogoal', "Not Detected")

    '''Shows the images to the screen'''
    cv2.imshow("Frame", frame)
    cv2.imshow("Mask Frame", mask)

    '''If q key is pressed then we quit'''
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

'''Clean up the camera and close all windows'''
camera.release()
cv2.destroyAllWindows()
