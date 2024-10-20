import socket
import cv2
import numpy as np


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('172.20.10.5', 10000))  # IP-адрес Raspberry Pi и порт 10000
server_socket.listen(1)

print("Ожидание подключения клиента...")
client_socket, addr = server_socket.accept()
print(f"Подключен к {addr}")

def align_histogram(frame): 
    frame_rgb = cv2.split(frame) 
    mean1 = np.mean(frame_rgb) 
    desired_mean = 60 
    alpha = mean1 / desired_mean 
    Inew_RGB = [] 
    for layer in frame_rgb: 
        Imin = layer.min() 
        Imax = layer.max() 
        Inew = ((layer - Imin) / (Imax - Imin)) ** alpha 
        Inew_RGB.append(Inew) 
    Inew = cv2.merge(Inew_RGB) 
    Inew_1 = (255*Inew).clip(0, 255).astype(np.uint8) 
    return Inew_1


cap = cv2.VideoCapture(0)

from ctrl_servo import CTRL_Servo
control_s = CTRL_Servo()
control_s.standart_pose()


def reduce_saturation(image, reduction_factor=0.5):

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hsv[:, :, 1] = hsv[:, :, 1] * reduction_factor

    desaturated_image = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    return desaturated_image

def reduce_brightness(image, reduction_factor=0.5):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hsv[:, :, 2] = np.clip(hsv[:, :, 2] * reduction_factor, 0, 255)
    
    darkened_image = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    return darkened_image


def find_red_cube(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_red1 = np.array([0, 70, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 70, 50])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)

    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) > 0:
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        return (x, y, w, h)
    else:
        return None
    

def find_bright_green_object(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_bright_green = np.array([35, 100, 100])
    upper_bright_green = np.array([150, 255, 255])

    mask = cv2.inRange(hsv, lower_bright_green, upper_bright_green)

    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) > 0:
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        return (x, y, w, h)
    else:
        return None
    
def find_blue_object(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_blue = np.array([100, 150, 0])
    upper_blue = np.array([140, 255, 255])

    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) > 0:
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        return (x, y, w, h)
    else:
        return None

def find_gray_box(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_gray = np.array([0, 0, 50])
    upper_gray = np.array([180, 50, 200])

    mask = cv2.inRange(hsv, lower_gray, upper_gray)

    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) > 0:
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        return (x, y, w, h)
    else:
        return None
    
    
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = align_histogram(frame)
        coordinates_red_cube = find_bright_green_object(frame)

        if coordinates_red_cube != None:
            x, y, h, w = coordinates_red_cube
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        _, buffer = cv2.imencode('.jpg', frame)
        data = buffer.tobytes()

        client_socket.sendall(len(data).to_bytes(4, byteorder='big'))
        client_socket.sendall(data)

        print(coordinates_red_cube)
except BaseException:
    client_socket.close()
    server_socket.close()


cap.release()
client_socket.close()
server_socket.close()
