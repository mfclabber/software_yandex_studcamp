import socket
import pickle
import cv2
import time
import numpy as np
from test_move import RobotDirection
from ctrl_servo import CTRL_Servo

control_s = CTRL_Servo()
# control_s.standart_pose()

go = RobotDirection()

MIDDLE_X_IMAGE = 320


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


class PIDController:
    def __init__(self, Kp, Ki, Kd, setpoint=0):
        self.Kp = Kp  # Пропорциональный коэффициент
        self.Ki = Ki  # Интегральный коэффициент
        self.Kd = Kd  # Дифференциальный коэффициент
        self.setpoint = setpoint  # Желаемая цель (напр., центр кубика)

        self.previous_error = 0  # Ошибка на предыдущем шаге
        self.integral = 0  # Интегральная сумма ошибок
        self.last_time = time.time()  # Время последнего вызова

    def update(self, current_value):
        # Шаг 1: Вычисляем ошибку
        error = current_value - self.setpoint

        # Шаг 2: Вычисляем разницу времени
        current_time = time.time()
        delta_time = current_time - self.last_time
        delta_error = error - self.previous_error

        # Шаг 3: Пропорциональная составляющая
        P = self.Kp * error

        # Шаг 4: Интегральная составляющая
        self.integral += error * delta_time
        I = self.Ki * self.integral

        # Шаг 5: Дифференциальная составляющая
        D = 0
        if delta_time > 0:
            D = self.Kd * (delta_error / delta_time)

        # Шаг 6: Рассчитываем итоговое значение управления
        output = P + I + D

        # Шаг 7: Сохраняем предыдущие значения для следующего шага
        self.previous_error = error
        self.last_time = current_time

        return output
    
    
pid = PIDController(Kp=0.1, Ki=0.0, Kd=0.05, setpoint=320)


def calculate_steering_angle(target_position):
    steering_angle = pid.update(target_position)
    steering_angle = max(-100, min(100, steering_angle))

    return steering_angle


def calculate_speed(current_position, target_position, K1):
    error_a = (target_position[0] - current_position[0])*3.14/4
    error_r = np.linalg.norm(target_position - current_position)

    #print("ERRORS")
    # print("ANGLE:",error_a,"DISTANCE: ",error_r)

    speed = K1 * error_r * np.cos(error_a)
    speed = max(0, min(100, speed))
 
    return speed



# Настройки сервера
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('', 10000))  # IP-адрес Raspberry Pi и порт 10000
server_socket.listen(1)

server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 4096)

print("Ожидание подключения клиента...")
client_socket, addr = server_socket.accept()
print(f"Подключен к {addr}")

# Подключение к камере
cap = cv2.VideoCapture(0)


current_position = np.array([0.0, 0.0])
position_with_label = np.array([0.0, 0.0])

frame_count = 0
fps_count = 0
start_time = time.time()
fps = 0 
print("SERVER RUN")

# Параметры контроллера
K1 = 10
K2 = 100

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


try:
    while True:
        # go.stop()
        ret, frame = cap.read()
        if not ret:
            print("Не удалось получить кадр")
            break
        print(f"FRAME WIDTH: {frame.shape[1]}")

        # frame = align_histogram(frame)
        
        _, buffer = cv2.imencode('.jpg', frame)
        data = buffer.tobytes()

        client_socket.sendall(len(data).to_bytes(64, byteorder='big'))
        client_socket.sendall(data)

        data_size = client_socket.recv(4)
        if not data_size:
            break
        size = int.from_bytes(data_size, byteorder='big')

        data2 = bytearray()
        while len(data2) < size:
            packet = client_socket.recv(size - len(data2))
            if not packet:
                break
            data2 += packet

        # print(f"{find_red_cube(frame)}")

        position_with_label = pickle.loads(data2)

        if type(position_with_label) == int:
            steering_angle = 10
            speed = 0
        else:
            steering_angle = float(calculate_steering_angle(position_with_label))
            speed = 35
            # speed = calculate_speed(current_position, position_with_label, K1)
            print(steering_angle, 35)

        fps_count += 1 

        # if abs(steering_angle) > 50 and speed < 30:
        #     speed += 10

        # print(f"FPS {fps}\n")
        # go.forward_with_angle(speed, steering_angle)

except ...:

    go.stop()
    client_socket.close()
    server_socket.close()

go.stop()
cap.release()

client_socket.close()
server_socket.close()

# go.forward_with_angle(50, 0)
# time.sleep(0.5)
# go.stop()

# control_s.take_cube()
# time.sleep(2)
# control_s.drop_object()
# time.sleep(1)
# control_s.standart_pose()