import socket
import cv2
import numpy as np


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('192.168.2.217', 10000))  # IP-адрес Raspberry Pi и порт 10000
server_socket.listen(1)

print("Ожидание подключения клиента...")
client_socket, addr = server_socket.accept()
print(f"Подключен к {addr}")

def align_histogram(frame): 
    frame_rgb = cv2.split(frame) 
    mean1 = np.mean(frame_rgb) 
    desired_mean = 70
    alpha = mean1 / desired_mean 
    Inew_RGB = [] 
    for layer in frame_rgb: 
        Imin = layer.min() 
        Imax = layer.max() 
        Inew = ((layer - Imin) / (Imax - Imin)) ** alpha 
        Inew_RGB.append(Inew) 
    Inew = cv2.merge(Inew_RGB) 
    Inew_1 = (255*Inew).clip(0, 255).astype(np.uint8) 
    return Inew_1


cap = cv2.VideoCapture(0)

from ctrl_servo import CTRL_Servo
control_s = CTRL_Servo()
control_s.standart_pose()


def reduce_saturation(image, reduction_factor=0.5):

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hsv[:, :, 1] = hsv[:, :, 1] * reduction_factor

    desaturated_image = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    return desaturated_image

def reduce_brightness(image, reduction_factor=0.5):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hsv[:, :, 2] = np.clip(hsv[:, :, 2] * reduction_factor, 0, 255)
    
    darkened_image = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    return darkened_image


def find_red_cube(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_red1 = np.array([0, 70, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 70, 50])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)

    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) > 0:
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        return (x, y, w, h)
    else:
        return None
    

def find_bright_green_object(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_bright_green = np.array([35, 100, 100])
    upper_bright_green = np.array([150, 255, 255])

    mask = cv2.inRange(hsv, lower_bright_green, upper_bright_green)

    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) > 0:
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        return (x, y, w, h)
    else:
        return None
    
def find_blue_object(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_blue = np.array([100, 150, 0])
    upper_blue = np.array([140, 255, 255])

    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) > 0:
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        return (x, y, w, h)
    else:
        return None
    
def mask_top_corners(frame, corner_fraction=0.2):
    # Получаем размеры изображения
    height, width = frame.shape[:2]

    # Создаем маску черного цвета
    mask = np.zeros((height, width), dtype=np.uint8)

    # Определяем точки для вырезания треугольников в углах
    triangle_height = int(height * corner_fraction)
    triangle_width = int(width * corner_fraction)

    # Левый верхний треугольник
    pts1 = np.array([[0, 0], [triangle_width, 0], [0, triangle_height]], np.int32)
    pts1 = pts1.reshape((-1, 1, 2))
    
    # Правый верхний треугольник
    pts2 = np.array([[width, 0], [width - triangle_width, 0], [width, triangle_height]], np.int32)
    pts2 = pts2.reshape((-1, 1, 2))

    # Заполняем маску белым цветом, оставляя углы черными
    cv2.fillPoly(mask, [pts1, pts2], 255)

    # Инвертируем маску
    mask = cv2.bitwise_not(mask)

    # Применяем маску к изображению
    frame_masked = cv2.bitwise_and(frame, frame, mask=mask)

    return frame_masked

def find_gray_box(frame, min_area=500, max_area=10000):
    # Обрезаем верхнюю часть изображения
    height, width = frame.shape[:2]
    crop_fraction = 0.8
    frame = frame[:int(height * crop_fraction), :]

    # Преобразуем изображение в цветовое пространство HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Определяем диапазоны для темно-серого цвета (несколько диапазонов для разных оттенков)
    lower_gray1 = np.array([0, 0, 0])
    upper_gray1 = np.array([180, 120, 50])
    
    lower_gray2 = np.array([0, 0, 0])
    upper_gray2 = np.array([180, 100, 80])

    # Создаем маски для темно-серого цвета
    mask1 = cv2.inRange(hsv, lower_gray1, upper_gray1)
    mask2 = cv2.inRange(hsv, lower_gray2, upper_gray2)

    # Объединяем маски
    mask = cv2.bitwise_or(mask1, mask2)

    # Применяем морфологическую обработку для удаления шумов
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

    # Применяем Canny для улучшения контуров
    edges = cv2.Canny(mask, 50, 150)

    # Находим контуры
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    best_bbox = None
    best_area = 0

    # Фильтруем по площади и анализируем соотношение сторон
    for contour in contours:
        area = cv2.contourArea(contour)

        if min_area < area < max_area:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / float(h)

            # Фильтрация по форме: корзина вероятно имеет соотношение сторон близкое к 1
            if 0.8 < aspect_ratio < 1.2 and area > best_area:
                best_bbox = (x, y, w, h)
                best_area = area

    return best_bbox if best_bbox else None
    

def find_gray_mesh_box(frame):
    # Преобразуем изображение в серый цвет
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Применяем CLAHE для улучшения контраста
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced_gray = clahe.apply(gray)

    # Убираем шум с помощью GaussianBlur
    blurred = cv2.GaussianBlur(enhanced_gray, (5, 5), 0)

    # Используем детектор краев Canny для выявления сетчатой структуры
    edges = cv2.Canny(blurred, 50, 150)

    # Применяем морфологическую обработку для усиления контуров
    edges = cv2.dilate(edges, np.ones((3, 3), np.uint8), iterations=1)

    # Находим контуры на изображении
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    detected_boxes = []

    for contour in contours:
        area = cv2.contourArea(contour)
        
        # Фильтруем контуры по площади, чтобы исключить слишком маленькие или большие объекты
        if 50 < area < 10000:  # Настроим пороги под твою задачу
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / float(h)

            # Фильтрация по соотношению сторон
            if 0.8 < aspect_ratio < 1.2:  # Корзина может иметь почти квадратную форму
                detected_boxes.append((x, y, w, h))

    # Если найдено несколько объектов, выбираем самый большой
    if len(detected_boxes) > 0:
        largest_box = max(detected_boxes, key=lambda box: box[2] * box[3])
        return largest_box
    else:
        return None
    
    
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = align_histogram(frame)
        coordinates_red_cube = find_gray_box(frame)

        if coordinates_red_cube != None:
            x, y, h, w = coordinates_red_cube
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        _, buffer = cv2.imencode('.jpg', frame)
        data = buffer.tobytes()

        client_socket.sendall(len(data).to_bytes(4, byteorder='big'))
        client_socket.sendall(data)

        print(coordinates_red_cube)

except BaseException:

    client_socket.close()
    server_socket.close()


cap.release()
client_socket.close()
server_socket.close()
