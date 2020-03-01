from imutils import build_montages
from datetime import datetime
import numpy as np
import imagezmq
import argparse
import imutils
import cv2

def getOutputsNames(net):
    layersNames = net.getLayerNames()
    return [layersNames[i[0] - 1] for i in net.getUnconnectedOutLayers()]

def postprocess(frame, outs):
    frameHeight = frame.shape[0]
    frameWidth = frame.shape[1]

    classIds = []
    confidences = []
    boxes = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            classId = np.argmax(scores)
            if classes[classId] != 'stop sign':
                continue
            confidence = scores[classId]
            if confidence > confThreshold:
                center_x = int(detection[0] * frameWidth)
                center_y = int(detection[1] * frameHeight)
                width = int(detection[2] * frameWidth)
                height = int(detection[3] * frameHeight)
                left = int(center_x - width / 2)
                top = int(center_y - height / 2)
                classIds.append(classId)
                confidences.append(float(confidence))
                boxes.append([left, top, width, height])
    indices = cv2.dnn.NMSBoxes(boxes, confidences, confThreshold, nmsThreshold)
    for i in indices:
        i = i[0]
        box = boxes[i]
        left = box[0]
        top = box[1]
        width = box[2]
        height = box[3]
        drawPred(classIds[i], confidences[i], left, top, left + width, top + height)

def drawPred(classId, conf, left, top, right, bottom):
    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255))
    
    label = '%.2f' % conf
    label = '%s:%s' % (classes[classId], label)
    
    labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
    top = max(top, labelSize[1])
    cv2.putText(frame, label, (left, top), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))

# construct the argument parser and parse the arguments
imageHub = imagezmq.ImageHub()

confThreshold = 0.5
nmsThreshold = 0.4

modelCfg = '/Users/gangbacol/Desktop/Development/socket_RaspberryPi_Mac/model&weight/yolov3.cfg'
modelWeight = '/Users/gangbacol/Desktop/Development/socket_RaspberryPi_Mac/model&weight/yolov3.weights'
classesFile = '/Users/gangbacol/Desktop/Development/socket_RaspberryPi_Mac/model&weight/coco.names'

with open(classesFile, 'rt') as f:
    classes = f.read().rstrip('\n').split('\n')

# 사용할 모델 불러오기
print("[INFO] loading model...")
net = cv2.dnn.readNetFromDarknet(modelCfg, modelWeight)

while True:
    (rpiName, frame) = imageHub.recv_image()
    imageHub.send_reply(b'OK')
    print("[INFO] Predicting will start...")
    
    frame = imutils.resize(frame, width=400)
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (320, 320)), 1/255, (320, 320), [0,0,0], 1, crop=False)

    net.setInput(blob)
    outs = net.forward(getOutputsNames(net))
    outs = np.array(outs)

    print(outs.shape)
    postprocess(frame, outs)

    t, _ = net.getPerfProfile()
    label = 'Inference time: %.2f ms' % (t * 1000.0 / cv2.getTickFrequency())
    cv2.putText(frame, label, (0, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))
    cv2.imshow('frame of realtime video', frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

cv2.destroyAllWindows()
