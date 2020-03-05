import imagezmq
import cv2
import imutils
import socket
from time import sleep

save_path = '/Users/gangbacol/Desktop/Development/socket_RaspberryPi_Mac/training_dataset'

imageHub = imagezmq.ImageHub()

count = 0
print("start")
while True:
    print("count: "+str(count+1))
    (rpiName, frame) = imageHub.recv_image()
    imageHub.send_reply(b'ok')
    frame = imutils.resize(frame, width=500)

    if count < 10 : cv2.imwrite(save_path+'/frame_000'+str(count+1)+'.jpg', frame)
    elif count < 100 : cv2.imwrite(save_path+'/frame_00'+str(count+1)+'.jpg', frame)
    elif count < 1000 : cv2.imwrite(save_path+'/frame_0'+str(count+1)+'.jpg', frame)
    else : cv2.imwrite(save_path+'/frame_'+str(count+1)+'.jpg', frame)
    
    count += 1
    sleep(0.05)
