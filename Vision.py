import cv2
import numpy as np
import LancerTable
import os

os.system("uvcdynctrl -s 'Exposure, Auto' 1")
os.system("uvcdynctrl -s 'Exposure (Absolute)' 5")


class Vision:
    def do_nothing(self):
        pass

    '#Pre process the image to get the mask'

    @staticmethod
    def process_image(image, lower, upper):
        # Convert the frame to the hsv colorspace
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Creates a mask for the color green
        mask = cv2.inRange(hsv_image, lower, upper)

        # Erode and dilate the mask to remove blobs
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        return mask

    '#Finds the contours in the image'

    @staticmethod
    def find_contours(mask_image):
        # Find the contour in the mask
        contours = cv2.findContours(mask_image.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

        # Create an array to hold all contour area
        area_array = []

        # Only if we find a contour do we continue
        if len(contours) > 0:
            # Find the largest contour
            first_largest_contour = max(contours, key=cv2.contourArea)

            # Fill the array with contour areas
            for i, j in enumerate(contours):
                area = cv2.contourArea(j)
                area_array.append(area)

            # Sort the array based on contour area
            sortedArray = sorted(zip(area_array, contours), key=lambda x: x[0], reverse=True)

            # Find the nth largest contour [n-1][1] only if there is more than one contour
            if len(contours) > 1:
                second_largest_contour = sortedArray[1][1]

            return first_largest_contour, second_largest_contour

    '#Calculate the centoid of the contour'

    @staticmethod
    def calculate_centroid(contour):

        moment = cv2.moments(contour)
        center_x = int(moment["m10"] / moment["m00"])
        center_y = int(moment["m01"] / moment["m00"])

        return center_x, center_y

    '#Draws contour on the image'

    @staticmethod
    def draw_contours(image, contour):
        x, y, w, h = cv2.boundingRect(contour)
        cv2.drawContours(image, contour, -1, (255, 0, 0), 2)
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    '#Find the angle to turn'

    @staticmethod
    def get_angle(frame, contour):
        height, width, channels = frame.shape
        center_x, center_y = Vision.calculate_centroid(contour)

        pixel_offset = width / 2 - center_x;
        angle_offset = 73 * pixel_offset / width
        angle_offset -= 3.5

        print(str(angle_offset))

        return angle_offset


    '#Create a window for the trackbars'
    cv2.namedWindow("Trackbars", cv2.WINDOW_NORMAL)

    '#Create trackbars to filter image'
    cv2.createTrackbar("Hue Lower", "Trackbars", 0, 180, do_nothing())
    cv2.createTrackbar("Hue Upper", "Trackbars", 180, 180, do_nothing())

    cv2.createTrackbar("Saturation Lower", "Trackbars", 0, 255, do_nothing())
    cv2.createTrackbar("Saturation Upper", "Trackbars", 255, 255, do_nothing())

    cv2.createTrackbar("Value Lower", "Trackbars", 0, 255, do_nothing())
    cv2.createTrackbar("Value Upper", "Trackbars", 255, 255, do_nothing())

    nt = LancerTable.get_network_table()

    camera = cv2.VideoCapture(0)
    camera.set(3, 160);
    camera.set(4, 120);

    while True:
        # Define both the lower and upper boundary of the ball tracking
        greenLower = np.array([cv2.getTrackbarPos("Hue Lower", "Trackbars"), cv2.getTrackbarPos("Saturation Lower", "Trackbars"),
                      cv2.getTrackbarPos("Value Lower", "Trackbars")])
        greenUpper = np.array([cv2.getTrackbarPos("Hue Upper", "Trackbars"), cv2.getTrackbarPos("Saturation Upper", "Trackbars"),
                      cv2.getTrackbarPos("Value Upper", "Trackbars")])

        # Read the frame from the camera
        (grabbed, frame) = camera.read()

        # Process the image to get a mask
        mask_image = process_image(frame, greenLower, greenUpper)

        # Find the largest and second largest contour
        first_contour, second_contour = find_contours(mask_image)

        # Draws the contours on the mask
        draw_contours(mask_image, first_contour)
        draw_contours(mask_image, second_contour)

        # Shows the image to the screen
        cv2.imshow("Frame", frame)
        cv2.imshow("Mask Frame", mask_image)

        angle_to_bigger_target = get_angle(mask_image, first_contour)
        angle_to_second_target = get_angle(mask_image, second_contour)

        nt.putNumber("First Angle to Turn", angle_to_bigger_target)

        key = cv2.waitKey(1) & 0xFF

        # If q key is pressed then we quit
        if key == ord("q"):
            break

    # Clean up the camera and close all windows
    camera.release()
    cv2.destroyAllWindows()
