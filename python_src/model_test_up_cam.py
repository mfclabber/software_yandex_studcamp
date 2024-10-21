import cv2
import numpy as np
from ultralytics import YOLO
import time
from frame_edit_func import undistort_frame

'''
classes ['G_O button', 'P_B button', 'cube', 'green base', 'red base', 'robot with green', 'robot with red']
'''
ID2LABEL_UPCAM = dict([
            (0, "G_O button"),
            (1, "P_B button"), 
            (2, "cube"),
            (3, "green base"),
            (4, "red base"),
            (5, "robot with green"),
            (6, "robot with red")
        ])
# print(ID2LABEL_UPCAM)

annotated_frame = []

#rtsp_url = "rtsp://Admin:rtf123@192.168.2.250:554/1/1"
reconnect_delay = 0.05 # Задержка перед повторным подключением (в секундах)
max_retries = 5      

def YOLO_UP_CAM(rtsp_url):
    list_of_point = []
    def initialize_video_capture(url):
        cap = cv2.VideoCapture(url)
        return cap

    cap = initialize_video_capture(rtsp_url)
    retries = 0

    while not cap.isOpened():
        if retries >= max_retries:
            print(f"Не удалось подключиться к видеопотоку после {max_retries} попыток.")
            return
        print(f"Не удалось подключиться к видеопотоку. Попытка {retries + 1}/{max_retries} через {reconnect_delay} секунд.")
        time.sleep(reconnect_delay)
        cap = initialize_video_capture(rtsp_url)
        retries += 1

    print("Успешно подключено к видеопотоку.")

    try:
        model = YOLO("/home/sruwer/Downloads/best_12.pt")  # Убедитесь, что файл best.pt находится в рабочей директории
    except Exception as e:
        print(f"Ошибка загрузки модели YOLO: {e}")
        cap.release()
        return
    frame_count = 0
    shown_frame_count = 0
    while True:
        ret, frame = cap.read()
        frame_count+=1
        if not ret:
            print("Потеряно соединение с видеопотоком. Попытка повторного подключения...")
            cap.release()
            retries = 0
            while retries < max_retries:
                cap = initialize_video_capture(rtsp_url)
                if cap.isOpened():
                    print("Успешно восстановлено соединение с видеопотоком.")
                    break
                else:
                    retries += 1
                    print(f"Попытка {retries}/{max_retries} не удалась. Повтор через {reconnect_delay} секунд.")
                    time.sleep(reconnect_delay)
            if not cap.isOpened():
                print(f"Не удалось восстановить соединение после {max_retries} попыток. Завершение работы.")
                break
            continue
    
        undistorted_frame = undistort_frame(frame)
        crop_image = undistorted_frame[:,270 : 1520]
        
        try:
            results = model(crop_image)[0]
        except Exception as e:
            print(f"Ошибка при применении модели YOLO: {e}")
            continue
        

        for box in results.boxes:
            bbox = box.xyxy[0].cpu().numpy()
            x_min, y_min, x_max, y_max = bbox

            center_x = int((x_min + x_max) / 2)
            center_y = int((y_min + y_max) / 2)

            object_class = int(box.cls[0].cpu().numpy())
            print(f"Координаты центра: ({center_x}, {center_y}), Класс: {object_class}")
            list_of_point.append([center_x, center_y, object_class])

        annotated_frame = results.plot()

        # cv2.imshow('YOLO Detected Frame', annotated_frame)

        shown_frame_count += 1

        if shown_frame_count > 0:
            break
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Получен сигнал на завершение работы.")
            break

    cap.release()
    cv2.destroyAllWindows()
    return crop_image, list_of_point, annotated_frame

