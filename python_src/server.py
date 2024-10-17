import socket
import cv2
import numpy as np

# Настройки сервера
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('192.168.2.217', 10000))  # IP-адрес Raspberry Pi и порт 10000
server_socket.listen(1)

print("Ожидание подключения клиента...")
client_socket, addr = server_socket.accept()
print(f"Подключен к {addr}")

# Подключение к камере
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Кодирование изображения в JPEG
    _, buffer = cv2.imencode('.jpg', frame)
    data = buffer.tobytes()

    # Передаем размер изображения
    client_socket.sendall(len(data).to_bytes(4, byteorder='big'))
    client_socket.sendall(data)

cap.release()
client_socket.close()
server_socket.close()
