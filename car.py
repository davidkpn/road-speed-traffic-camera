import numpy as np
import cv2
from vectors import irl_distance, poly_contains, polies_intersect, dist
import time

class Road:
    '''
    Lucas Kanade params (lk_params)
        winSize => movement check between the two frames
        maxLevel => The pyramid pictures which size is decreased, makes the detection easier since there is less movement
        this for level 1: level_one = cv2.pyrDown(frame)
        this for level 2: level_two = cv2.pyrDown(level_one)
        and so on..
        criteria => the calculation creterion , change params to match different flows.
        currently properties are fine with the clear road
    '''
    _lk_params = dict(winSize = (21, 21),
                     maxLevel = 4,
                     criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
    def __init__(self, data, cars=[], old_points=np.empty((0,2), np.float32),speed_limit=50):
        self.cars = cars
        self.old_points = old_points
        self.speed_limt = speed_limit
        self.road_name = data['road_name']
        self.n_lanes = data['n_lanes']
        self.irl_lane_length = data['irl_lane_length']
        self.view_point = data['view_point']
        self.view_point_lines = data['view_point_lines']
        self.lane_view_lines = data['lane_view_lines']
        self.rol = data['region_of_lanes']
        self.general_roi = data['general_roi']

    # detecting which lane a point of car belongs.
    # return the car point which not in the general roi as potential deleted cars
    def lane_detector(self, points):
        for lane_index, lane in enumerate(self.rol):
            for j, in_lane in enumerate(poly_contains(lane, points)):
                if in_lane:
                    self.cars[j].lane = lane_index
        # find all the cars outside the relevant region, and mark to delete
        cars_to_delete = np.where(np.array(poly_contains(self.general_roi, points))==False)[0]
        return cars_to_delete.tolist()#.flatten().tolist()

    def delete_cars(self, cars_indices):
        self.old_points = np.delete(self.old_points, cars_indices, axis=0)
        self.cars = [c for i, c in enumerate(self.cars) if i not in cars_indices]

    def add_car(self, position, current_speed=0, lane=0, box=None):
        # add box for car
        self.cars.append(Car(position, current_speed, lane, box))
        self.old_points = np.append(self.old_points, np.array([position],  dtype=np.float32), axis=0)

    def update_speed_position(self, old_gray_frame, curr_gray_frame, old_time):
        curr_frame_t = time.time()
        cars_to_delete = []
        if not self.cars:
            return
        new_points, status, error = cv2.calcOpticalFlowPyrLK(old_gray_frame, curr_gray_frame, self.old_points, None, **Road._lk_params)
        cars_to_delete += self.lane_detector(new_points)
        for i, car in enumerate(self.cars):
            if not status[i][0]:
                cars_to_delete.append(i)
                continue
            # calculate the real distance from new point to c point
            a1, c1 = self.lane_view_lines[car.lane][0], self.lane_view_lines[car.lane][1]
            b1 = new_points[i]
            dn = irl_distance(a1, b1, c1, self.irl_lane_length, self.view_point)
            # calculate the real distance from old point to c point
            a2, c2 = self.lane_view_lines[car.lane][0], self.lane_view_lines[car.lane][1]
            b2 = self.old_points[i]
            do = irl_distance(a2, b2, c2, self.irl_lane_length, self.view_point)
            # calculate speed by subtracting old point distance and new one devided by the time took to make the distance and times 3.6 ( convert to km/h)
            speed = (do - dn) * 3.6 / (curr_frame_t - old_time)
            car.add_speed(speed)
            car.position = new_points[i]
        self.old_points = new_points
        self.delete_cars(cars_to_delete)


class Car:
    _id = 0
    _standing_sill_threshold = 10 

    def __init__(self, position, current_speed=0, lane=0, box=None, normalized_num=10):
        self.id = Car._id
        self.position = position
        self.current_speed = current_speed
        self.lane = 0
        self.box = box # a width, height tuple
        self.speed_array = np.concatenate(([0.0]*(normalized_num-1), [current_speed]), axis=0)
        self.weights = [w*100/normalized_num for w in range(1, normalized_num+1)]

        Car._id += 1

    def add_speed(self, speed):
        self.speed_array = np.concatenate((self.speed_array[1:], [speed]), axis=0)
        self.current_speed = self.balanced_speed()

    '''
    Reduce speed inaccurate value by calculating weighted average of the last 15 speeds.
    '''
    def balanced_speed(self):
        return np.average(self.speed_array, weights=self.weights)

    def in_roi(self, poly):
        return poly_contains(poly, [self.position])

    def dist(self, point):
        return dist(self.position, point)

if __name__ == "__main__":
    c = Car((0, 0), 1)
    c.add_speed(13.1)
    print(c.current_speed)
