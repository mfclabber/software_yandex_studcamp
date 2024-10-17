import socket
import cv2
import time
import numpy as np
from test_move import RobotDirection

go = RobotDirection()


def calculate_steering_angle(current_position, target_position, K1, K2):
    error_a = (target_position[0] - current_position[0])*3.14/4
    error_r = np.linalg.norm(target_position - current_position)

    steering_angle = K1 * error_r * np.cos(error_a) * np.sin(error_a) + K2 * error_a

    steering_angle = max(-100, min(100, steering_angle)) + 5

    return steering_angle


def calculate_speed(current_position, target_position, K1):
    error_a = (target_position[0] - current_position[0])*3.14/4
    error_r = np.linalg.norm(target_position - current_position)

    #print("ERRORS")
    # print("ANGLE:",error_a,"DISTANCE: ",error_r)

    speed = K1 * error_r * np.cos(error_a)

    # Устанавливаем скорость в зависимости от расстояния (линейная зависимость)
    speed = max(0, min(100, speed))  # скорость от 0 до 100, в зависимости от расстояния

    return speed



# Настройки сервера
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('192.168.2.217', 10000))  # IP-адрес Raspberry Pi и порт 10000
server_socket.listen(1)

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
K1 = 140
K2 = 30
Kd = 0.1
dt = 0.1


try:
    while True:
        ret, frame = cap.read()

        if not ret:
            print("Не удалось получить кадр")
            break

        _, buffer = cv2.imencode('.jpg', frame)
        data = buffer.tobytes()

        client_socket.sendall(len(data).to_bytes(4, byteorder='big'))
        client_socket.sendall(data)


        # Получаем данные
            

        steering_angle = calculate_steering_angle(current_position, position_with_label, K1, K2)
        speed = calculate_speed(current_position, position_with_label, K1)
        print(steering_angle, speed)

        fps_count += 1 
        # print(f"FPS {fps}\n")
        go.forward_with_angle(speed, steering_angle)

    cap.release()
except KeyboardInterrupt:
    go.stop()

go.stop()

cap.release()
client_socket.close()
server_socket.close()
