'''
Program for controlling an RC Car through POST requests
Created by Jacob Sommer 2020-01-20
'''
import math
from time import sleep
import atexit
import RPi.GPIO as GPIO
from flask import Flask, request, render_template, Response
# from flask_assets import Bundle, Environment
import camera

video_camera = camera.Camera() # creates a camera object

# define the ports
# based on the number coming after GPIO (BCM numbering mode) ex: IN1 is connected to port 11/GPIO17 which is 17
BR1 = 6
BR2 = 13
FR1 = 26
FR2 = 19
BL1 = 16
BL2 = 12
FL1 = 20
FL2 = 21

# constants for maximum motor speed (up to 100)
DRIVE_SPEED = 100
TURN_SPEED = 100

# set up GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(FL1, GPIO.OUT)
GPIO.setup(FL2, GPIO.OUT)
GPIO.setup(BR1, GPIO.OUT)
GPIO.setup(BR2, GPIO.OUT)
GPIO.setup(FR1, GPIO.OUT)
GPIO.setup(FR2, GPIO.OUT)
GPIO.setup(BL1, GPIO.OUT)
GPIO.setup(BL2, GPIO.OUT)

def stop(): 
    GPIO.output(BR1, False)
    GPIO.output(BR2, False)
    GPIO.output(FR1, False)
    GPIO.output(FR2, False)
    GPIO.output(BL1, False)
    GPIO.output(BL2, False)
    GPIO.output(FL1, False)
    GPIO.output(FL2, False)

stop() # make sure car is initially stopped
# drive_pwm = GPIO.PWM(PWM1, 100)
# turn_pwm = GPIO.PWM(PWM2, 100)
# drive_pwm.start(DRIVE_SPEED)
# turn_pwm.start(TURN_SPEED)

def forward(pin1, pin2):
    GPIO.output(pin1, True)
    GPIO.output(pin2, False)

def backward(pin1, pin2):
    GPIO.output(pin1, False)
    GPIO.output(pin2, True)

def drive(x, y):
    '''
    Drive at the specified speed in the specified direction
    x - float between -1 and 1, raw input value, forward/backward movement
    y - float between -1 and 1, raw input value, left/right movement
    '''
    if y > 0: # right
        forward(FL1, FL2)
        forward(BL1, BL2)
        backward(FR1, FR2)
        backward(BR1, BR2)
        # turn_pwm.ChangeDutyCycle(int(TURN_SPEED * value))
    elif y < 0: # left
        backward(FL1, FL2)
        backward(BL1, BL2)
        forward(FR1, FR2)
        forward(BR1, BR2)
        # turn_pwm.ChangeDutyCycle(int(TURN_SPEED * -value))
    elif x > 0: # forward
        forward(FL1, FL2)
        forward(BL1, BL2)
        forward(FR1, FR2)
        forward(BR1, BR2)
        # drive_pwm.ChangeDutyCycle(int(DRIVE_SPEED * value))
    elif x < 0: # backward
        backward(FL1, FL2)
        backward(BL1, BL2)
        backward(FR1, FR2)
        backward(BR1, BR2)
        # drive_pwm.ChangeDutyCycle(int(DRIVE_SPEED * -value))
    else:
        stop()

app = Flask(__name__) # create Flask app object

@app.route('/drive', methods=['POST'])
def route_drive():
    '''
    Listen for POST requests to /drive and process them
    '''
    drive(float(request.form['x']), float(request.form['y']))
    return 'Drive'

@app.route('/')
def index():
    return render_template('index.html')

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(video_camera),
                  mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__': # if this file is launched directly
    camera.init_camera()
    app.run(host='0.0.0.0', port=5000, threaded=True) # run Flask app, threaded allows multiple requests to be handled at once

@atexit.register
def cleanup():
    '''
    Cleans up GPIO pins when app is closed
    '''
    GPIO.cleanup()
