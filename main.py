from imageai.Detection import ObjectDetection
import numpy as np
import cv2
import os
import time
from park_calc import find_space, cut_parking

execution_path = os.getcwd()


def get_car_boxes(frame):
    car_boxes = []
    detections = (detector.detectCustomObjectsFromImage(custom_objects=custom, input_type="array", input_image=np.array(frame), output_type="array", minimum_percentage_probability=18))[1]

    for eachObject in detections:
        car_boxes.append(eachObject["box_points"])

    return np.array(car_boxes)


VIDEO_SOURCE = "test_images/parking1.flv"

detector = ObjectDetection()
detector.setModelTypeAsRetinaNet()
detector.setModelPath( os.path.join(execution_path , "resnet50_coco_best_v2.1.0.h5"))
detector.loadModel()

custom = detector.CustomObjects(bicycle=True, car=True, motorcycle=True, bus=True, truck=True, boat=True, bear=False) #объекты, которые должна искать нейронка

video_capture = cv2.VideoCapture(VIDEO_SOURCE)

spf = 0

while video_capture.isOpened():
    success, frame = video_capture.read()
    if not success:
        break

    if spf > 0:
        spf -= 1 / video_capture.get(cv2.CAP_PROP_FPS)
        continue

    t0 = time.time()

    rgb_image = frame[:, :, ::-1]

    car_boxes = get_car_boxes(rgb_image) #координаты коробок с машинами

    for car in car_boxes:
        x1, y1, x2, y2 = car
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)

    car_boxes = cut_parking(car_boxes, 0)
    spaces = find_space(car_boxes, 0)
    for space in spaces:

        x, y = space
        cv2.rectangle(frame, (x, y), (x, y), (0, 0, 255), 20)

    #если понадобится выводить на экран обработанное изображение и информацию про каждый объект в консоль, то можно вместо вызова get_car_boxes вставить этот код

    print(car_boxes)
    for car in car_boxes:
        x1, y1, x2, y2 = car
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 3)

    cv2.imshow('Video', frame) #перепутаны синий и красный каналы

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    spf = time.time() - t0


video_capture.release()
cv2.destroyAllWindows()
