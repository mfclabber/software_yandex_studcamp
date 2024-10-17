import socket
import pathlib
import numpy as np
import cv2
import time
from perception.src.perception import Perception

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('192.168.2.217', 10000))

frame_count = 0
fps_count = 0

path2model_weight = pathlib.Path("/home/itmo/software_yandex_studcamp/python_src/perception/weights/main_model_weights.pt")
perception = Perception(path2weights=path2model_weight)


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

    frame_count += 1

    if frame_count % 10 == 0:

        image, target, positions_in_world, distances = perception.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        non_zero_indices = ((target['labels'] == 0.) | (target['labels'] == 1.)).nonzero(as_tuple=True)
        print(non_zero_indices)
        if non_zero_indices[0].numel() > 0:  # Используем numel() для проверки наличия элементов
            
            label_index = non_zero_indices[0][0].item()

            # Используем только если label_index был найден
            bbox_with_label = target['bboxes'][label_index]
            score_with_label = target['scores'][label_index]
            position_with_label = positions_in_world[label_index]
            # print(f"DISTANCE {distances[label_index]}\n")
            # if distances[label_index] < 22:
            #     break   

        
        current_time = time.time()
        fps = fps_count / (current_time - start_time) if current_time > start_time else 0

        # cv2.putText(image, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow('YOLOv8 Detection', cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        # cv2.imwrite('output_image.png', image)
        # time.sleep(0.01)

        fps_count = 0
        start_time = current_time

        print(target)
        print(positions_in_world)

client_socket.close()
cv2.destroyAllWindows()