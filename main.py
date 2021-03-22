import cv2
import time
from flask import Flask, render_template, Response

app = Flask('parking-recognition', template_folder="templates")
stream_url1 = "https://s2.moidom-stream.ru/s/public/0000010493.m3u8"  # парковка у жд вокзала
stream_url2 = "https://s2.moidom-stream.ru/s/public/0000010491.m3u8"  # парковка на просп. Ленина


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


@app.route('/uploading')
def uploading_and_processing():
    """Uploading page"""
    # url = get_video() - imported function to upload video to sources/ and get it's url
    # return render_template(url)
    return '...'


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
