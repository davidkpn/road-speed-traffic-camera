'''
Generate important data of road image.
Set the number of lanes you are calculating
Set the real life distance of lane



Avleim 70, 781
from cross-road to next light-stop line 173m

Gan Yavne
from cross-road to 4th arrows line 60m
'''


import sys
import cv2
import numpy as np
import mss
import pickle
from vectors import collision_point

def mouse_event(event, x, y, flags, params):
    global method
    if method == 0:
        generate_view_point(event, x, y)
    elif method == 1:
        generate_lane_view_lines(event, x, y)
    elif method == 2:
        generate_lane_roi(event, x, y)
    elif method == 3:
        generate_general_roi(event, x, y)
    elif method > 3:
        pass

'''

Draw 2 lines which in real life are parallel but on camera collides.
one both line has been drawn, generate view point
'''
def generate_view_point(event, x, y):

    global method, view_point
    if event == cv2.EVENT_LBUTTONDOWN:
        if not view_point_lines or len(view_point_lines[-1]) >= 2:
            view_point_lines.append([(x, y)])
        else:
            view_point_lines[-1].append((x, y))
            cv2.line(new_frame, view_point_lines[-1][0], view_point_lines[-1][1], (0,255,0), 2)
            if len(view_point_lines) >= 2:
                x, y = collision_point(np.array(view_point_lines[0]), np.array(view_point_lines[1]))
                view_point = (int(x),int(y))
                cv2.circle(new_frame, view_point, 3, (0,255,0), -1)
                cv2.putText(new_frame, "v=" + str(view_point), view_point, font, 1, (0, 255, 0), 1, cv2.LINE_AA)
                method = 1
    if view_point_lines:
        if len(view_point_lines[-1]) < 2:
            cv2.line(frame, view_point_lines[-1][0], (x, y), (255,0,0), 2)

'''
Params -
        mouse event, mouse x and y positions.

Draw lane's line, the accuracy calculated by the distance from the white line.
Which is the straight line from the view point to the start point.
The distance should be low.
params:
'''
def generate_lane_view_lines(event, x, y):

    global method
    if event == cv2.EVENT_LBUTTONDOWN:
        if not lane_view_lines or len(lane_view_lines[-1]) >= 2:
            lane_view_lines.append([(x, y)])
        else:
            lane_view_lines[-1].append((x, y))
            if len(lane_view_lines[-1]) >= 2:
                s_p, e_p = lane_view_lines[-1]
                cv2.line(new_frame, s_p, e_p, (255,0,0), 1)
                cv2.putText(new_frame, "start point: " + str(s_p), s_p, font, 1, (255,130,130), 2, cv2.LINE_AA)
                cv2.putText(new_frame, "end point: " + str(e_p), e_p, font, 1, (255,130,130), 2, cv2.LINE_AA)
                # After selecting all the lanes, change method to select lane's roi
                if len(lane_view_lines) >= n_lanes:
                    method = 2

    # Draw on all mouse events, draw start point condition
    if not lane_view_lines or len(lane_view_lines[-1])>=2:
        cv2.circle(frame, (x, y), 3, (0,0,255), -1)
        cv2.line(frame, (x, y), view_point, (0,0,255), 2)
        cv2.putText(frame, f"start point lane{len(lane_view_lines) + 1}", (x, y), font, 1, (0, 0, 255), 2, cv2.LINE_AA)
    # Draw end point condition
    elif lane_view_lines:
        cv2.circle(frame, (x, y), 5, (255,0,0), -1)
        # Draw line from start point to current point
        cv2.line(frame, (x, y), lane_view_lines[-1][0], (0,0,255), 2)
        # Draw line from current point to view point
        cv2.line(frame, (x, y), view_point, (0,0,255), 2)
        # Draw perfect line to copy
        cv2.line(frame, view_point, lane_view_lines[-1][0], (255,255,255), 1)
        cv2.putText(frame, f"end point lane{len(lane_view_lines) + 1 - len(lane_view_lines[-1])}", (x, y), font, 1, (0, 0, 255), 2, cv2.LINE_AA)

'''
Params -
        mouse event, mouse x and y positions.

Draw lane's poligon as region of interest
params:
'''
def generate_lane_roi(event, x, y):
    global method, new_frame
    if event == cv2.EVENT_LBUTTONDOWN:
        if not rol or len(rol[-1]) >= 4:
            rol.append([(x, y)])
            cv2.circle(new_frame, (x, y), 3, (0,0,0), -1)
        else:
            rol[-1].append((x, y))
            cv2.circle(new_frame, (x, y), 3, (0,0,0), -1)
            if len(rol[-1]) >= 4:
                cv2.putText(new_frame, "lane " + str(len(rol) + 1), rol[-1][0], font, 1, (255,130,130), 2, cv2.LINE_AA)
                # After selecting all the lanes, change method to select lane's roi
                if len(rol) >= n_lanes:
                    method = 3

def generate_general_roi(event, x, y):
    global method, new_frame
    if event == cv2.EVENT_LBUTTONDOWN:
        if not rol:
            general_roi.append([(x, y)])
            cv2.circle(new_frame, (x, y), 3, (0,0,0), -1)
        else:
            general_roi.append((x, y))
            cv2.circle(new_frame, (x, y), 3, (0,0,0), -1)
            if len(rol[-1]) >= 4:
                cv2.putText(new_frame, "General ROI ", general_roi, font, 1, (255,130,130), 2, cv2.LINE_AA)
                method = 4

def poly_roi(frame, vertices):
    vertices = np.array([vertices], np.int32)
    mask = np.zeros_like(frame)
    cv2.fillPoly(mask, vertices, (255,255,255))
    return cv2.bitwise_and(frame, mask)

# Initial cv2 objects
cv2.namedWindow("Frame")
# Initialize the screen recording
mon = {"top": 0, "left": 0, "width": 1920, "height": 1080}
sct = mss.mss()
# Set Road name
road_name = "Gan-Yanve"
# Grab screen
frame = np.asarray(sct.grab(mon))
# Define a copy of the screen to keep drawing
new_frame = frame.copy()
# Set mouse call back function
cv2.setMouseCallback("Frame", mouse_event)
# Number of lanes
n_lanes = 5
# In real life lane length in meters
irl_lane_length = 60
# Collision point of two irl parallel lines
view_point = None

view_point_lines = []

lane_view_lines = []
# Region of Lanes
rol = []
# General roi, the whole region where you would like to compute information
general_roi = []
# Drawing methods
methods = ['generate_view_point','generate_lane_view_lines']
# current_method to execute on mouse click
method = 0

# Draw generator info
font_scale = 1
thickness = 1
margin = 5
font = cv2.FONT_HERSHEY_SIMPLEX
text = f"Road:{road_name}, number of lanes:{n_lanes}"
text_size = cv2.getTextSize(text, font, font_scale, thickness)
text_width = text_size[0][0]
text_height = text_size[0][1]
line_height = text_height + text_size[1] + margin
cv2.rectangle(new_frame, (20, 0), (25 + text_width, line_height), (255,255,255),cv2.FILLED)
cv2.putText(new_frame, text, (25,25), font, font_scale, (32, 32, 32), thickness, cv2.LINE_AA)

while True:

    cv2.imshow("Frame", frame)

    frame=new_frame.copy()

    # quit on 'q' pressed down
    if cv2.waitKey(1) == ord('q'):
        break


data = {
'road_name': road_name,
'n_lanes': n_lanes,
'irl_lane_length': irl_lane_length,
'view_point': view_point,
'view_point_lines': view_point_lines,
'lane_view_lines': lane_view_lines,
'region_of_lanes': rol,
'general_roi': general_roi
}
with open(f'{road_name}.pickle', 'wb') as handle:
    pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
