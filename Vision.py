import cv2
import numpy as np

#Define both the lower and upper boundary of the ball tracking
#TODO add trackbar
greenLower = (0,0,0)
greenUpper = (1,1,1)

camera = cv2.VideoCapture(0)

while True:
    #Read the frame from the camera
    (grabbed, frame) = camera.read()

    #Convert the frame to the hsv colorspace
    hsvImage = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    #Creates a mask for the color green
    mask = cv2.inRange(hsvImage, greenLower, greenUpper)

    #Erode and dilate the mask to remove blobs
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    #Find the contour in the mask
    contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

    #Only if we find a contour do we continue
    if len(contours) > 0:
        #Find the largest contour
        maxContour = max(contours, key=cv2.contourArea)

        # TODO Find second largest contour

        moments = cv2.moments(maxContour)

    #Shows the image to the screen
    cv2.imshow("Frame", frame)
    cv2.imshow("HSV Frame", hsvImage)
    cv2.imshow("Mask Frame", mask)

    key = cv2.waitKey(1) & 0xFF

    #If q key is pressed then we quit
    if key == ord("q"):
        break

#Clean up the camera and close all windows
camera.release()
cv2.destroyAllWindows()