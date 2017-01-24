import cv2
import numpy as np
from networktables import NetworkTable


# os.system("uvcdynctrl -s 'Exposure, Auto' 1")
# os.system("uvcdynctrl -s 'Exposure (Absolute)' 5")

NetworkTable.setIPAddress('10.51.15.2')
NetworkTable.setClientMode()
NetworkTable.initialize()

nt = NetworkTable.getTable('jetson')

def do_nothing(x):
    pass

'#Calculate the centroid of the contour'


def calculate_centroid(contour):
    moment = cv2.moments(contour)
    if moment["m00"] != 0:
        center_x = int(moment["m10"] / moment["m00"])
        center_y = int(moment["m01"] / moment["m00"])
    else:
        center_x = 0
        center_y = 0

    return center_x, center_y

'#Find the angle to turn'


def get_angle(frames, contour):
    height, width, channel = frames.shape
    center_x, center_y = calculate_centroid(contour)

    pixel_offset = width / 2 - center_x
    angle_offset = 73 * pixel_offset / width
    angle_offset -= 3.5

    print(str(angle_offset))

    return angle_offset


'#Create a window for the trackbars'
#cv2.namedWindow("Trackbars", cv2.WINDOW_NORMAL)

'#Create trackbars to filter image'
#cv2.createTrackbar("Hue Lower", "Trackbars", 0, 180, do_nothing)
#cv2.createTrackbar("Hue Upper", "Trackbars", 180, 180, do_nothing)

#cv2.createTrackbar("Saturation Lower", "Trackbars", 0, 255, do_nothing)
#cv2.createTrackbar("Saturation Upper", "Trackbars", 255, 255, do_nothing)

#cv2.createTrackbar("Value Lower", "Trackbars", 0, 255, do_nothing)
#cv2.createTrackbar("Value Upper", "Trackbars", 255, 255, do_nothing)

camera = cv2.VideoCapture(0)
camera.set(3, 160)
camera.set(4, 120)

while True:
    # Define both the lower and upper boundary of the ball tracking
    greenLower = np.array([49, 110, 104])
    greenUpper = np.array([180, 255, 255])

    # Read the frame from the camera
    (grabbed, frame) = camera.read()

    # Process the image to get a mask
    # Convert the frame to the hsv colorspace
    hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Creates a mask for the color green
    mask_image = cv2.inRange(hsv_image, greenLower, greenUpper)

    # Erode and dilate the mask to remove blobs
    mask = cv2.erode(mask_image, None, iterations=2)
    mask_image = cv2.dilate(mask, None, iterations=2)

    # Find the contour in the mask
    contours = cv2.findContours(mask_image.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

    # Create an array to hold all contour area
    area_array = []

    # Only if we find a contour do we continue
    if len(contours) > 0:
        # Find the largest contour
        first_largest_contour = max(contours, key=cv2.contourArea)

        # Draws the contours on the mask
        cv2.drawContours(frame, first_largest_contour, -1, (255, 0, 0), 2)

        # Fill the array with contour areas
        for i, j in enumerate(contours):
            area = cv2.contourArea(j)
            area_array.append(area)

        # Sort the array based on contour area
        sortedArray = sorted(zip(area_array, contours), key=lambda x: x[0], reverse=True)

        if len(contours) > 1:
            # Find the nth largest contour [n-1][1] only if there is more than one contour
            second_largest_contour = sortedArray[1]

            if first_largest_contour is second_largest_contour:
                print("Equal")

        a = get_angle(frame, first_largest_contour)
        if nt.isConnected() and a != 36 and a != 32.5:
            nt.putNumber('angletogoal', a)

    # Shows the image to the screen
    cv2.imshow("Frame", frame)
    cv2.imshow("Mask Frame", mask_image)

    # nt.putNumber("First Angle to Turn", angle_to_bigger_target)

    key = cv2.waitKey(1) & 0xFF

    # If q key is pressed then we quit
    if key == ord("q"):
        break

# Clean up the camera and close all windows
camera.release()
cv2.destroyAllWindows()
