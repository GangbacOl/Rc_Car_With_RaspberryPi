from imutils.video import VideoStream
import RPi.GPIO as gpio
import imagezmq
import argparse
import socket
import time
import threading

def ultrasound() :
	while True:
		global distance
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

def receiveStopSign():
	while True:
		client_socket.send(str(distance).encode())
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

distance = 0
drive_flag = True

trig = 13
echo = 19
in_1_forward = 18
in_2_forward = 23

gpio.setmode(gpio.BCM)
gpio.setup(trig, gpio.OUT)
gpio.setup(echo, gpio.IN)
gpio.setup(in_1_forward, gpio.OUT)
gpio.setup(in_2_forward, gpio.OUT)

pwm_forward_1 = gpio.PWM(in_1_forward, 100)
pwm_forward_2 = gpio.PWM(in_2_forward, 100)

pwm_forward_1.start(0)
pwm_forward_2.start(0)

pwm_forward_1.ChangeDutyCycle(30)

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
t2 = threading.Thread(target=ultrasound)
t2.start()

while drive_flag:
	frame = vs.read()
	sender.send_image(rpiName, frame)
	gpio.output(in_2_forward, 0)
