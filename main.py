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


def gen(url):
    """Video streaming function"""
    cap = cv2.VideoCapture(url)

    while cap.isOpened():
        ret, img = cap.read()
        if ret:
            img = cv2.resize(img, (0, 0), fx=1.0, fy=1.0)
            frame = cv2.imencode('.jpeg', img)[1].tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.01)
        else:
            break


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
