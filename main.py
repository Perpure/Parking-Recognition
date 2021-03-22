import cv2
import time
import os
from flask import Flask, render_template, Response, request, flash, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from markupsafe import escape

stream_url1 = "https://s2.moidom-stream.ru/s/public/0000010493.m3u8"  # парковка у жд вокзала
stream_url2 = "https://s2.moidom-stream.ru/s/public/0000010491.m3u8"  # парковка на просп. Ленина

UPLOAD_FOLDER = 'sources/'
ALLOWED_EXTENSIONS = {'flv', 'avi', 'mkv', 'mp4'}

app = Flask('parking-recognition', template_folder="templates")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def start():
    """Home page"""
    return render_template("home.html")


@app.route('/stream1')
def main_page():
    """Livestream of the 1st camera"""
    return render_template("index.html")


@app.route('/stream2')
def main_page2():
    """Livestream of the 2nd camera"""
    return render_template("index2.html")


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
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(f'http://127.0.0.1:5000/process_video/{filename}')
    return render_template("upload.html")


def get_car_boxes(frame):
    car_boxes = []
    detections = (detector.detectCustomObjectsFromImage(custom_objects=custom, input_type="array", input_image=np.array(frame), output_type="array", minimum_percentage_probability=18))[1]

    for eachObject in detections:
        car_boxes.append(eachObject["box_points"])

    return np.array(car_boxes)


def gen(VIDEO_SOURCE):
    """Video streaming function"""

    video_capture = cv2.VideoCapture(VIDEO_SOURCE)

    spf = 0
    video_spf = 1 / 25 #узнать фпс видео - video_capture.get(cv2.CAP_PROP_FPS), но для потока возвращает 180000
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

        car_boxes = get_car_boxes(rgb_image)
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

        img = cv2.imencode('.jpeg', frame)[1].tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + img + b'\r\n')

        spf = time.time() - t0


@app.route('/process_video/<filename>')
def run_video(filename):
    return Response(gen(f'sources/{escape(filename)}'),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_feed')
def video_feed():
    return Response(gen(stream_url1),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_feed2')
def video_feed2():
    return Response(gen(stream_url2),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True)
