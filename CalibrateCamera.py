import cv2
from SetupUtil import *
from MultithreadVideoStream import MultithreadVideoStream
from VisionUtils import *
import numpy as np


'''Required for trackbars'''
def do_nothing(x):
    pass

setUpCamera(devicePort=0)

camera = MultithreadVideoStream(src=0).start()

setUpWindowsAndTrackbars()

greenLower = np.array([cv2.getTrackbarPos("huelower", "Trackbars"), cv2.getTrackbarPos("satlower", "Trackbars"),
                       cv2.getTrackbarPos("vallower", "Trackbars")])
greenUpper = np.array([cv2.getTrackbarPos("hueupper", "Trackbars"), cv2.getTrackbarPos("satupper", "Trackbars"),
                       cv2.getTrackbarPos("valupper", "Trackbars")])

first = camera.read()
mask1 = preprocessImage(first, greenLower, greenUpper)
contours = cv2.findContours(mask1.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
largest_contour = max(contours, key=cv2.contourArea)
target = cv2.minAreaRect(largest_contour)
focalLength = (target[1][1] * 1.524) / 0.1016

while True:
    greenLower = np.array([cv2.getTrackbarPos("huelower", "Trackbars"), cv2.getTrackbarPos("satlower", "Trackbars"), cv2.getTrackbarPos("vallower", "Trackbars")])
    greenUpper = np.array([cv2.getTrackbarPos("hueupper", "Trackbars"), cv2.getTrackbarPos("satupper", "Trackbars"), cv2.getTrackbarPos("valupper", "Trackbars")])

    frame = camera.read()

    mask = preprocessImage(frame, greenLower, greenUpper)

    print(focalLength)

    cv2.imshow("Frame", frame)
    cv2.imshow("Mask", mask)

    if checkkeypressed():
        break

writeHSV()
camera.release()
cv2.destroyAllWindows()