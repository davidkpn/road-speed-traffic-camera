'''
Before -
    prepare the data by running the generate_road_params.py file

1. Detect incoming Cars
2. Track cars and compute Real-Time Real-Life speed
3. Detect Red-light outlaws - disabled

'''
import cv2
import numpy as np
import mss
import time
import pickle
from car import Road
from vectors import poly_contains, dist

# Mouse Function
def select_point(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        # added_point = np.array([x, y],  dtype=np.float32)
        # box = [(x-40,y-40),(x+40,y),(x,y+40),(x+40,y+40)]
        # r.add_car(added_point, current_speed=50, lane=0, box=box)
        print(x,y)

def roi(img, vertices):
    vertices = np.array([vertices], np.int32)
    #blank mask:
    mask = np.zeros_like(img)
    # fill the mask
    cv2.fillPoly(mask, vertices, (255,255,255))
    # now only show the area that is the mask
    masked = cv2.bitwise_and(img, mask)
    return masked

def green_light(img, light_roi):
    img = roi(img, light_roi)
    hsv_frame =  cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # Red color hsv scheme
    low_red = np.array([161, 155, 83])
    high_red = np.array([179,255,255])
    # Mask only pixels in between low_red and high_red value
    red_mask = cv2.inRange(hsv_frame, low_red, high_red)
    # Green color hsv scheme
    low_green = np.array([25, 52, 72])
    high_green = np.array([102, 255, 255])
    # Mask only pixels in between low_green and high_green value
    green_mask = cv2.inRange(hsv_frame, low_green, high_green)

    contours_red, hierarchy = cv2.findContours(red_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours_green, hierarchy = cv2.findContours(green_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    green_light = sum([cv2.contourArea(c) for c in contours_green])
    red_light = sum([cv2.contourArea(c) for c in contours_red])

    return green_light >= red_light

def in_roi(poly, point):
    return poly_contains(poly, [point])[0]

if __name__ == "__main__":
    # import generated data
    with open('Gan-Yanve.pickle', 'rb') as handle:
        data = pickle.load(handle)

    # Hard code light and crossroad regions
    light_roi = [(1794 ,495), (1794 ,476), (1786 ,477), (1786 ,494)]
    crossroad_roi = [(1819 ,563),(1519 ,536),(1506 ,549),(1820 ,578)]
    # speed limit of the current road (gan yavne)
    speed_limt = 60
    # define Road Object
    r = Road(data, speed_limit=speed_limt)
    # Initialize screen recorder
    # Initialize CV objects
    cv2.namedWindow("Frame")
    # assign the click event on the cv2 window
    cv2.setMouseCallback("Frame", select_point)
    font = cv2.FONT_HERSHEY_SIMPLEX
    cap = cv2.VideoCapture('a.avi')
    # Initialize prev image to calculate properly the optical flow
    _, frame = cap.read()
    old_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #### load any object detection platform and model
    # for this project i've used yolov2 on darkflow adapted to tensorflow
    from darkflow.net.build import TFNet
    options = {
        'model': 'cfg/yolov2.cfg',
        'load': 'bin/yolov2.weights',
        'threshold': .3,
        'gpu': 1.0,
    }
    tfnet = TFNet(options)
    #######
    # Initial loop time
    prev_frame_t = time.time()
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Detect incoming cars
        #################################################################
        # Option 1
        ############################
        results = tfnet.return_predict(frame)
        for result in results:
            tl = (result['topleft']['x'], result['topleft']['y'])
            br = (result['bottomright']['x'], result['bottomright']['y'])
            label = result['label']
            confidence = result['confidence']
            # cv2.rectangle(frame, tl, br, (255,0,0), 5)
            # cv2.putText(frame, label, tl, cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,0), 2)
            c_x = int(tl[0] + (br[0]-tl[0])/2)
            c_y = int(tl[1] + (br[1]-tl[1])/2)
            rect = [int((br[0]-tl[0])/2), int((br[1]-tl[1])/2)]
            if dist(tl, br) > 300:
                continue
            close_point = False
            cv2.circle(frame, (c_x, c_y), 2, (0,0,255), -1)

            for car in r.cars:
                close_point = car.dist((c_x, c_y)) < 75
                if close_point:
                    car.box = rect
                    break
            if not close_point: r.add_car((c_x, c_y), current_speed=50, lane=0, box=rect)
        ####
        # OR any deep-learning object detection like yolov3, ssd, inception or exception
        # Example for yolov3 could be found in the yolo folder
        # for good performence required tensorflow on gpu
        ####

        # # Option 2
        # ############################
        # substracted = cv2.subtract(old_gray, gray_frame)
        # blur = cv2.GaussianBlur(substracted, (35, 35), 0)
        # _, thresh = cv2.threshold(blur,9,255,cv2.THRESH_BINARY)
        # ######################################################
        # # kernel = np.ones((15,15),np.uint8)
        # # dilation = cv2.dilate(thresh,kernel,iterations = 1)
        # # cv2.imshow("gaga", dilation)
        # ######################################################
        # contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # for c in contours:
        #     # set area limit to consider as human movement object
        #     if(cv2.contourArea(c) < 100): break
        #     # compute the center of the contour
        #     M = cv2.moments(c)
        #     if M["m00"] == 0: M["m00"] = 1
        #     cX = int(M["m10"] / M["m00"])
        #     cY = int(M["m01"] / M["m00"])
        #     # compute the rectangle of the contour
        #     (x,y,w,h) = cv2.boundingRect(c)
        #     cv2.rectangle(frame, (x,y), (x+w,y+h), (255, 0, 0), 2)
        #     cv2.circle(frame, (cX, cY), 2, (0,0,255), -1)
        #     rect = [int(w/2), int(h/2)]
        #
        #     # detect car enter intersect when red light is on!
        #     # if not green_light(frame, light_roi) and in_roi(crossroad_roi, (cX, cY)):
        #     #     print(f"car crossed in red light")
        #     #     cv2.imshow(f"car", frame[x:x+w, y:y+h])
        #     ####################################################
        #     close_point = False
        #     for car in r.cars:
        #         close_point = car.dist((cX, cY)) < 75
        #         if close_point:
        #             break
        #     if not close_point: r.add_car((cX, cY), current_speed=50, lane=0, box=rect)
        #################################################################

        # Track and Speed control
        #################################################################
        if len(r.cars) > 0:
            r.update_speed_position(old_gray, gray_frame, prev_frame_t)
            for car in r.cars:
                # Standing still threshold, trying to avoid off car points
                if sum(car.speed_array[-10:]) <= 10:
                    continue
                pos = tuple(car.position.astype(int))
                color = (0, 255, 0) if car.current_speed < r.speed_limt else (0, 0, 255)
                cv2.putText(frame, str(round(car.current_speed, 1)) + "km/h", pos, font, .7, color, 1, cv2.LINE_AA)
                cv2.circle(frame, pos, 2, (0,0,255), -1)
                tl = (pos[0] - car.box[0], pos[1] - car.box[1])
                br = (pos[0] + car.box[0], pos[1] + car.box[1])
                # cv2.rectangle(frame, tl, br, (0, 255, 0), 2)
        #################################################################

        print(1 / (time.time() - prev_frame_t))

        old_gray = gray_frame

        prev_frame_t = time.time()

        cv2.imshow("Frame", frame)

        key = cv2.waitKey(1)
        if key== 27:
            break

    cap.release()
    cv2.destroyAllWindows()
