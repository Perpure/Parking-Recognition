from imageai.Detection import ObjectDetection
import numpy as np
import cv2
<<<<<<< HEAD
import mrcnn.config
import mrcnn.utils
from mrcnn.model import MaskRCNN
from pathlib import Path
from park_calc import cut_parking, PARKS_POLYGONS

class MaskRCNNConfig(mrcnn.config.Config):
    NAME = "coco_pretrained_model_config"
    IMAGES_PER_GPU = 1
    GPU_COUNT = 1
    NUM_CLASSES = 1 + 80
    DETECTION_MIN_CONFIDENCE = 0.25

def get_car_boxes(boxes, class_ids):
=======
import os
import time

execution_path = os.getcwd()

def get_car_boxes(frame):
>>>>>>> car-recognition
    car_boxes = []
    detections = (detector.detectCustomObjectsFromImage(custom_objects=custom, input_type="array", input_image=np.array(frame), output_type="array", minimum_percentage_probability=20))[1]

    for eachObject in detections:
        car_boxes.append(eachObject["box_points"])

    return np.array(car_boxes)


<<<<<<< HEAD
ROOT_DIR = Path(".")
MODEL_DIR = ROOT_DIR / "logs"
COCO_MODEL_PATH = ROOT_DIR / "mask_rcnn_coco.h5"

if not COCO_MODEL_PATH.exists():
    mrcnn.utils.download_trained_weights(COCO_MODEL_PATH)

IMAGE_DIR = ROOT_DIR / "images"
VIDEO_SOURCE = "test_images/parking3.flv"
=======
VIDEO_SOURCE = "test_images/parking1.mp4"
>>>>>>> car-recognition

detector = ObjectDetection()
detector.setModelTypeAsRetinaNet()
detector.setModelPath( os.path.join(execution_path , "resnet50_coco_best_v2.1.0.h5"))
detector.loadModel()

custom = detector.CustomObjects(bicycle=True, car=True, motorcycle=True, bus=True, truck=True, boat=True, bear=True) #объекты, которые должна искать нейронка

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

<<<<<<< HEAD
    r = results[0]

    if parked_car_boxes is None:
        parked_car_boxes = get_car_boxes(r['rois'], r['class_ids'])
    else:
        car_boxes = get_car_boxes(r['rois'], r['class_ids'])
        parked_cars = cut_parking(car_boxes, PARKS_POLYGONS[0])
        overlaps = mrcnn.utils.compute_overlaps(parked_car_boxes, car_boxes)
        for parking_area, overlap_areas in zip(parked_car_boxes, overlaps):
            max_IoU_overlap = np.max(overlap_areas)

            y1, x1, y2, x2 = parking_area

=======
    rgb_image = frame[:, :, ::-1]

    car_boxes = get_car_boxes(rgb_image) #координаты коробок с машинами 
>>>>>>> car-recognition

    '''
    #если понадобится выводить на экран обработанное изображение и информацию про каждый объект в консоль, то можно вместо вызова get_car_boxes вставить этот код
    
    detections = detector.detectCustomObjectsFromImage(custom_objects=custom, input_type="array", input_image=np.array(rgb_image), output_type="array", minimum_percentage_probability=20)
    cv2.imshow('Video', detections[0]) #перепутаны синий и красный каналы

<<<<<<< HEAD
        for car in parked_cars:
            y1, x1, y2, x2 = parking_area
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 3)
        cv2.imshow('Video', frame)
=======
    for eachObject in detections[1]:
        print(eachObject["name"] , " : " , eachObject["percentage_probability"], " : ", eachObject["box_points"])
>>>>>>> car-recognition

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    '''
    spf = time.time() - t0
    

video_capture.release()
cv2.destroyAllWindows()
