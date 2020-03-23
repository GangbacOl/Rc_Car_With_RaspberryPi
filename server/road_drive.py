from imutils import build_montages
from datetime import datetime
import numpy as np
import imagezmq
import argparse
import imutils
import cv2
import time
import socket

def color_filtering(ROI):
    hsv = cv2.cvtColor(ROI, cv2.COLOR_BGR2HSV)

    lower_red = np.array([170, 100, 0])
    upper_red = np.array([180, 255, 255])
    #h, s, v = cv2.split(hsv)
    mask_red = cv2.inRange(hsv, lower_red, upper_red) 
    cv2.imshow('mask_red', mask_red)
    return mask_red

def set_ROI(img):
    cuttingImg = img[96:][0:]
    return cuttingImg

def dir_discriminator(img):
    try:
        filteredImg = color_filtering(set_ROI(img))
        lines = cv2.HoughLinesP(filteredImg, 0.8, np.pi / 180, 90, minLineLength = 10, maxLineGap = 100)
        slope_degree = (np.arctan2(lines[:, 0, 1] - lines[:, 0, 3], lines[:, 0, 0] - lines[:, 0, 2]) * 180) / np.pi

        avg_angle = np.average(np.array(slope_degree))

        if avg_angle > -160.2 and avg_angle < -100.0:
            print('left')
            print('angle: '+str(avg_angle))
            return -1, avg_angle
        elif avg_angle > 100.4 and avg_angle < 170.1:
            print('right')
            print('angle: '+str(avg_angle))
            return 1, avg_angle

    except TypeError:
            return

imageHub = imagezmq.ImageHub()

while True:
    rpiName, frame = imageHub.recv_image()
    imageHub.send_reply(b'OK')
    cv2.imshow('test', frame)
    print(dir_discriminator(frame))
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
cv2.destroyAllWindows()
