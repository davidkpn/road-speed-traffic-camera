import numpy as np
from matplotlib import path
from shapely.geometry import Polygon

'''
Params -
        u, v are vectors representing lines ( vector = [(x1,y1), (x2,y2)] )
Return - norm of the vector which is the distance between the two points the vector represented by.

dot = Scalar multiplication in R^2 (Inner products of the Euclidean space)
norm(u-v) => ||u-v|| = sqrt((u-v) dot (u-v)) = sqrt((x1-x2)**2 + (y1-y2)**2)
'''
def dist(u, v):
    return np.linalg.norm(np.array(u, np.float32)-np.array(v, np.float32))

def linear_t_mirror_y(v):
    p1, p2 = v.copy()
    tmp = p1[1]
    p1[1] = p2[1]
    p2[1] = tmp
    return np.array((p1, p2))

'''
Params -
        v is vector representing line ( vector = (x1,y1) )
Return - linear slope
'''
def slope(v):
    p1, p2 = v
    dx, dy = p2 - p1
    return dy/dx

'''
Params -
        v is vector representing line ( vector = [(x1,y1), (x2,y2)] )

Return - the slope and the bias of the linear equation - y = mx + b || f(x) = mx + b

y = mx + b
m = slope
b = bias
return m, b
'''
def linear_eq(v):
    p1, p2 = v
    m = slope(v)
    b = p1[1] - m*p1[0]
    return(m, b)

'''
Params -
        u, v are vectors representing lines ( vector = [(x1,y1), (x2,y2)] )

Return - Collision point in space

when two lines got the same x, y it is a collision point.
assuming two lines got the same y value, calculate the x point.
Place the x in one of the linear equations and calculate the y value for that x.
'''
def collision_point(v, u):
    m1, b1 = linear_eq(v)
    m2, b2 = linear_eq(u)
    x = (b2-b1)/(m1-m2)
    y = x*m1 + b1
    return x, y

'''
Params -
        a, b, c, v are points in the Euclidean space
        ac_meters real number representing the real life distance between point a and c

Return - the distance from b to c in real life measurement

let a,b,c,v points belongs to one line.
a = start point
b = wanted distance start point
c = end point
v = horizon perspective point
https://en.wikipedia.org/wiki/Cross-ratio
https://math.stackexchange.com/questions/1216298/how-to-calculate-true-lengths-from-perspective-projection
'''
def irl_distance(a, b, c, ac_meters, v):
    ac_pixel = dist(c, a)
    bc_pixel = dist(c, b)
    av_pixel = dist(v, a)
    bv_pixel = dist(v, b)

    bc_meters = ac_meters * (bc_pixel * av_pixel) / (ac_pixel*bv_pixel)
    return bc_meters

'''
Params -
        u, v are vectors representing lines ( vector = [(x1,y1), (x2,y2)] )

Return - vector representing the middle line connecting between the center of _u and _v

given two lines, find the center of each
returns tuple of (first line center point, second line center point)
'''
def center_line(u, v):
    mid_lane = []
    for p1, p2 in [u,v]:
        mid_lane.append((int((p1[0] + p2[0])/2) , int((p1[1] + p2[1])/2)))
    return mid_lane

'''
Params -
    polygon - poly's coordinates [(x1, y1), (x2, y2), ...]
    points - list of points
Return - Boolean list, the same size and shape as the points list

Boolean array for each cell in array representing a point.
True value means the poly contains the point, False otherwise.
'''
def poly_contains(polygon, points):
    p = path.Path(polygon)
    return p.contains_points(points)

def polies_intersect(poly1, poly2):
    #from shapely.geometry import Polygon
    p1 = Polygon(poly1)
    p2 = Polygon(poly2)
    return p1.intersects(p2)

if __name__ == "__main__":
    # שתי וקטורים נחתכים בנקודת אופק
    u1 = np.array([(1130, 503), (1182, 404)])
    u2 = np.array([(1272, 506), (1288,402)])
    # u1_tag = linear_t_mirror_y(u1)
    # u2_tag = linear_t_mirror_y(u2)
    print(collision_point(u1, u2))
