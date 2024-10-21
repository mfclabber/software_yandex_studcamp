import socket
import pickle
import pathlib

import cv2
import time
import numpy as np

from perception.src.perception import Perception


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('192.168.2.217', 10000))

frame_count = 0
fps_count = 0
position_with_label = np.array([0.0, 0.0])

#change path to weight to up cam
path2model_weight = pathlib.Path("/home/mfclabber/client_yandex_studcamp/software_yandex_studcamp/python_src/perception/weights/main_model_weights.pt")
perception = Perception(path2weights=path2model_weight)

start_time = time.time()
# distances = 


while True:

    data_size = client_socket.recv(4)
    if not data_size:
        break
    size = int.from_bytes(data_size, byteorder='big')

    # data = client_socket.recv(size)

    data = bytearray()
    while len(data) < size:
        packet = client_socket.recv(size - len(data))
        if not packet:
            break
        data.extend(packet)

    image = np.frombuffer(data, dtype=np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

    frame_count += 1

    # if frame_count % 10 == 0: 

    image, target, positions_in_world, distances = perception.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    non_zero_indices = ((target['labels'] == 0.) | (target['labels'] == 0.)).nonzero(as_tuple=True)
    

    def calculate_area(bbox):
        width = bbox[2] - bbox[0]  # x_max - x_min
        height = bbox[3] - bbox[1]  # y_max - y_min
        return width * height

    # Вычисляем площади для каждого bbox
    # areas = np.array([calculate_area(bbox) for bbox in target['bboxes'][non_zero_indices]])
    # max_area_index = np.argmax(areas)
    # largest_bbox = target['bboxes'][max_area_index]


    if non_zero_indices[0].numel() > 0: 

        areas = np.array([calculate_area(bbox) for bbox in target['bboxes'][non_zero_indices]])
        max_area_index = np.argmax(areas)
        
        label_index = non_zero_indices[0][0].item()
        bbox_with_label = target['bboxes'][label_index]
        score_with_label = target['scores'][label_index]
        position_with_label = positions_in_world[max_area_index]

        print(f"DISTANCE {distances[max_area_index]}")

        if distances[max_area_index] < 0.19 and 2 in target['labels'] :
            break   

    
    current_time = time.time()
    fps = fps_count / (current_time - start_time) if current_time > start_time else 0

    # cv2.putText(image, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow('YOLOv8 Detection', cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    fps_count = 0
    start_time = current_time
    

    # print(target)
    # print(positions_in_world)

    data2 = pickle.dumps(position_with_label)
    client_socket.sendall(len(data2).to_bytes(4, byteorder='big'))
    client_socket.sendall(data2)
    #client_socket.sendall(positions_in_world)

    print(position_with_label)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

client_socket.close()
cv2.destroyAllWindows()