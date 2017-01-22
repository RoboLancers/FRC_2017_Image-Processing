import cv2


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

    '#Draws contour on the image'

    @staticmethod
    def draw_contours(image, largestContour, secondLargestContour):
        x, y, w, h = cv2.boundingRect(largestContour)
        cv2.drawContours(image, largestContour, -1, (255, 0, 0), 2)
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        x, y, w, h = cv2.boundingRect(secondLargestContour)
        cv2.drawContours(image, secondLargestContour, -1, (255, 0, 0), 2)
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    '#Create a window for the trackbars'
    cv2.namedWindow("Trackbars", cv2.WINDOW_NORMAL)

    '#Create trackbars to filter image'
    cv2.createTrackbar("Hue Lower", "Trackbars", 0, 180, do_nothing())
    cv2.createTrackbar("Hue Upper", "Trackbars", 180, 180, do_nothing())

    cv2.createTrackbar("Saturation Lower", "Trackbars", 0, 255, do_nothing())
    cv2.createTrackbar("Saturation Upper", "Trackbars", 255, 255, do_nothing())

    cv2.createTrackbar("Value Lower", "Trackbars", 0, 255, do_nothing())
    cv2.createTrackbar("Value Upper", "Trackbars", 255, 255, do_nothing())

    camera = cv2.VideoCapture(0)

    while True:
        # Define both the lower and upper boundary of the ball tracking
        greenLower = (cv2.getTrackbarPos("Hue Lower", "Trackbars"), cv2.getTrackbarPos("Saturation Lower", "Trackbars"),
                      cv2.getTrackbarPos("Value Lower", "Trackbars"))
        greenUpper = (cv2.getTrackbarPos("Hue Upper", "Trackbars"), cv2.getTrackbarPos("Saturation Upper", "Trackbars"),
                      cv2.getTrackbarPos("Value Upper", "Trackbars"))

        # Read the frame from the camera
        (grabbed, frame) = camera.read()

        # Process the image to get a mask
        maskImage = process_image(frame, greenLower, greenUpper)

        # Find the largest and second largest contour
        firstContour, secondContour = find_contours(maskImage)

        # Draws the contours on the mask
        draw_contours(maskImage, firstContour, secondContour)

        # Shows the image to the screen
        cv2.imshow("Frame", frame)
        cv2.imshow("Mask Frame", maskImage)

        key = cv2.waitKey(1) & 0xFF

        # If q key is pressed then we quit
        if key == ord("q"):
            break

    # Clean up the camera and close all windows
    camera.release()
    cv2.destroyAllWindows()
