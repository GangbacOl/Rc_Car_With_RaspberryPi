from imutils.video import VideoStream
import RPi.GPIO as gpio
import imagezmq
import argparse
import socket
import time
import threading

def receiveStopSign():
	while True:
		sign = client_socket.recv(1024)
		if sign:
			global drive_flag
			print('stop')
			pwm_forward_1.ChangeDutyCycle(0)
			pwm_forward_2.ChangeDutyCycle(0)
			gpio.output(in_1_forward, 1)
			gpio.output(in_2_forward, 1) 
			drive_flag = False
			break

drive_flag = True

in_1_forward = 18
in_2_forward = 23

gpio.setmode(gpio.BCM)
gpio.setup(in_1_forward, gpio.OUT)
gpio.setup(in_2_forward, gpio.OUT)

pwm_forward_1 = gpio.PWM(in_1_forward, 100)
pwm_forward_2 = gpio.PWM(in_2_forward, 100)

pwm_forward_1.start(0)
pwm_forward_2.start(0)

pwm_forward_1.ChangeDutyCycle(20)

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

t1 = threading.Thread(target=receiveStopSign)
t1.start()

while drive_flag:
	frame = vs.read()
	sender.send_image(rpiName, frame)
	gpio.output(in_2_forward, 0)

