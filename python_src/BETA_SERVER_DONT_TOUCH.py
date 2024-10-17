import socket
import cv2
import pickle
import struct

# Настройки сокета
server_ip = '192.168.2.217'
server_port = 10001

# Создание сокета
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((server_ip, server_port))
server_socket.listen(1)
print('Ожидание подключения клиента...')

conn, addr = server_socket.accept()
print('Подключен клиент:', addr)

while True:
    # Чтение изображения с камеры и сжатие
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()

    # Сжимаем изображение в формат JPEG для уменьшения объема данных
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]  # Сжатие изображения
    result, frame_encoded = cv2.imencode('.jpg', frame, encode_param)

    # Сериализация изображения
    data = pickle.dumps(frame_encoded, protocol=pickle.HIGHEST_PROTOCOL)
    size = len(data)

    # Отправка размера и изображения
    conn.sendall(struct.pack(">L", size))
    conn.sendall(data)

    # Получение и обработка данных от клиента
    received_size = struct.unpack(">L", conn.recv(4))[0]
    data = b""
    while len(data) < received_size:
        data += conn.recv(4096)
    matrix = pickle.loads(data)
    print("Получена матрица от клиента:", matrix)

conn.close()
server_socket.close()
