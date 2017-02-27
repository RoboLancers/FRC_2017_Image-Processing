from MultithreadVideoStream import MultithreadVideoStream
from SetupUtil import *
from VisionUtils import *

'''Create threaded video stream'''
camera = MultithreadVideoStream('http://10.3.21.2:1180/?action=stream').start()
# camera = MultithreadVideoStream(0).start()

args = parse_arguments()

nt = setUpNetworkTables()

MIN_PERIMETER = 50

focal_length = 887.9928588867188

hsv_values = readHSV()

while True:

    green_lower = np.array([int(hsv_values[0][1]), int(hsv_values[2][1]), int(hsv_values[4][1])])
    green_upper = np.array([int(hsv_values[1][1]), int(hsv_values[3][1]), int(hsv_values[5][1])])

    '''Read frame from thread camera'''
    frame = camera.read()

    while frame is None:
        frame = camera.read()

    '''Process the image to get a mask'''
    mask = preprocess_image(frame, green_lower, green_upper)

    '''Find the contour in the mask'''
    contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

    contours = [x for x in contours if not cv2.arcLength(x, True) < MIN_PERIMETER]

    '''Only if we find both contours do we continue'''
    if len(contours) > 1:

        sortArray = findAndSortContourArea(contours=contours)

        '''Find the largest contour'''
        first_largest_contour = max(contours, key=cv2.contourArea)

        '''Find the nth largest contour [n-1][1] only if there is more than one contour
           So here we find the second largest'''
        second_largest_contour = sortArray[1][1]

        x, y, w, h = cv2.boundingRect(first_largest_contour)
        x1, y1, w1, h1 = cv2.boundingRect(second_largest_contour)

        if w > h and w1 > h1:
            degrees = degreesAboveCamera(y)
            distance = distanceFromBoilerCamera(degrees)

            if args["print"] > 0:
                print("Distance: ", str(distance))

            putInNetworkTable(nt, "Distance To Boiler", str(distance))

    else:
        putInNetworkTable(nt, 'Distance To Boiler', 'Not Detected')

    if args["display"] > 0:
        '''Shows the images to the screen'''
        cv2.imshow("Frame", frame)
        cv2.imshow("Mask Frame", mask)

        if check_key_pressed():
            break

'''Clean up the camera and close all windows'''
camera.release()
cv2.destroyAllWindows()
