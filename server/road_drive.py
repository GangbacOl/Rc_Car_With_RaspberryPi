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

    lower_blue = np.array([255, 0, 0])
    upper_blue = np.array([127, 127, 255])

    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
    
    return mask_blue

def set_ROI(img):
    cuttingImg = img[250:][0:]
    return cuttingImg

def dir_discriminator(img):
    try:
        filteredImg = color_filtering(set_ROI(img))
        lines = cv2.HoughLinesP(filteredImg, 0.8, np.pi / 180, 90, minLineLength = 10, maxLineGap = 100)
        slope_degree = (np.arctan2(lines[:, 0, 1] - lines[:, 0, 3], lines[:, 0, 0] - lines[:, 0, 2]) * 180) / np.pi

        avg_angle = np.average(np.array(slope_degree))
        print(avg_angle)

        if avg_angle > -160.2 and avg_angle < -100.0:
            return -1
        elif avg_angle > 100.4 and av < 170.1:
            return 1

    except TypeError:
            return

imageHub = imagezmq.ImageHub()

while True:
    rpiName, frame = imageHub.recv_image()
    imageHub.send_reply(b'OK')
    print(dir_discriminator(frame))
    time.sleep(0.2)
