from imageai.Detection import ObjectDetection
import numpy as np
import cv2
import os

execution_path = os.getcwd()

def get_car_boxes(frame):
    car_boxes = []
    detections = (detector.detectCustomObjectsFromImage(custom_objects=custom, input_type="array", input_image=np.array(frame), output_type="array", minimum_percentage_probability=25))[1]

    for eachObject in detections:
        car_boxes.append(eachObject["box_points"])

    return np.array(car_boxes)

VIDEO_SOURCE = "test_images/parking1.mp4"

detector = ObjectDetection()
detector.setModelTypeAsRetinaNet()
detector.setModelPath( os.path.join(execution_path , "resnet50_coco_best_v2.1.0.h5"))
detector.loadModel()

custom = detector.CustomObjects(bicycle=True, car=True, motorcycle=True, bus=True, truck=True, boat=True, bear=True) #объекты, которые должна искать нейронка

video_capture = cv2.VideoCapture(VIDEO_SOURCE)

while video_capture.isOpened():
    success, frame = video_capture.read()
    if not success:
        break

    rgb_image = frame[:, :, ::-1]

    car_boxes = get_car_boxes(rgb_image) #координаты коробок с машинами 

    '''
    #если понадобится выводить на экран обработанное изображение и информацию про каждый объект в консоль, то можно вместо вызова get_car_boxes вставить этот код
    
    detections = detector.detectCustomObjectsFromImage(custom_objects=custom, input_type="array", input_image=np.array(rgb_image), output_type="array", minimum_percentage_probability=25)
    cv2.imshow('Video', detections[0]) #перепутаны синий и красный каналы

    for eachObject in detections[1]:
        print(eachObject["name"] , " : " , eachObject["percentage_probability"], " : ", eachObject["box_points"])

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    '''

video_capture.release()
cv2.destroyAllWindows()