from MultithreadVideoStream import MultithreadVideoStream
from SetupUtil import *
from VisionUtils import *

setUpCamera(device_port=0)

camera = MultithreadVideoStream(src=0).start()

setUpWindowsAndTrackbars()

greenLower = np.array([cv2.getTrackbarPos("huelower", "Trackbars"), cv2.getTrackbarPos("satlower", "Trackbars"),
                       cv2.getTrackbarPos("vallower", "Trackbars")])
greenUpper = np.array([cv2.getTrackbarPos("hueupper", "Trackbars"), cv2.getTrackbarPos("satupper", "Trackbars"),
                       cv2.getTrackbarPos("valupper", "Trackbars")])

while True:
    greenLower = np.array([cv2.getTrackbarPos("huelower", "Trackbars"), cv2.getTrackbarPos("satlower", "Trackbars"), cv2.getTrackbarPos("vallower", "Trackbars")])
    greenUpper = np.array([cv2.getTrackbarPos("hueupper", "Trackbars"), cv2.getTrackbarPos("satupper", "Trackbars"), cv2.getTrackbarPos("valupper", "Trackbars")])

    frame = camera.read()

    mask = preprocess_image(frame, greenLower, greenUpper)

    contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

    if len(contours) > 0:

        largest_contour = max(contours, key=cv2.contourArea)

        target = cv2.minAreaRect(largest_contour)

    cv2.imshow("Frame", frame)
    cv2.imshow("Mask", mask)

    if check_key_pressed():
        break

writeHSV()
camera.release()
cv2.destroyAllWindows()
