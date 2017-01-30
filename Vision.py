import cv2, sys
import numpy as np
from networktables import NetworkTable
import os
import re
from urllib.request import urlopen


os.system("uvcdynctrl -s 'Exposure, Auto' 3")
os.system("uvcdynctrl -s Brightness 62")
os.system("uvcdynctrl -s Contrast 4")
os.system("uvcdynctrl -s Saturation 79")
os.system("uvcdynctrl -s 'White Balance Temperature, Auto' 0")
os.system("uvcdynctrl -s 'White Balance Temperature' 4487")
os.system("uvcdynctrl -s 'Sharpness' 25")

NetworkTable.setIPAddress('10.3.21.2')
NetworkTable.setClientMode()
NetworkTable.initialize()

nt = NetworkTable.getTable('jetson')

#def do_nothing(x):
    #pass

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

    return angle_offset

def find_center(contour1, contour2):
    center_x1, center_y1 = calculate_centroid(contour1)
    center_x2, center_y2 = calculate_centroid(contour2)
    return (center_x1 + center_x2) / 2


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

#camera.set(3, 160)
#camera.set(4, 120)

while True:
    # Define both the lower and upper boundary of the ball tracking
    #Value with uvcdynctrl
    #greenLower = np.array([cv2.getTrackbarPos("Hue Lower", "Trackbars"), cv2.getTrackbarPos("Saturation Lower", "Trackbars"), cv2.getTrackbarPos("Value Lower", "Trackbars")])
    #greenUpper = np.array([cv2.getTrackbarPos("Hue Upper", "Trackbars"), cv2.getTrackbarPos("Saturation Upper", "Trackbars"), cv2.getTrackbarPos("Value Upper", "Trackbars")])
    greenLower = np.array([48,103,135])
    greenUpper = np.array([137,225,255])

    # Read the frame from the camera
    grabbed, frame = camera.read()

    # Process the image to get a mask
    # Convert the frame to the hsv colorspace
    hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # Creates a mask for the color green
    mask_image = cv2.inRange(hsv_image, greenLower, greenUpper)

    blurred_image = cv2.bilateralFilter(mask_image,9,75,75)

    # Erode and dilate the mask to remove blobs
    mask = cv2.erode(mask_image, None, iterations=2)
    mask_image = cv2.dilate(mask_image, None, iterations=2)

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
        b = 0

        if len(contours) > 1:
            # Find the nth largest contour [n-1][1] only if there is more than one contour
            second_largest_contour = sortedArray[1][1]
            cv2.drawContours(frame, second_largest_contour, -1, (255,0,0), 2)
            b = get_angle(frame, second_largest_contour)
            b = round(b, 2)

        a = get_angle(frame, first_largest_contour)
        a = round(a, 2)
        average_middle = (a+b)/2
        average_middle_string = str(average_middle)
        print(str(average_middle))
        #lancer_socket.sendall(str(a) + "\n")
        if nt.isConnected() and a != 36 and a != 32.5:
            nt.putString('angletogoal', average_middle_string)
    else:
        if nt.isConnected():
            nt.putString('angletogoal', "Not Detected")

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
