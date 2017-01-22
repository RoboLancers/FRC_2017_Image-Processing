import cv2
import numpy as np

class Vision():

    def processImage(self, image, lower, upper):
        #Convert the frame to the hsv colorspace
        hsvImage = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        #Creates a mask for the color green
        mask = cv2.inRange(hsvImage, lower, upper)

        #Erode and dilate the mask to remove blobs
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        return mask

    def findContours(self, maskImage):
        #Find the contour in the mask
        contours = cv2.findContours(maskImage.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

        #Create an array to hold all contour area
        areaArray = []

        #Only if we find a contour do we continue
        if len(contours) > 0:
            #Find the largest contour
            firstLargestContour = max(contours, key=cv2.contourArea)

            #Fill the array with contour areas
            for i, j in enumerate(contours):
                area = cv2.contourArea(j)
                areaArray.append(area)

            #Sort the array based on contour area
            sortedArray  = sorted(zip(areaArray,contours), key=lambda x: x[0], reverse=True)

            #Find the nth largest contour [n-1][1] only if there is more than one contour
            if len(contours) > 1:
                secondLargestContour = sortedArray[1][1]

            return firstLargestContour, secondLargestContour

    def drawContours(self, image, largestContour, secondLargestContour):
        x, y, w, h = cv2.boundingRect(largestContour)
        cv2.drawContours(image, largestContour, -1, (255, 0, 0), 2)
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        x, y, w, h = cv2.boundingRect(secondLargestContour)
        cv2.drawContours(image, secondLargestContour, -1, (255, 0, 0), 2)
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    #Define both the lower and upper boundary of the ball tracking
    #TODO add trackbar
    greenLower = (0,0,0)
    greenUpper = (1,1,1)

    camera = cv2.VideoCapture(0)

    while True:
        #Read the frame from the camera
        (grabbed, frame) = camera.read()

        #Process the image to get a mask
        maskImage = processImage(frame, greenLower, greenUpper)

        #Find the largest and second largest contour
        firstContour, secondContour = findContours(maskImage)

        #Draws the contours on the mask
        drawContours(maskImage, firstContour, secondContour)

        #Shows the image to the screen
        cv2.imshow("Frame", frame)
        cv2.imshow("Mask Frame", maskImage)

        key = cv2.waitKey(1) & 0xFF

        #If q key is pressed then we quit
        if key == ord("q"):
            break

    #Clean up the camera and close all windows
    camera.release()
    cv2.destroyAllWindows()