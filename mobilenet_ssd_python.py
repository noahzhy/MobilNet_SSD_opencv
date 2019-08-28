#Import the neccesary libraries
import numpy as np
import argparse
import cv2
import cmath

# construct the argument parse
parser = argparse.ArgumentParser()
# parser.add_argument("--video", help="path to video file. If empty, camera's stream will be used")
parser.add_argument("--video", default=0)
parser.add_argument("--prototxt", default="MobileNetSSD_deploy.prototxt")
parser.add_argument("--weights", default="MobileNetSSD_deploy.caffemodel")
parser.add_argument("--thr", default=0.2, type=float, help="confidence")
args = parser.parse_args()

# Labels of Network.
# classNames = { 0: 'background',
#     1: 'aeroplane', 2: 'bicycle', 3: 'bird', 4: 'boat',
#     5: 'bottle', 6: 'bus', 7: 'car', 8: 'cat', 9: 'chair',
#     10: 'cow', 11: 'diningtable', 12: 'dog', 13: 'horse',
#     14: 'motorbike', 15: 'person', 16: 'pottedplant',
#     17: 'sheep', 18: 'sofa', 19: 'train', 20: 'tvmonitor' }

classNames = { 15: 'person' }

# Open video file or capture device.
if args.video:
    cap = cv2.VideoCapture(args.video)

else:
    cap = cv2.VideoCapture(1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 300)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 300)
    cap.set(cv2.CAP_PROP_FPS, 25)

# Load the Caffe model
net = cv2.dnn.readNetFromCaffe(args.prototxt, args.weights)

count = 0
a = 0
c0 = [0, 0]
c1 = [0, 0]
FLAG_FALL = False

while True:
    # Capture frame-by-frame

    ret, frame = cap.read()
    # frame_resized = frame
    frame_resized = cv2.resize(frame,(300,300)) # resize frame for prediction

    # MobileNet requires fixed dimensions for input image(s)
    # so we have to ensure that it is resized to 300x300 pixels.
    # set a scale factor to image because network the objects has differents size.
    # We perform a mean subtraction (127.5, 127.5, 127.5) to normalize the input;
    # after executing this command our "blob" now has the shape:
    # (1, 3, 300, 300)
    blob = cv2.dnn.blobFromImage(frame_resized, 0.007843, (300, 300), (127.5, 127.5, 127.5), False)
    #Set to network the input blob
    net.setInput(blob)
    #Prediction of network
    detections = net.forward()

    #Size of frame resize (300x300)
    cols = frame_resized.shape[1]
    rows = frame_resized.shape[0]

    #For get the class and location of object detected,
    # There is a fix index for class, location and confidence
    # value in @detections array .
    # for i in range(1):
    i = 0
    confidence = detections[0, 0, i, 2] # Confidence of prediction
    if confidence > args.thr: # Filter prediction
        class_id = int(detections[0, 0, i, 1]) # Class label
        if class_id in classNames:
            # Object location
            xLeftBottom = int(detections[0, 0, i, 3] * cols)
            yLeftBottom = int(detections[0, 0, i, 4] * rows)
            xRightTop   = int(detections[0, 0, i, 5] * cols)
            yRightTop   = int(detections[0, 0, i, 6] * rows)
            # Factor for scale to original size of frame
            heightFactor = frame.shape[0]/300.0
            widthFactor = frame.shape[1]/300.0
            # Scale object detection to frame
            xLeftBottom = int(widthFactor * xLeftBottom)
            yLeftBottom = int(heightFactor * yLeftBottom)
            xRightTop   = int(widthFactor * xRightTop)
            yRightTop   = int(heightFactor * yRightTop)
            # Draw label and confidence of prediction in frame resized
            label = classNames[class_id] + ": " + str(confidence)
            labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 1, 1)
            yLeftBottom = max(yLeftBottom, labelSize[1])
            h = yRightTop - yLeftBottom
            w = xRightTop - xLeftBottom



            # count += 1
            # if (count % 4 == 0):
            #     count = 0
            #     c0 = [float(w/2), float(h/2)]
            #     # print((c0,c1))
            #     a = abs((c0[1]-c1[1])**2)**0.5
            #     print(a)
            #
            # c1 = [float(w/2), float(h/2)]
            #
            # print(FLAG_FALL)
#
            if float(w/h) >= 1.1:
            # if (a > 15) or FLAG_FALL:
                # FLAG_FALL = True
                cv2.rectangle(frame, (xLeftBottom, yLeftBottom), (xRightTop, yRightTop), (0, 0, 255), 5)
                cv2.putText(frame, "Fall", (xLeftBottom+10, yLeftBottom+30),cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255),3)
            else:
                cv2.rectangle(frame, (xLeftBottom, yLeftBottom), (xRightTop, yRightTop), (0, 255, 0), 5)
                cv2.putText(frame, label, (xLeftBottom+10, yLeftBottom+30),cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0),3)
            #
            # if (5 < a) and FLAG_FALL:
            #     FLAG_FALL = False
            # print(label) #print class and confidence

    cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("frame", 640, 480);
    cv2.imshow("frame", frame)
    if cv2.waitKey(1) >= 0:  # Break with ESC
        break
