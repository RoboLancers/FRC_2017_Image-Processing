from MultithreadVideoStream import MultithreadVideoStream
from SetupUtil import *
from VisionUtils import *

BOILER_HEIGHT = 88.5
CAMERA_HEIGHT = 21.5

camera = MultithreadVideoStream(0).start()
args = parse_arguments()
nt = setUpNetworkTables()
hsv_values = readHSV()

widthB = 1
greenLower = np.array([int(hsv_values[0][1]), int(hsv_values[2][1]), int(hsv_values[4][1])])
greenUpper = np.array([int(hsv_values[1][1]), int(hsv_values[3][1]), int(hsv_values[5][1])])

while True:
    frame = camera.read()
    mask = preprocess_image(frame, greenLower, greenUpper)

    contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    contours = [x for x in contours if not cv2.arcLength(x, True) < 50]

    if len(contours) > 0:
        bigContour = max(contours, key=cv2.contourArea)

        area = cv2.contourArea(bigContour)

        x, y, w, h = cv2.boundingRect(bigContour)
        widthB = w
        heightB = h
        centerXB = x + w / 2
        centerYB = y + h / 2

        if w > h:
            degrees = ((480 - y)/480) * 38.5
            print("Degrees High: ", degrees)
            print("Distance: ", (BOILER_HEIGHT - CAMERA_HEIGHT) / math.sin(math.radians(degrees + 21.75)))

    if args["display"] > 0:
        cv2.imshow("Frame", frame)
        cv2.imshow("mask", mask)

        if check_key_pressed():
            break

camera.release()
cv2.destroyAllWindows()
