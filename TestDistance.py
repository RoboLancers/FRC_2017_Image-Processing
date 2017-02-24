from MultithreadVideoStream import MultithreadVideoStream
from SetupUtil import *
from VisionUtils import *
import math

# Dimensions in use (Microsoft Lifecam HD-3000)
FRAME_X = 640
FRAME_Y = 480
FOV_ANGLE = 59.02039664
DEGREES_PER_PIXEL = FOV_ANGLE / FRAME_X
FRAME_CX = 320
FRAME_CY = 240

# Gear dimensions
MIN_AREA = 15000
MAX_AREA = 50000

def polygon(c, epsil):
    """Remove concavities from a contour and turn it into a polygon."""
    hull = cv2.convexHull(c)
    epsilon = epsil * cv2.arcLength(hull, True)
    goal = cv2.approxPolyDP(hull, epsilon, True)
    return goal

def calc_center(M):
    """Detect the center given the moment of a contour."""
    cx = int(M['m10'] / M['m00'])
    cy = int(M['m01'] / M['m00'])
    return cx, cy


def calc_horiz_angle(error):
    """Calculates the horizontal angle from pixel error"""
    return error * DEGREES_PER_PIXEL


def is_aligned(angle_to_turn):
    """Check if shooter is aligned and ready to shoot."""
    if 1 > angle_to_turn > -1:
        return True
    else:
        return False


def avg(x1, x2):
    """"Take average of 2 numbers"""
    sum = x1 + x2
    return sum / 2


def report_command(error):
    """Testing - show robot commands in terminal."""
    if 1 > error > -1:
        print("X Aligned")
    else:
        if error > 10:
            print("Turn Right")
        elif error < -10:
            print("Turn Left")


def report_y(cy):
    """Report state of y to terminal."""
    # Maybe useful but not necessary if you have a nice set shooter angle
    if FRAME_CY + 10 > cy > FRAME_CY - 10:
        print("Y Aligned")
    else:
        if cy > FRAME_CY + 10:
            print("Aim Lower")
        elif cy < FRAME_CY - 10:
            print("Aim Higher")

camera = MultithreadVideoStream(0).start()
args = parsearguments()
nt = setUpNetworkTables()
hsv_values = readHSV()

widthB = 1
greenLower = np.array([int(hsv_values[0][1]), int(hsv_values[2][1]), int(hsv_values[4][1])])
greenUpper = np.array([int(hsv_values[1][1]), int(hsv_values[3][1]), int(hsv_values[5][1])])

while True:
    frame = camera.read()
    mask = preprocessImage(frame, greenLower, greenUpper)

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
            print(480 - y)
            cv2.circle(frame, (int((x + x + w )/2),y), 10, (255,255,0))
            print("Degrees High: ", degrees)
            #Boiler Height 88.5
            print("Distance: ", (88.5-26.5)/math.sin(math.radians(degrees + 21.75)))

    if args["display"] > 0:
        cv2.imshow("Frame", frame)
        cv2.imshow("mask", mask)

        if checkkeypressed():
            break

camera.release()
cv2.destroyAllWindows
