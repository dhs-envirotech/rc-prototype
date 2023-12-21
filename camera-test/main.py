import threading
from typing import Any
import cv2
from flask import Flask, render_template, Response
import time

app = Flask(__name__)


class Camera():
    camera = None

    def make_stream(self):
        if self.camera is None:
            self.camera = cv2.VideoCapture(0)

        while True:
            success, frame = self.camera.read()
            if not success:
                break

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    def close(self):
        self.camera.release()

camera = Camera()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(camera.make_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    threading.Thread(target=video_feed).start()
    app.run(debug=True, host='0.0.0.0')
