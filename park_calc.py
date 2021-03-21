import numpy as np
from shapely.geometry import Polygon

PARKS = [[(527, 569), (592, 515), (1412, 701), (1537, 815)]]

PARKS_POLYGONS = [Polygon(x) for x in PARKS]

def rect_area(arr):
    x1, y1, x2, y2 = arr
    return (x2 - x1) * (y2 - y1)

def width(arr):
    x1, y1, x2, y2 = arr
    return x2 - x1

def make_polygon(car):
    x1, y1, x2, y2 = car
    return Polygon([(x1, y1), (x1, y2), (x2, y2), (x2, y1)])

def cut_parking(cars, park):
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
    delta = np.median(np.apply_along_axis(width, 1, parked_cars)) * 0.3
    answer = []
    i = 0
    while i < len(parked_cars) - 1:
        x1, _, _, _ = parked_cars[i, :]
        x2, _, _, _ = parked_cars[i + 1, :]
        if (x2 - x1 < delta):
            if (abs(rect_area(parked_cars[i]) - med) <
                abs(rect_area(parked_cars[i + 1]) - med)):
                parked_cars = np.delete(parked_cars, i + 1, 0)
            else:
                parked_cars = np.delete(parked_cars, i, 0)
        else:
            i += 1
    return parked_cars
