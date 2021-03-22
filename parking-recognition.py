from imageai.Detection import ObjectDetection
import numpy as np
import cv2
import os
import time
from park_calc import find_space, cut_parking
import tensorflow as tf




def get_car_boxes(frame, detector, custom):
    car_boxes = []
    detections = (detector.detectCustomObjectsFromImage(custom_objects=custom, input_type="array", input_image=np.array(frame), output_type="array", minimum_percentage_probability=18))[1]

    for eachObject in detections:
        car_boxes.append(eachObject["box_points"])

    return np.array(car_boxes)


VIDEO_SOURCE1 = "https://s2.moidom-stream.ru/s/public/0000010491.m3u8"


def process(VIDEO_SOURCE):
    physical_devices = tf.config.list_physical_devices('GPU') 
    tf.config.experimental.set_memory_growth(physical_devices[0], True)

    execution_path = os.getcwd()

    detector = ObjectDetection()
    detector.setModelTypeAsRetinaNet()
    detector.setModelPath( os.path.join(execution_path , "resnet50_coco_best_v2.1.0.h5"))
    detector.loadModel()

    custom = detector.CustomObjects(bicycle=True, car=True, motorcycle=True, bus=True, truck=True, boat=True) #объекты, которые должна искать нейронка

    video_capture = cv2.VideoCapture(VIDEO_SOURCE)

    spf = 0
    video_spf = 1 / 25 #узнать фпс видео - video_capture.get(cv2.CAP_PROP_FPS)
    prev_cars = []
    change_counter = 0

    while video_capture.isOpened():
        success, frame = video_capture.read()
        if not success:
            break

        t0 = time.time()

        if spf > video_spf:
            if spf > video_spf * 2:
                spf -= video_spf
                continue

            t0 -= spf - video_spf

        elif video_spf > spf:
            time.sleep(video_spf - spf)

        rgb_image = frame[:, :, ::-1]

        car_boxes = get_car_boxes(rgb_image, detector, custom) #координаты коробок с машинами

        """
        for car in car_boxes:
            x1, y1, x2, y2 = car
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 1)
        """

        car_boxes = cut_parking(car_boxes, 0)


        if (prev_cars != []):
            if (len(car_boxes) != len(prev_cars)):
                if (change_counter < 2 / spf):  #cars updates within 2 sec
                    change_counter += 1
                    car_boxes = prev_cars
                else:
                    change_counter = 0
            else:
                change_counter = 0

        if change_counter == 0:
            prev_cars = car_boxes

        spaces = find_space(car_boxes, 0)

        for space in spaces:
            x, y = space
            cv2.rectangle(frame, (x - 25, y - 35), (x + 25, y + 35), (0, 255, 0), 3)

        #если понадобится выводить на экран обработанное изображение и информацию про каждый объект в консоль, то можно вместо вызова get_car_boxes вставить этот код

        """
        for car in car_boxes:
            x1, y1, x2, y2 = car
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 3)
        """


        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        spf = time.time() - t0


    video_capture.release()
    cv2.destroyAllWindows()

process(VIDEO_SOURCE1)