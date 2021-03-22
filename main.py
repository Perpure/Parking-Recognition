import cv2
import imutils
import time
from flask import Flask, render_template, Response, request

app = Flask('parking-recognition', template_folder="templates")


@app.route('/')
def start():
    """Home page"""
    return render_template("index.html")


def gen():
    """Video streaming function"""
    cap = cv2.VideoCapture("https://s2.moidom-stream.ru/s/public/0000010491.m3u8")
    # img = cv2.imread("sources/parking-picture.jpeg")

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


@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True)
