import cv2
import numpy as np

greenLower = (0,0,0)
greenUpper = (1,1,1)

camera = cv2.VideoCapture(0)

while True:
    (grabbed, frame) = camera.read()

    cv2.imshow("Frame", frame)


camera.release()
cv2.destroyAllWindows()