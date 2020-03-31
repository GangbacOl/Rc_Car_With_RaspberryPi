import socket
import time
from imutils.video import VideoStream
import imagezmq
import threading
import RPi.GPIO as gpio

def LRController():
	while True:
		sign = int(client_socket.recv(1024))
		if sign == 1:
			print('right!')
			gpio.output(in_1_handle, 1)
			gpio.output(in_2_handle, 0)
		else:
			print('left!')
			gpio.output(in_1_handle, 0)
			gpio.output(in_2_handle, 1)

in_1_handle = 16
in_2_handle = 12
in_3_forward = 18
in_4_forward = 23

gpio.setmode(gpio.BCM)
gpio.setup(in_1_handle, gpio.OUT)
gpio.setup(in_2_handle, gpio.OUT)
gpio.setup(in_3_forward, gpio.OUT)
gpio.setup(in_4_forward, gpio.OUT)

pwm_forward_1 = gpio.PWM(in_3_forward, 100)
pwm_forward_2 = gpio.PWM(in_4_forward, 100)

pwm_forward_1.start(0)
pwm_forward_2.start(0)

pwm_forward_1.ChangeDutyCycle(50)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('192.168.219.110', 9999))

sender = imagezmq.ImageSender(connect_to='tcp://192.168.219.110:5555')

rpi_name = socket.gethostname()
picam = VideoStream(usePiCamera=True).start()
time.sleep(2.0)

t1 = threading.Thread(target=LRController)
t1.start()

while True:
	image = picam.read()
	sender.send_image(rpi_name, image)
	gpio.output(in_4_forward, 0)
