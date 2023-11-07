from ultralytics import YOLO
import cv2
import RPi.GPIO as GPIO
import math
from termcolor import colored

# GPIO pin definitions
MOTOR_PINS = {
    "BR1": 6,
    "BR2": 13,
    "FR1": 26,
    "FR2": 19,
    "BL1": 16,
    "BL2": 12,
    "FL1": 20,
    "FL2": 21
}

# Motor speed constants
DRIVE_SPEED = 100
TURN_SPEED = 100

# Set up GPIO
GPIO.setmode(GPIO.BCM)
for pin in MOTOR_PINS.values():
    GPIO.setup(pin, GPIO.OUT)

# Car functions
def stop():
    for pin in MOTOR_PINS.values():
        GPIO.output(pin, False)

def forward(pin1, pin2):
    GPIO.output(pin1, True)
    GPIO.output(pin2, False)

def backward(pin1, pin2):
    GPIO.output(pin1, False)
    GPIO.output(pin2, True)

def drive(x, y):
    if y > 0:  # Turn right
        forward(MOTOR_PINS["FL1"], MOTOR_PINS["FL2"])
        forward(MOTOR_PINS["BL1"], MOTOR_PINS["BL2"])
        backward(MOTOR_PINS["FR1"], MOTOR_PINS["FR2"])
        backward(MOTOR_PINS["BR1"], MOTOR_PINS["BR2"])
        command = "Turn Right"
    elif y < 0:  # Turn left
        backward(MOTOR_PINS["FL1"], MOTOR_PINS["FL2"])
        backward(MOTOR_PINS["BL1"], MOTOR_PINS["BL2"])
        forward(MOTOR_PINS["FR1"], MOTOR_PINS["FR2"])
        forward(MOTOR_PINS["BR1"], MOTOR_PINS["BR2"])
        command = "Turn Left"
    elif x > 0:  # Move forward
        forward(MOTOR_PINS["FL1"], MOTOR_PINS["FL2"])
        forward(MOTOR_PINS["BL1"], MOTOR_PINS["BL2"])
        forward(MOTOR_PINS["FR1"], MOTOR_PINS["FR2"])
        forward(MOTOR_PINS["BR1"], MOTOR_PINS["BR2"])
        command = "Move Forward"
    elif x < 0:  # Move backward
        backward(MOTOR_PINS["FL1"], MOTOR_PINS["FL2"])
        backward(MOTOR_PINS["BL1"], MOTOR_PINS["BL2"])
        backward(MOTOR_PINS["FR1"], MOTOR_PINS["FR2"])
        backward(MOTOR_PINS["BR1"], MOTOR_PINS["BR2"])
        command = "Move Backward"
    else:
        stop()
        command = "Stop"
    
    print(colored(command, 'green'))

# Set camera parameters
width = 1000
height = 500

PERSON_SIZE_MIN = 100000

cap = cv2.VideoCapture(0)
cap.set(3, width)  # Set width
cap.set(4, height)  # Set height

model = YOLO("yolo-Weights/yolov8n.pt")

classNames = ["person"]

def calc_box_area(x1, y1, x2, y2):
    return (x2 - x1) * (y2 - y1)

def within_margin(num1, num2, tolerance):
    return ((abs(num1 - num2) / num1) < tolerance)

# Suppress OpenCV print messages
block_print()

while True:
    success, img = cap.read()
    results = model(img, stream=True)

    biggest_box = None
    biggest_box_area = 0

    for r in results:
        boxes = r.boxes

        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            area = calc_box_area(x1, y1, x2, y2)
            if area > biggest_box_area:
                biggest_box_area = area
                biggest_box = box

        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            area = calc_box_area(x1, y1, x2, y2)
            area_right = 0

            if within_margin(area, biggest_box_area, 0.1):
                area_right = calc_box_area(math.floor(width / 2), y1, x2, y2)
                left_area = round(((area - area_right) / area), 2)
                right_area = round((area_right / area), 2)
                rover_command = round((left_area - right_area), 1)
                normalized_turn = math.copysign(1, rover_command) * (0 if abs(rover_command) < 0.4 else TURN_SPEED)
                rounded_area = round(area, -4)
                speed = round(((area - PERSON_SIZE_MIN) / 10000), 0)
                normalized_speed = math.copysign(1, speed) * 0 if abs(speed) < 20 else DRIVE_SPEED
            else:
                normalized_turn = 0
                normalized_speed = 0
    
    drive(normalized_turn, normalized_speed)
