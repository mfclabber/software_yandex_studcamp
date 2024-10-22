import os
import cv2
import sys
import time
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import xr_gpio as gpio
from test_move import RobotDirection
from ctrl_servo import CTRL_Servo

MIDDLE_X_IMAGE = 320


def align_histogram(frame): 
    frame_rgb = cv2.split(frame) 
    mean1 = np.mean(frame_rgb) 
    desired_mean = 70 
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
    

def find_green_object(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_bright_green = np.array([35, 100, 100])
    upper_bright_green = np.array([85, 255, 255])

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
 
    
def find_gray_box(frame, min_area=500, max_area=10000):
    # Обрезаем верхнюю часть изображения
    height, width = frame.shape[:2]
    crop_fraction = 0.8
    frame = frame[:int(height * crop_fraction), :]

    # Преобразуем изображение в цветовое пространство HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Применяем CLAHE для увеличения контрастности
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    lab[..., 0] = clahe.apply(lab[..., 0])
    frame = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Определяем узкие диапазоны для темно-серого цвета в HSV
    lower_gray = np.array([0, 0, 0])
    upper_gray = np.array([180, 50, 60])  # Уменьшили верхнюю границу яркости для темного серого

    # Создаем маску для темно-серого цвета
    mask = cv2.inRange(hsv, lower_gray, upper_gray)

    # Применяем морфологическую обработку для удаления шумов
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # Применяем Canny для улучшения контуров
    edges = cv2.Canny(mask, 20, 150)

    # Находим контуры
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    best_bbox = None
    best_area = 0

    # Фильтруем по площади, анализируем соотношение сторон и форму
    for contour in contours:
        area = cv2.contourArea(contour)

        if min_area < area < max_area:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / float(h)

            # Проверяем форму (квадратоподобная) и площадь
            if 0.8 < aspect_ratio < 3 and area > best_area:
                best_bbox = (x, y, w, h)
                best_area = area

    return best_bbox if best_bbox else None
    

class PIDController:
    def __init__(self, Kp, Ki, Kd, setpoint=0):
        self.Kp = Kp 
        self.Ki = Ki 
        self.Kd = Kd
        self.setpoint = setpoint

        self.previous_error = 0 
        self.integral = 0 
        self.last_time = time.time()

    def update(self, current_value):
        error = current_value - self.setpoint

        current_time = time.time()
        delta_time = current_time - self.last_time
        delta_error = error - self.previous_error

        P = self.Kp * error

        self.integral += error * delta_time
        I = self.Ki * self.integral

        D = 0
        if delta_time > 0:
            D = self.Kd * (delta_error / delta_time)

        output = P + I + D

        self.previous_error = error
        self.last_time = current_time

        return output
    

def calculate_steering_angle(target_position):
    steering_angle = pid.update(target_position)
    if isinstance(steering_angle, np.ndarray):
        # Если это массив, примените ограничение поэлементно
        steering_angle = np.max(np.clip(steering_angle, -70, 70))
    else:
        # Если это скаляр
        steering_angle = max(-70, min(70, steering_angle))

    

    return steering_angle


def calculate_speed(current_position, target_position, K1):
    error_a = (target_position[0] - current_position[0])*3.14/4
    error_r = np.linalg.norm(target_position - current_position)

    #print("ERRORS")
    # print("ANGLE:",error_a,"DISTANCE: ",error_r)

    speed = K1 * error_r * np.cos(error_a)
    speed = max(0, min(100, speed))
 
    return speed

pid = PIDController(Kp=0.15, Ki=0.0, Kd=0.03142
                    , setpoint=320)

def follow2cube():
    cap = cv2.VideoCapture(0)
    go = RobotDirection()
    control_s = CTRL_Servo()

    control_s.standart_pose()

    try:
        # CUBE
        coordinates_object = 320
        while coordinates_object != None:
            ret, frame = cap.read()
            frame = align_histogram(frame)
            if not ret:
                break

            coordinates_object = find_red_cube(frame)

            if coordinates_object != None:
                x, y, h, w = coordinates_object 
                position_with_label = x

            _, buffer = cv2.imencode('.jpg', frame)
            data = buffer.tobytes()

            steering_angle = float(calculate_steering_angle(position_with_label))
            speed = 20

            print(steering_angle, speed)
            go.forward_with_angle(speed, steering_angle)

            if gpio.digital_read(gpio.IR_M) == 0:
                time.sleep(0.4)
                go.stop()
                break

        # time.sleep(1)
        go.stop()
        control_s.take_cube()
        

    except KeyboardInterrupt:
        go.stop()

    go.stop()


current_position = np.array([0.0, 0.0])
position_with_label = np.array([0.0, 0.0])
coordinates_object = 320


coordinates = []
cap = cv2.VideoCapture(0)
go = RobotDirection()
control_s = CTRL_Servo()

control_s.standart_pose()

pid = PIDController(Kp=0.15, Ki=0.0, Kd=0.03, setpoint=320)
avg_coordinates = []
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = align_histogram(frame)

    # Детектируем объект 10 раз
    for i in range(30):
        coordinates_gray_box = find_gray_box(frame)
        if coordinates_gray_box is not None:
            coordinates.append(coordinates_gray_box)

    if len(coordinates) == 30:
        # Вычисляем средние значения
        avg_coordinates = np.mean(coordinates, axis=0).astype(int)
        x, y, w, h = avg_coordinates
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Очищаем список для следующего цикла
        coordinates = []

    _, buffer = cv2.imencode('.jpg', frame)
    data = buffer.tobytes()

    steering_angle = float(calculate_steering_angle(avg_coordinates))
    speed = 20

    print(steering_angle, speed)
    go.forward_with_angle(speed, steering_angle)

    if gpio.digital_read(gpio.IR_L) == 0 or gpio.digital_read(gpio.IR_R) == 0:
        time.sleep(0.1)
        go.stop()
        object_is_find = True
        break

control_s.drop_object()


# current_position = np.array([0.0, 0.0])
# position_with_label = np.array([0.0, 0.0])
# coordinates_object = 320

# follow2cube()
    
# if __name__ == "__main__":

#     cap = cv2.VideoCapture(0)
#     go = RobotDirection()
#     control_s = CTRL_Servo()

#     control_s.standart_pose()

#     pid = PIDController(Kp=0.15, Ki=0.0, Kd=0.03, setpoint=320)
#     try:
#         # CUBE
#         # while coordinates_object != None:
#         #     ret, frame = cap.read()
#         #     frame = align_histogram(frame)
#         #     if not ret:
#         #         break

#         #     coordinates_object = find_bright_green_object(frame)

#         #     if coordinates_object != None:
#         #         x, y, h, w = coordinates_object 
#         #         position_with_label = x

#         #     _, buffer = cv2.imencode('.jpg', frame)
#         #     data = buffer.tobytes()

#         #     # print(coordinates_object)

#         #     # if type(position_with_label) == int:
#         #     #     steering_angle = 10
#         #     #     speed = 0
#         #     # else:
#         #     steering_angle = float(calculate_steering_angle(position_with_label))
#         #     speed = 40
#         #         # speed = calculate_speed(current_position, position_with_label, K1)
#         #     print(steering_angle, speed)
#         #     # print()

#         #     go.forward_with_angle(speed, steering_angle)


#         # BUTTON
#         # object_is_find = False

#         # while object_is_find != True:
#         #     ret, frame = cap.read()
#         #     frame = align_histogram(frame)
#         #     if not ret:
#         #         break

#         #     coordinates_object = find_blue_object(frame)

#         #     if coordinates_object != None:
#         #         x, y, h, w = coordinates_object 
#         #         position_with_label = x

#         #     _, buffer = cv2.imencode('.jpg', frame)
#         #     data = buffer.tobytes()

#         #     # print(coordinates_object)

#         #     # if type(position_with_label) == int:
#         #     #     steering_angle = 10
#         #     #     speed = 0
#         #     # else:
#         #     steering_angle = float(calculate_steering_angle(position_with_label))
#         #     speed = 20
#         #         # speed = calculate_speed(current_position, position_wiwwwwwwwwth_label, K1)
#         #     print(steering_angle, speed)
#         #     # print()

#         #     go.forward_with_angle(speed, steering_angle)

#         #     if gpio.digital_read(gpio.IR_M) == 0:
#         #         go.stop()
#         #         object_is_find = True
#         #         break

#         # control_s.push_button()


#         # GET CUBE AND GET DOWN TO BOX
#         while coordinates_object != None:
#             ret, frame = cap.read()
#             frame = align_histogram(frame)
#             if not ret:
#                 break

#             coordinates_object = find_red_cube(frame)

#             if coordinates_object != None:
#                 x, y, h, w = coordinates_object 
#                 position_with_label = x

#             _, buffer = cv2.imencode('.jpg', frame)
#             data = buffer.tobytes()

#             steering_angle = float(calculate_steering_angle(position_with_label))
#             speed = 30

#             print(steering_angle, speed)
#             go.forward_with_angle(speed, steering_angle)

#             if gpio.digital_read(gpio.IR_M) == 0:
#                 time.sleep(0.1)
#                 go.stop()
#                 object_is_find = True
#                 break
        
#         go.stop()
#         time.sleep(0.5)
#         control_s.take_cube()

#         # object_is_find = False
#         # while object_is_find != True:
#         #     ret, frame = cap.read()
#         #     frame = align_histogram(frame)
#         #     if not ret:
#         #         break

#         #     coordinates_object = find_gray_box(frame)

#         #     if coordinates_object != None:
#         #         x, y, h, w = coordinates_object 
#         #         position_with_label = x

#         #     _, buffer = cv2.imencode('.jpg', frame)
#         #     data = buffer.tobytes()

#         #     steering_angle = float(calculate_steering_angle(position_with_label))
#         #     speed = 30

#         #     print(steering_angle, speed)
#         #     go.forward_with_angle(speed, steering_angle)

#         #     if gpio.digital_read(gpio.IR_L) == 0 or gpio.digital_read(gpio.IR_R) == 0:
#         #         time.sleep(0.1)
#         #         go.stop()
#         #         object_is_find = True
#         #         break

#         control_s.drop_object()
        

#     except KeyboardInterrupt:
#         go.stop()

#     go.stop()

#     # control_s.push_button()
#     control_s.standart_pose()
#     # control_s.take_cube()
#     # time.sleep(2)
#     # control_s.drop_object()