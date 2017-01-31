import numpy as np

from SetupUtil import *
from VisionUtils import *

args = parsearguments()

'''Set up the lifecam manually'''
setUpCamera()

'''Setup the network table and assign it to nt'''
nt = setUpNetworkTables()

setUpWindowsAndTrackbars()

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

    if grabbed:

        mask = preprocessImage(frame, greenLower, greenUpper)

        '''Find the contour in the mask'''
        contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

        '''Create an array to hold all contour area'''
        area_array = []

        '''Only if we find both contours do we continue'''
        if len(contours) > 1:
            '''Find the largest contour'''
            first_largest_contour = max(contours, key=cv2.contourArea)

            sortArray = findAndSortContourArea(contours=contours)

            '''Find the nth largest contour [n-1][1] only if there is more than one contour
               So here we find the second largest'''
            second_largest_contour = sortArray[1][1]

            average_angle_to_middle = calculateAngleToCenterOfContour(frame, first_largest_contour,
                                                                      second_largest_contour)
            average_middle_string = str(average_angle_to_middle)

            if args["display"] > 0:
                '''Shows the images to the screen'''
                cv2.imshow("Frame", frame)
                cv2.imshow("Mask Frame", mask)

                if checkkeypressed():
                    break

            if average_angle_to_middle != 36 and average_angle_to_middle != 32.5:
                putInNetworkTable(nt, 'angletogoal', average_middle_string)
        else:
            putInNetworkTable(nt, 'angletogoal', 'Not Detected')

'''Clean up the camera and close all windows'''
writeHSV()
camera.release()
cv2.destroyAllWindows()
