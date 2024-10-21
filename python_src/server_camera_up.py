import socket
import pickle
import cv2
import time
import numpy as np



# Настройки сервера
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('', 10000))  # IP-адрес Raspberry Pi и порт 10000
server_socket.listen(1)

server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 4096)

print("Ожидание подключения клиента...")
client_socket, addr = server_socket.accept()
print(f"Подключен к {addr}")

start_time = time.time()
print("SERVER RUN")

try:

    data_size = client_socket.recv(4)
    # if not data_size:
    #     return None

    size = int.from_bytes(data_size, byteorder='big')

    data2 = bytearray()
    while len(data2) < size:
        packet = client_socket.recv(size - len(data2))
        if not packet:
            break
        data2 += packet

    array_from_camera_up = pickle.loads(data2)

except ...:
    client_socket.close()
    server_socket.close()


print(array_from_camera_up)

client_socket.close()
server_socket.close()