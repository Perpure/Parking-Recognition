import numpy as np
from shapely.geometry import Polygon

PARKS = [[(527, 569), (592, 515), (1412, 701), (1537, 815)]]

PARKS_POLYGONS = [Polygon(x) for x in PARKS]

def make_polygon(car):
    y1, x1, y2, x2 = car
    return Polygon([(x1, y1), (x1, y2), (x2, y2), (x2, y1)])

def cut_parking(cars, park):
    parked_cars = []
    for car in cars:
        car_poly = make_polygon(car)
        intersec = car_poly.intersection(park).area
        if intersec / car_poly.area > 0.6:
            parked_cars.append(car)
    return np.array(parked_cars)
