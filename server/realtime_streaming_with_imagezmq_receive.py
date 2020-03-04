from imutils import build_montages
from datetime import datetime
import numpy as np
import imagezmq
import argparse
import imutils
import cv2
import time
import socket
import threading

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
            if classes[classId] != 'stop sign' and classes[classId] != 'car':
                continue
            print(str(classes[classId])+' detect!')
            confidence = scores[classId]
            if confidence > confThreshold:
                box = detection[0:4] * np.array([frameWidth, frameHeight, frameWidth, frameHeight])
                (center_x, center_y, width, height) = box.astype("int")
                x = int(center_x - width / 2)
                y = int(center_y - height / 2)
                classIds.append(classId)
                confidences.append(float(confidence))
                boxes.append([x, y, int(width), int(height)])
    indices = cv2.dnn.NMSBoxes(boxes, confidences, confThreshold, nmsThreshold)
    for i in indices:
        i = i[0]
        box = boxes[i]
        (x, y) = (box[0], box[1])
        (width, height) = (box[2], box[3])
        drawPred(classIds[i], confidences[i], x, y, x + width, y + height)

def drawPred(classId, conf, left, top, right, bottom):
    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
    
    label = '%.2f' % conf
    label = '%s:%s' % (classes[classId], label)
    
    labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
    top = max(top, labelSize[1])
    cv2.putText(frame, label, (left, top), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))

def receiveDistance():
    while True:
        global distance
        distance = client_socket.recv(1024)

# construct the argument parser and parse the arguments
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('192.168.219.110', 9999))
server_socket.listen()
client_socket, addr = server_socket.accept()
print('Connected by', addr)

distance = 0

imageHub = imagezmq.ImageHub()

confThreshold = 0.5
nmsThreshold = 0.4

modelCfg = '/Users/gangbacol/Desktop/Development/socket_RaspberryPi_Mac/server/model&weight/yolov3-tiny.cfg'
modelWeight = '/Users/gangbacol/Desktop/Development/socket_RaspberryPi_Mac/server/model&weight/yolov3-tiny.weights'
classesFile = '/Users/gangbacol/Desktop/Development/socket_RaspberryPi_Mac/server/model&weight/coco.names'

with open(classesFile, 'rt') as f:
    classes = f.read().rstrip('\n').split('\n')

# 사용할 모델 불러오기
print("[INFO] loading model...")
net = cv2.dnn.readNetFromDarknet(modelCfg, modelWeight)

t = threading.Thread(target=receiveDistance)
t.start()
while True:
    (rpiName, frame) = imageHub.recv_image()
    imageHub.send_reply(b'OK')
    print("[INFO] Predicting will start...")
    
    frame = imutils.resize(frame, width=800)
    (h, w) = frame.shape[:2]
    
    cv2.imshow('input frame(GrayScale)', cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))

    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (320, 320)), 1/255.0, (320, 320), [0,0,0], 1, crop=False)
    
    net.setInput(blob)
    outs = net.forward(getOutputsNames(net))
    outs = np.array(outs)

    postprocess(frame, outs)
    
    t, _ = net.getPerfProfile()
    label = 'Inference time: %.2f ms' % (t * 1000.0 / cv2.getTickFrequency())
    cv2.putText(frame, label, (0, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))
    cv2.putText(frame, str(distance)+'cm', (15, (h-30)), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
    cv2.imshow('frame of realtime video', frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
cv2.destroyAllWindows()
