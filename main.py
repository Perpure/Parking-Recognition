from imageai.Detection import ObjectDetection
import numpy as np
import cv2
import os
import time
from park_calc import find_space, cut_parking
import tensorflow as tf
from flask import Flask, render_template, Response, request, flash, redirect, url_for, send_from_directory, make_response
from werkzeug.utils import secure_filename
from markupsafe import escape
from threading import Thread

stream_url = ["https://s2.moidom-stream.ru/s/public/0000010491.m3u8"] #,"rtsp://93.190.206.140:8554/vokzal"]
video_url = "sources/parking.mp4"


frame_read_mode = [False] #, False, False]
frames = [None] #, None, None]
free_parks = [0] #, 0, 0]

UPLOAD_FOLDER = 'sources/'
ALLOWED_EXTENSIONS = {'flv', 'avi', 'mkv', 'mp4'}

app = Flask('parking-recognition', template_folder="templates")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def start():
    """Home page"""
    park_urls = [url_for('stream1')]
    space_urls = [url_for('get_spaces1')]
    return render_template("home.html", park_urls=park_urls, space_urls=space_urls)

@app.route('/stream1')
def stream1():
    """Livestream of the 1st camera"""
    return render_template("stream1.html")

@app.route('/get_spaces1')
def get_spaces1():
    response = make_response(str(free_parks[0]), 200)
    response.mimetype = "text/plain"
    return response


@app.route('/get_frame1')
def get_frame1():
    response = make_response(read_frame(0), 200)
    response.mimetype = "image/jpeg"
    return response

# @app.route('/stream2')
# def stream2():
#     """Livestream of the 2nd camera"""
#     return render_template("index2.html")


# @app.route('/stream3')
# def stream3():
#     """Livestream of the 3nd camera"""
#     return render_template("index3.html")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/upload_video", methods=["GET", "POST"])
def upload_video():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], "parking.mp4"))
            return render_template("video.html")
            #return redirect(f'http://127.0.0.1:5000/process_video/{filename}')
    return render_template("upload.html")


def get_car_boxes(frame):
    car_boxes = []
    detections = (detector.detectCustomObjectsFromImage(custom_objects=custom, input_type="array", input_image=np.array(frame), output_type="array", minimum_percentage_probability=18))[1]

    for eachObject in detections:
        car_boxes.append(eachObject["box_points"])

    return np.array(car_boxes)

def gen(id):
    """Video streaming function"""
    video = cv2.VideoCapture(stream_url[id])

    spf = 3
    video_spf = 1 / 25 #???????????? ?????? ?????????? - video_capture.get(cv2.CAP_PROP_FPS), ???? ?????? ???????????? ???????????????????? 180000
    prev_cars = []
    change_counter = 0

    success, frame = video.read()
    if success:
        get_car_boxes(frame) #???????????????????? ???????????? ????????, ?????? ????????, ?????????? ?????? ???????????? ???????????????????? ?????????????????????? ???? ?????????????????? ??????????

    global frame_read_mode
    global frames
    global free_parks
    while video.isOpened():
            success, frame = video.read()
            if not success:
                continue

            t0 = time.time()
            if spf > video_spf:
                if spf > video_spf * 2:
                    spf -= video_spf
                    continue
                t0 -= spf - video_spf
            elif video_spf > spf:
                time.sleep(video_spf - spf)

            rgb_image = frame[:, :, ::-1]

            car_boxes = get_car_boxes(rgb_image)
            car_boxes = cut_parking(car_boxes, id)

            spaces = find_space(car_boxes, id)
            
            
            if (len(prev_cars) != 0):
                if (len(spaces) != len(prev_cars)):
                    if (change_counter < 4):  #cars updates within 4 sec
                        change_counter += 1
                        spaces = prev_cars
                    else:
                        change_counter = 0
                else:
                    change_counter = 0

            if change_counter == 0:
                prev_cars = spaces

            for space in spaces:
                x, y = space
                cv2.rectangle(frame, (x - 25, y - 35), (x + 25, y + 35), (0, 255, 0), 3)

            img = cv2.imencode('.jpeg', frame)[1].tobytes()
            frames[id] = img
            free_parks[id] = len(spaces)
            frame_read_mode[id] = True
            spf = time.time() - t0

def read_frame(cam):
    while True:
        global frame_read_mode
        if (frame_read_mode[cam]) and (frames[cam] != None):
            frame_read_mode[cam] = False
            return frames[cam]

def get_frame(cam):
    while True:
        frame = read_frame(cam)
        yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/process_video')
def run_video():
    return Response(gen(), #???????? ?????? ???????????????????????????? ???????????? ?????????? ???????????????? ???? ??????????. ????????????
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed1')
def video_feed1():
    return Response(get_frame(0),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route('/video_feed2')
# def video_feed2():
#     return Response(get_frame(1),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route('/video_feed3')
# def video_feed3():
#     return Response(get_frame(2),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')


execution_path = os.getcwd()

detector = ObjectDetection()
detector.setModelTypeAsRetinaNet()
detector.setModelPath(os.path.join(execution_path , "resnet50_coco_best_v2.1.0.h5"))
detector.loadModel()

custom = detector.CustomObjects(bicycle=True, car=True, motorcycle=True, bus=True, truck=True, boat=True) #??????????????, ?????????????? ???????????? ???????????? ????????????????


if __name__ == '__main__':
    for i in range(1): #???????????????? ?? ?????????? ??????????????????
        t = Thread(target=gen, args=[i])
        t.start()
    app.run()
