import pathlib
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import cv2
import time
import threading

from perception.src.perception import Perception
from test_move import RobotDirection

go = RobotDirection()

# if __name__ == "main":
path2model_weight = pathlib.Path("/home/itmo/software_yandex_studcamp/python_src/perception/weights/main_model_weights.pt")

perception = Perception(path2weights=path2model_weight)
# received_event = threading.Event() 
# for first testing
# image, target, positions_in_world, distances = perception.process(image=np.array(Image.open("/home/mfclabber/yandex_camp_software/data/main_train_data/train/images/frame_0232.jpg")))
# cv2.imwrite("image.png", cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

# perception.process_thread(port_camera="/dev/video0")
# yolo_thread = perception.process_thread(port_camera="/dev/video0")
# perception.process_video()

# threading.Thread(target=perception.get_data, args=(yolo_thread, received_event)).start()
# perception.get_data()
# while True:
#     if received_event.is_set():
#         received_event.clear()


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

cap = cv2.VideoCapture("/dev/video0")

if not cap.isOpened():
    print("Не удалось открыть камеру")
    exit()

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

current_position = np.array([0.0, 0.0])
position_with_label = np.array([0.0, 0.0])

# steering_angle = calculate_steering_angle(current_position, position_with_label, Kp)
# speed = calculate_speed(current_position, position_with_label)
# print(steering_angle[0], speed)
try:
    while True:
        ret, frame = cap.read()
        # Преобразование в цветовую модель YUV
        # yuv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)

        # # Выравнивание гистограммы только по яркостному каналу (Y)
        # yuv_img[:, :, 0] = cv2.equalizeHist(yuv_img[:, :, 0])

        # # Преобразование обратно в BGR
        # frame= cv2.cvtColor(yuv_img, cv2.COLOR_YUV2BGR)

        # height, width = frame.shape[:2]
        # mask = np.zeros((height, width), dtype=np.float32)

        # # Верхняя часть затемнена, нижняя - без изменений (градиентная маска)
        # for i in range(height):
        #     mask[i, :] = i / height

        # # Преобразование изображения в HSV для работы с яркостью
        # hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # # Применение маски к каналу яркости (Value)
        # hsv_image[:, :, 2] = (hsv_image[:, :, 2] * (1 - 0.5 * mask)).astype(np.uint8)
        # frame = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)

        if not ret:
            print("Не удалось получить кадр")
            break

        frame_count += 1

        if frame_count % 10 == 0:

            go.stop()

            image, target, positions_in_world, distances = perception.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            non_zero_indices = ((target['labels'] == 0.) | (target['labels'] == 1.) | (target['labels'] == 2.) | (target['labels'] == 3.)).nonzero(as_tuple=True)
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
            # cv2.imshow('YOLOv8 Detection', cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            # cv2.imwrite('output_image.png', image)
            # time.sleep(0.01)

            fps_count = 0
            start_time = current_time
    # KeyboardInterrupt
            # print("Данные отправлены в очередь")
            # time.sleep(0.01)
            print(target)
            print(positions_in_world)
            

        steering_angle = calculate_steering_angle(current_position, position_with_label, K1, K2)
        speed = calculate_speed(current_position, position_with_label, K1)
        print(steering_angle, speed)

            # cv2.imwrite("image.png", cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        fps_count += 1 
        # print(f"FPS {fps}\n")
        go.forward_with_angle(speed, steering_angle)



        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    # cv2.destroyAllWindows()
except KeyboardInterrupt:
    go.stop()

go.stop()
