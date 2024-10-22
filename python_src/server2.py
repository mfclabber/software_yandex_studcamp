import socket
import cv2
import numpy as np


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_socket.bind(('192.168.2.217', 10000))  # IP-адрес Raspberry Pi и порт 10000
server_socket.bind(('172.20.10.5', 10000))  # IP-адрес Raspberry Pi и порт 10000
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

    # Применяем CLAHE для увеличения контрастности
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    lab[..., 0] = clahe.apply(lab[..., 0])
    frame = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Определяем узкие диапазоны для темно-серого цвета в HSV
    lower_gray = np.array([0, 0, 0])
    upper_gray = np.array([180, 50, 60])  # Уменьшили верхнюю границу яркости для темного серого

    # Создаем маску для темно-серого цвета
    mask = cv2.inRange(hsv, lower_gray, upper_gray)

    # Применяем морфологическую обработку для удаления шумов
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # Применяем Canny для улучшения контуров
    edges = cv2.Canny(mask, 20, 150)

    # Находим контуры
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    best_bbox = None
    best_area = 0

    # Фильтруем по площади, анализируем соотношение сторон и форму
    for contour in contours:
        area = cv2.contourArea(contour)

        if min_area < area < max_area:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / float(h)

            # Проверяем форму (квадратоподобная) и площадь
            if 0.8 < aspect_ratio < 3 and area > best_area:
                best_bbox = (x, y, w, h)
                best_area = area

    return best_bbox if best_bbox else None

avg_coordinates = []
coordinates = []
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = align_histogram(frame)

    # Детектируем объект 10 раз
    for i in range(30):
        coordinates_gray_box = find_gray_box(frame)
        if coordinates_gray_box is not None:
            coordinates.append(coordinates_gray_box)

    if len(coordinates) == 30:
        # Вычисляем средние значения
        avg_coordinates = np.mean(coordinates, axis=0).astype(int)
        x, y, w, h = avg_coordinates
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Очищаем список для следующего цикла
        coordinates = []

    _, buffer = cv2.imencode('.jpg', frame)
    data = buffer.tobytes()

    client_socket.sendall(len(data).to_bytes(4, byteorder='big'))
    client_socket.sendall(data)

    print(avg_coordinates)

# except BaseException:

#     client_socket.close()
#     server_socket.close()


cap.release()
client_socket.close()
server_socket.close()