from imutils.video import VideoStream
import imagezmq
import socket
import argparse
import time
import cv2
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("-s", "--server-ip", required=True,
		help="ip address of the server to which the client will connect")
args = vars(ap.parse_args())

sender = imagezmq.ImageSender(connect_to="tcp://{}:5555".format(args["server_ip"]))

rpiName = socket.gethostname()
vs = VideoStream(usePiCamera=True).start()
print("start..!")

count = 0
while True:
	frame = vs.read()
	sender.send_image(rpiName, frame)
vs.close()

