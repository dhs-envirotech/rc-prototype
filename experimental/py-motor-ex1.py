#IN1 on, IN2 off → clockwise
#IN1 off, IN2 off → counterclockwise
#turns all motors clockwise
import RPi.GPIO as GPIO
import time

IN1 = 6

IN2 = 13

IN3 = 19

IN4 = 2619

def init():

    GPIO.setmode(GPIO.BCM)

    GPIO.setup(IN1, GPIO.OUT)

    GPIO.setup(IN2, GPIO.OUT) 

    GPIO.setup(IN3, GPIO.OUT) 

    GPIO.setup(IN4, GPIO.OUT) 

def moveFirst(t):

    init()

    GPIO.output(IN1, True)

    GPIO.output(IN2, False)

    time.sleep(t)

    GPIO.cleanup()

def moveSecond(t):

    init()

    GPIO.output(IN1, True)

    GPIO.output(IN2, False)

    time.sleep(t)

    GPIO.cleanup()

def moveThird(t):

    init()

    GPIO.output(IN3, True)

    GPIO.output(IN4, False)

    time.sleep(t)

    GPIO.cleanup()

def moveFourth(t):

    init()

    GPIO.output(IN3, True)

    GPIO.output(IN4, False)

    time.sleep(t)

    GPIO.cleanup()

print “motors turning”

moveFirst(10)

moveSecond(10)

moveThird(10)

moveFourth(10)
