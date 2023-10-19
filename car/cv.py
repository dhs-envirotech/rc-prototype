from ultralytics import YOLO
import cv2
import math

width = 1000
height = 500

cap = cv2.VideoCapture(0)
cap.set(3, width)  # width
cap.set(4, height)  # height

model = YOLO("yolo-Weights/yolov8n.pt")

# classNames = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
#               "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
#               "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
#               "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat",
#               "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
#               "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli",
#               "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed",
#               "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone",
#               "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",
#               "teddy bear", "hair drier", "toothbrush"
#               ]

classNames = ["person"]


# These functions should be converted to lambda functions later
def calc_box_area(x1, y1, x2, y2):
    return (x2-x1)*(y2-y1)

def within_margin(num1, num2, tolerance):
    return ((abs(num1 - num2)/num1) < tolerance)


while True:
    success, img = cap.read()
    results = model(img, stream=True)

    # coordinates
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

            confidence = math.ceil((box.conf[0]*100))/100
            cls = int(box.cls[0])

            org = [x1, y1]
            font = cv2.FONT_HERSHEY_SIMPLEX
            fontScale = 1
            color = (255, 255, 255)
            thickness = 2

            area = calc_box_area(x1, y1, x2, y2)
            area_right = 0
            if within_margin(area, biggest_box_area, 0.1):
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(img, (math.floor(width/2), y1), (x2, y2), (255, 0, 0), 2)

                area_right = calc_box_area(math.floor(width/2), y1, x2, y2)

                left_area = round(((area-area_right)/area), 2)
                right_area = round((area_right/area), 2)

                cv2.putText(img, "Left", org,
                        font, fontScale, color, thickness)
                cv2.putText(img, f"Area: {left_area}", (x1, y1 + 30),
                            font, 0.7, color, thickness)
                
                cv2.putText(img, "Right", [x2, y1],
                        font, fontScale, color, thickness)
                cv2.putText(img, f"Area: {right_area}", (x2, y1 + 30),
                            font, 0.7, color, thickness)
                
                direction = ""
                rover_command = round((left_area - right_area), 1)
                if rover_command > 0:
                    direction = "Left"
                elif rover_command < 0:
                    direction = "Right"
                else:
                    direction = "Straight"          

                cv2.putText(img, f"Rover Turn: {direction} & {abs(rover_command)}", [50, 50], font, 1, color, thickness)

                approach_direction = ""
                rounded_area = round(area, -4)
                if area < 50000:
                    approach_direction = "closer"
                elif area > 50000:
                    approach_direction = "farther"
                else:
                    approach_direction = "X"

                speed = (rounded_area-50000)/1000

                cv2.putText(img, f"Rover Approach: Move {approach_direction} @ {speed}", [50, 100], font, 1, color, thickness)
            else:
                cv2.rectangle(img, (math.floor(width/2), y1), (math.floor(width/2), y2), (255, 0, 255), 2)
                cv2.putText(img, "Person", org,
                            font, fontScale, color, thickness)
                cv2.putText(img, str(confidence), (x1, y1 + 30),
                            font, 0.7, color, thickness)
            cv2.line(img, (math.floor(width/2), 0), (math.floor(width/2), height), (255, 0, 255), 2)



    cv2.imshow('Webcam', img)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
