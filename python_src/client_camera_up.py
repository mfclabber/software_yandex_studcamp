import socket
import pickle
import pathlib

import cv2
import time
import numpy as np

from start_file_for_up_cam_planing import UP_CAM

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('192.168.2.217', 10000))

start_time = time.time()


# while True:
output_func = UP_CAM("red")

data = pickle.dumps(output_func)
client_socket.sendall(len(data).to_bytes(4, byteorder='big'))
client_socket.sendall(data)

print(output_func)

client_socket.close()
cv2.destroyAllWindows()