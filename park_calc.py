import numpy as np
from shapely.geometry import Polygon

PARKS = [[(527, 569), (592, 515), (1412, 701), (1537, 815)], #1
         [(200, 389), (263, 367), (884, 530), (802, 596)]] #2 left

PIX_PER_CAR = [73, 40]

PARKS_POLYGONS = [Polygon(x) for x in PARKS]

def rect_area(arr):
    x1, y1, x2, y2 = arr
    return (x2 - x1) * (y2 - y1)

def width(arr):
    x1, _, x2, _ = arr
    return x2 - x1

def height(arr):
    _, y1, _, y2 = arr
    return y2 - y1

def center_rect(r):
    x1, y1, x2, y2 = r
    return x1 + (x2 - x1) / 2, y1 + (y2 - y1) / 2

def dist_dot(d1, d2):
    x1, y1 = d1
    x2, y2 = d2
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

def make_polygon(car):
    x1, y1, x2, y2 = car
    return Polygon([(x1, y1), (x1, y2), (x2, y2), (x2, y1)])

def cut_parking(cars, id):
    park = PARKS_POLYGONS[id]
    parked_cars = []
    for car in cars:
        car_poly = make_polygon(car)
        intersec = car_poly.intersection(park).area
        if intersec / car_poly.area > 0.4:
            parked_cars.append(car)
    if parked_cars == []:
        return np.array([])
    parked_cars = np.array(parked_cars)
    parked_cars = parked_cars[parked_cars[:, 0].argsort()]
    med = np.median(np.apply_along_axis(rect_area, 1, parked_cars))
    delta_w = np.median(np.apply_along_axis(width, 1, parked_cars)) * 0.5
    delta_h = np.median(np.apply_along_axis(height, 1, parked_cars)) * 0.5
    i = 0
    while i < len(parked_cars) - 1:
        x1, y1, _, _ = parked_cars[i, :]
        x2, y2, _, _ = parked_cars[i + 1, :]
        if (x2 - x1 < delta_w) and (y2 - y1 < delta_h):
            if (abs(rect_area(parked_cars[i]) - med) <
                abs(rect_area(parked_cars[i + 1]) - med)):
                parked_cars = np.delete(parked_cars, i + 1, 0)
            else:
                parked_cars = np.delete(parked_cars, i, 0)
        else:
            i += 1
    return parked_cars

def find_space_between_cars(d1, d2, delta):
    x, y = d1
    xf, yf = d2
    if (x > 900):
        delta += 4
    else:
        delta -= 7 # because of perspective

    spaces = np.empty(shape=[0, 2], dtype=int)
    if (xf < x):
        return spaces

    dist = dist_dot((x, y), (xf, yf))
    vec_x = (xf - x) / dist
    vec_y = (yf - y) / dist
    n = int(dist // delta)

    if n == 0:
        return spaces

    if n > 6:
        delta += 5
        n = int(dist//delta)

    step = dist / n / 2
    buf = np.empty(shape=[1, 2], dtype=int)
    for _ in range(n):
        x += vec_x * step
        y += vec_y * step
        buf[0] = int(x), int(y)
        spaces = np.concatenate((spaces, buf))
        x += vec_x * step
        y += vec_y * step
    return spaces

def find_space(cars, id):
    park = PARKS[id]
    delta = PIX_PER_CAR[id]
    spaces = np.empty(shape=[0, 2], dtype=int)
    x, y = park[0]
    if len(cars) == 0:
        xf, yf = park[2]
        return find_space_between_cars((x, y - 20), (xf, yf + 40), delta)
    car = cars[0, :]
    x1, y1, x2, y2 = car
    xf, yf = x1, y1 + (y2 - y1) / 2
    spaces = np.concatenate((spaces, find_space_between_cars((x, y - 20), (xf, yf), delta)))
    for i in range(len(cars) - 1):
        car1 = cars[i, :]
        car2 = cars[i + 1, :]
        x1, y1, x2, y2 = car1
        x3, y3, x4, y4 = car2
        x, y = x2, y1 + (y2 - y1) / 2
        xf, yf = x3, y3 + (y4 - y3) / 2
        spaces = np.concatenate((spaces, find_space_between_cars((x, y), (xf, yf), delta)))


    xf, yf = park[2]
    car = cars[len(cars) - 1, :]
    x1, y1, x2, y2 = car
    x, y = x2, y1 + (y2 - y1) / 2
    spaces = np.concatenate((spaces, find_space_between_cars((x, y), (xf, yf + 40), delta)))
    return spaces
