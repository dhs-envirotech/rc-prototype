'''
Controls an RC Car

Original by Jacob Sommer 2020-01-20
'''
import RPi.GPIO as GPIO

import atexit

from flask import Flask, render_template, Response
from flask_socketio import SocketIO

# Define Wheel Pins
GPIO.setmode(GPIO.BCM)
BackRightPins = [6, 13]
FrontRightPins = [26, 19]
BackLeftPins = [16, 12]
FrontLeftPins = [20, 21]
# BR1 = 6
# BR2 = 13
# FR1 = 26
# FR2 = 19
# BL1 = 16
# BL2 = 12
# FL1 = 20
# FL2 = 21

class Wheel:
    def __init__(self, pins):
        GPIO.setup(pins[0], GPIO.OUT)
        GPIO.setup(pins[1], GPIO.OUT)
        self.pin1 = pins[0]
        self.pin2 = pins[1]
    
    def forward(self):
        GPIO.output(self.pin1, True)
        GPIO.output(self.pin2, False)

    def backward(self):
        GPIO.output(self.pin1, False)
        GPIO.output(self.pin2, True)

    def stop(self):
        GPIO.output(self.pin1, False)
        GPIO.output(self.pin2, False)

# Create Wheels
BackRightWheel = Wheel(BackRightPins)
FrontRightWheel = Wheel(FrontRightPins)
BackLeftWheel = Wheel(BackLeftPins)
FrontLeftWheel = Wheel(FrontLeftPins)

wheels = [BackRightWheel, FrontRightWheel, BackLeftWheel, FrontLeftWheel]

# Controller
app = Flask(__name__, static_folder="static")
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('drive')
def drive(action):
    print(action)

    if action == 'forward':
        for wheel in wheels:
            wheel.forward()
    elif action == 'backward':
        for wheel in wheels:
            wheel.backward()
    elif action == 'left':
        BackLeftWheel.backward()
        FrontLeftWheel.backward()
        BackRightWheel.forward()
        FrontRightWheel.forward()
    elif action == 'right':
        BackRightWheel.backward()
        FrontRightWheel.backward()
        BackLeftWheel.forward()
        FrontLeftWheel.forward()
    elif action == 'stop':
        for wheel in wheels:
            wheel.stop()
    else:
        return 'Invalid action', 400

# @app.route('/drive/<path:action>', methods=['POST'])
# def drive_http(action):
#     if action == 'forward':
#         for wheel in wheels:
#             wheel.forward()
#     elif action == 'backward':
#         for wheel in wheels:
#             wheel.backward()
#     elif action == 'left':
#         BackLeftWheel.backward()
#         FrontLeftWheel.backward()
#         BackRightWheel.forward()
#         FrontRightWheel.forward()
#     elif action == 'right':
#         BackRightWheel.backward()
#         FrontRightWheel.backward()
#         BackLeftWheel.forward()
#         FrontLeftWheel.forward()
#     elif action == 'stop':
#         for wheel in wheels:
#             wheel.stop()
#     else:
#         return 'Invalid action', 400
    
#     return ''

drive('stop')

# app.run(debug=True, host='0.0.0.0')
socketio.run(app, host='0.0.0.0')

@atexit.register
def cleanup():
    drive('stop')
    GPIO.cleanup()
    print('Clean exit')