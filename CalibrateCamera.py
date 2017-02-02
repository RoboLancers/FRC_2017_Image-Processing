import cv2
from SetupUtil import *
from MultithreadVideoStream import MultithreadVideoStream
from VisionUtils import *
import numpy as np


'''Required for trackbars'''
def do_nothing(x):
    pass

setUpCamera()

camera = MultithreadVideoStream(src=0).start()

setUpWindowsAndTrackbars()

while True:
    greenLower = np.array([cv2.getTrackbarPos("huelower", "Trackbars"), cv2.getTrackbarPos("satlower", "Trackbars"), cv2.getTrackbarPos("vallower", "Trackbars")])
    greenUpper = np.array([cv2.getTrackbarPos("hueupper", "Trackbars"), cv2.getTrackbarPos("satupper", "Trackbars"), cv2.getTrackbarPos("valupper", "Trackbars")])

    frame = camera.read()

    mask = preprocessImage(frame, greenLower, greenUpper)
    cv2.imshow("Frame", frame)
    cv2.imshow("Mask", mask)

    if checkkeypressed():
        break

writeHSV()
camera.release()
cv2.destroyAllWindows()