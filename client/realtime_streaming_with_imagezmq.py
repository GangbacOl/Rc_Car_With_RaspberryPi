from imutils.video import VideoStream
import RPi.GPIO as gpio
import imagezmq
import argparse
import socket
import time
import threading

def ultrasound() :
	while True:
		gpio.output(trig, False)
		time.sleep(0.5)
		gpio.output(trig, True)
		time.sleep(0.00001)
		gpio.output(trig, False)
		while gpio.input(echo) == 0:
			pulse_start = time.time()
		while gpio.input(echo) == 1:
			pulse_end = time.time()
		pulse_duration = pulse_end - pulse_start
		distance = pulse_duration * 17000
		distance = round(distance, 2)	
		client_socket.send(str(distance).encode())

gpio.setmode(gpio.BCM)
trig = 13
echo = 19

gpio.setup(trig, gpio.OUT)
gpio.setup(echo, gpio.IN)

ap = argparse.ArgumentParser()
ap.add_argument("-s", "--server-ip", required=True,
		help="ip address of the server to which the client will connect")
args = vars(ap.parse_args())

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((args["server_ip"], 9999))

sender = imagezmq.ImageSender(connect_to="tcp://{}:5555".format(args["server_ip"]))

rpiName = socket.gethostname()
vs = VideoStream(usePiCamera=True).start()

time.sleep(2.0)
t = threading.Thread(target=ultrasound)
t.start()

while True:
	frame = vs.read()
	sender.send_image(rpiName, frame)
vs.close()
