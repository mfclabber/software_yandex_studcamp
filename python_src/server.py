import socket
import pickle
import cv2
import time
import numpy as np
from test_move import RobotDirection
from ctrl_servo import CTRL_Servo

control_s = CTRL_Servo()
control_s.standart_pose()

go = RobotDirection()



def calculate_steering_angle(current_position, target_position, K1, K2):
    error_a = (target_position[0] - current_position[0])*3.14/4
    error_r = np.linalg.norm(target_position - current_position)

    steering_angle = K1 * error_r * np.cos(error_a) * np.sin(error_a) + K2 * error_a

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
K1 = 60
K2 = 100


try:
    while True:
        # go.stop()
        ret, frame = cap.read()

        if not ret:
            print("Не удалось получить кадр")
            break

        _, buffer = cv2.imencode('.jpg', frame)
        data = buffer.tobytes()

        client_socket.sendall(len(data).to_bytes(4, byteorder='big'))
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

        print("Данные получены")

        position_with_label = pickle.loads(data2)

        if type(position_with_label) == int:
            steering_angle = 10
            speed = 0
        else:
            steering_angle = calculate_steering_angle(current_position, position_with_label, K1, K2)
            speed = calculate_speed(current_position, position_with_label, K1)
            print(steering_angle, speed)

        #fps_count += 1 

        # if abs(steering_angle) > 50 and speed < 30:
        #     speed += 10

        # print(f"FPS {fps}\n")
        go.forward_with_angle(speed, steering_angle)
        time.sleep(1)

    cap.release()

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