import numpy as np

from MultithreadVideoStream import MultithreadVideoStream
from SetupUtil import *
from VisionUtils import *


setUpCamera()

'''Create threaded video stream'''
camera = MultithreadVideoStream(src=0).start()

args = parsearguments()

nt = setUpNetworkTables()

setUpWindowsAndTrackbars()

MIN_PERIMETER = 50

while True:

    greenLower = np.array([cv2.getTrackbarPos("huelower", "Trackbars"), cv2.getTrackbarPos("satlower", "Trackbars"), cv2.getTrackbarPos("vallower", "Trackbars")])
    greenUpper = np.array([cv2.getTrackbarPos("hueupper", "Trackbars"), cv2.getTrackbarPos("satupper", "Trackbars"), cv2.getTrackbarPos("valupper", "Trackbars")])

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

        x, y, w, h = cv2.boundingRect(first_largest_contour)
        x1, y1, w1, h1 = cv2.boundingRect(second_largest_contour)

        if aspectRatioOfGear(w,h) and aspectRatioOfGear(w1, h1):
            average_angle_to_middle = calculateAngleToCenterOfContour(frame, first_largest_contour,
                                                                  second_largest_contour)
            if args["printangle"] > 0:
                print(str(average_angle_to_middle))

            average_middle_string = str(average_angle_to_middle)

            if average_angle_to_middle != 36 and average_angle_to_middle != 32.5:
                putInNetworkTable(nt, 'Angle to Gear', average_middle_string)
    else:
        putInNetworkTable(nt, 'angletogoal', 'Not Detected')

    if args["display"] > 0:
        '''Shows the images to the screen'''
        cv2.imshow("Frame", frame)
        cv2.imshow("Mask Frame", mask)

        if checkkeypressed():
            break

'''Clean up the camera and close all windows'''
camera.release()
cv2.destroyAllWindows()
