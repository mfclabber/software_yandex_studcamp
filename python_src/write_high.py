import cv2

# URL для подключения к левой IP-камере
ip_camera_url_left = "rtsp://Admin:rtf123@192.168.2.250/251:554/1/1"

# Создаем объект VideoCapture для захвата видео с левой IP-камеры
video_capture_left = cv2.VideoCapture(ip_camera_url_left)

# Проверяем, удалось ли открыть поток с камеры
if not video_capture_left.isOpened():
    print("Не удалось подключиться к левой IP-камере")
    exit()

# Получаем параметры видео (ширину, высоту, частоту кадров)
frame_width = int(video_capture_left.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(video_capture_left.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(video_capture_left.get(cv2.CAP_PROP_FPS))

# Настраиваем кодек и создаем объект для записи видео
fourcc = cv2.VideoWriter_fourcc(*'XVID')
output_file_left = 'output_left.avi'

out_left = cv2.VideoWriter(output_file_left, fourcc, fps, (frame_width, frame_height))

# Цикл для захвата кадров и записи их в файл
while True:
    ret_left, frame_left = video_capture_left.read()

    if not ret_left:
        print("Ошибка захвата видео с левой камеры")
        break

    # Записываем захваченные кадры в файл
    out_left.write(frame_left)

    # Показываем видео в реальном времени (опционально)
    cv2.imshow('Left Camera', frame_left)

    # Выход по нажатию клавиши 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Освобождаем ресурсы
video_capture_left.release()
out_left.release()
cv2.destroyAllWindows()