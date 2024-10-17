import socket
import numpy as np
import cv2

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('192.168.2.217', 10000))

while True:

    data_size = client_socket.recv(4)
    if not data_size:
        break
    size = int.from_bytes(data_size, byteorder='big')

    data = bytearray()
    while len(data) < size:
        packet = client_socket.recv(size - len(data))
        if not packet:
            break
        data.extend(packet)

    image = np.frombuffer(data, dtype=np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

client_socket.close()
cv2.destroyAllWindows()