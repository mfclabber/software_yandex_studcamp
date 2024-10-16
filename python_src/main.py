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
print("YOLO RUN")
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
    error_r = (target_position[1] - current_position[1])

    steering_angle = K1 * error_r * np.cos(error_a) * np.sin(error_a) + K2 * error_a

    steering_angle = max(-100, min(100, steering_angle))

    return steering_angle

# Контроллер для скорости (например, постоянная)
def calculate_speed(current_position, target_position, K1):
    error_a = (target_position[0] - current_position[0])*3.14/4
    error_r = (target_position[1] - current_position[1])

    print("ERRORS:")
    print("ANGLE:",error_a,"DISTANCE: ",error_r)

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
print("YOLOv8 RUN!!!")

# Параметры контроллера
K1 = 50
K2 = 10
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
        channels = cv2.split(frame)

        equalized_channels = []
        for channel in channels:
            equalized_channels.append(cv2.equalizeHist(channel))

        frame = cv2.merge(equalized_channels)
        lab_img = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)

        lab_img[:, :, 1] = cv2.add(lab_img[:, :, 1], 5)
        frame = cv2.cvtColor(lab_img, cv2.COLOR_LAB2BGR)

        if not ret:
            print("Не удалось получить кадр")
            break

        frame_count += 1

        if frame_count % 1 == 0:
            image, target, positions_in_world, distances = perception.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            # Получаем позиции нужных кнопок
            # if len(target) != 0:
                # print()
            non_zero_indices = ((target['labels'] == 0.) | (target['labels'] == 1.) | (target['labels'] == 2.) | (target['labels'] == 3.)).nonzero(as_tuple=True)
            print(non_zero_indices)
            if non_zero_indices[0].numel() > 0:  # Используем numel() для проверки наличия элементов
                
                label_index = non_zero_indices[0][0].item()

                # Используем только если label_index был найден
                bbox_with_label = target['bboxes'][label_index]
                score_with_label = target['scores'][label_index]
                position_with_label = positions_in_world[label_index]
                print(f"DISTANCE {distances[label_index]}\n")
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

        fps_count += 1 

        steering_angle = calculate_steering_angle(current_position, position_with_label, K1, K2)
        speed = calculate_speed(current_position, position_with_label, K1)
        print(steering_angle, speed)
        # go.forward_with_angle(speed, steering_angle)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        cv2.imwrite("image.png", image)

    cap.release()
    # cv2.destroyAllWindows()
except KeyboardInterrupt:
    go.stop()

go.stop()