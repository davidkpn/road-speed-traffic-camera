# Detect Traffic Speed LIVE

[![](http://img.youtube.com/vi/CtSznvnyVSw/0.jpg)](http://www.youtube.com/watch?v=CtSznvnyVSw "Detect Traffic Speed LIVE")

Detect cars on the road and calculate their speed live from the web,

without any information about the height, lens length, or any detail on the camera.

with only one known parameter, a given road part real-life distance is enough to make the perspective transformation and calculate any distance within the frame.

**bonus - detect red light outlaws.**

live stream tested on https://www.iroads.co.il/%D7%AA%D7%99%D7%A7%D7%99%D7%99%D7%AA-%D7%9E%D7%A6%D7%9C%D7%9E%D7%95%D7%AA/

Gan Yavne Road No. 4

## Calculate Car's speed from an unknown perspective

The titled camera changes the view perspective and therefore manipulating the viewed distance.

Half of the screen will contain less than half of the actual view.

thanks to linear algebra, we can transform one perspective to another.

in the real world, there are parallel lines, such as straight road lines.

but since a camera has a tilt, those lines aren't parallel for the viewer,

therefore these lines collide.

and the collision point is the perspective viewpoint, like the horizon.

an infinite point of view.

when looking on a ship sailing in the sea getting farther from the coast, it becomes so small that it disappears.

for this reason, I've drawn the real-life parallel lines.

calculate their linear equation and calculate the collision point of them.

this point called the viewpoint.

base on this information, the distance between two different points to one point share the perspective to the real distance between them.

and since we've got the real distance (google maps), we can calculate any point on the line by substracting the two locations.

The mathematical calculating explained in the vectors file.

![Perspective lines](https://github.com/davidkpn/road-speed-traffic-camera/blob/master/arrows.png "Perspective lines, View point is out of view")

The green lines are parallel in real life.

## Detecting Incoming Cars

Two options to obtain the detection -

1. deep learning model to detect object location on the screen.

2. substracting two following images, since the camera is still the difference is the moving object in the frame. Using the computer vision gaussian blur and thresholding the white pixels, I've Isolated the cars from foreign objects.

## Track speed

Every detected car saved as an object and tracked by the Lucas Kanade optical flow algorithm.

if two cars detected on the same vehicle, it wouldn't save the latter.

Calculating the difference between the previous position to current for each car divided bypassed time, results in the speed.

but this calculation isn't accurate for the short-term, because the live feed contains bad stream frames which make these small mistakes.

this issue fixed by balancing the speed, calculating the weighted average for previous 15-speed inputs.

The latter got a higher weight while the first or the oldest got the lowest weight. Therefore speed jumps won't affect much the result.

and the algorithm is more accurate.

## Red light outlaws

By isolating HSV colors from a frame, it is possible to get the pixels where the range of colors appears.

Therefore given the traffic lights region, I've separated all the red and green colors.

I have calculated their area in the traffic lights and the higher area defines which color on the light.

When the light is waving, it means the green light or green permission is still on.

When the red light is on, any car enters the intersection from the light side will be considered as an outlaw driver.
