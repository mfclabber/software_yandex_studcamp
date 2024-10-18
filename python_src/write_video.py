import cv2

# Захват видео с камеры (индекс 0 обычно означает основную камеру)
cap = cv2.VideoCapture(0)

# Проверяем, что камера открыта успешно
if not cap.isOpened():
    print("Не удалось получить доступ к камере")
    exit()

# Получаем ширину, высоту и FPS видео
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))




# Определяем кодек и создаем объект записи видео
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Кодек для формата MP4
out = cv2.VideoWriter('output.mp4', fourcc, fps, (frame_width, frame_height))

print("Началась запись видео. Нажмите 'q', чтобы остановить.")

while True:
    ret, frame = cap.read()  # Считываем кадр с камеры
    if not ret:
        print("Не удалось захватить кадр")
        break

    out.write(frame)  # Записываем кадр в файл

    # Отображаем видео в реальном времени (опционально)
    # cv2.imshow('Video Recording', frame)

    # Прерываем запись при нажатии клавиши 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Освобождаем ресурсы
cap.release()
out.release()
cv2.destroyAllWindows()

print("Запись завершена.")
