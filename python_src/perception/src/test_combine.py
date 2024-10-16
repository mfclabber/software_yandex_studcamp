import cv2
import os

def combine_videos(video_paths, output_combined_video):
    # Получаем параметры первого видео
    cap = cv2.VideoCapture(video_paths[0])
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    # Создаем VideoWriter для объединенного видео
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Кодек для сохранения видео
    out = cv2.VideoWriter(output_combined_video, fourcc, fps, (width, height))

    # Читаем и записываем кадры из каждого видео
    for video_path in video_paths:
        cap = cv2.VideoCapture(video_path)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)
        cap.release()

    out.release()
    print(f"Видео сохранено как {output_combined_video}")

def save_frames_from_video(video_path, output_dir, frame_interval=5):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    saved_frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            frame_filename = os.path.join(output_dir, f"frame_{saved_frame_count:04d}.jpg")
            cv2.imwrite(frame_filename, frame)
            saved_frame_count += 1

        frame_count += 1

    cap.release()
    print(f"Сохранено {saved_frame_count} кадров в папку {output_dir}")

if __name__ == "__main__":
    # Пути к видеофайлам
    video_paths = ["/home/mfclabber/yandex_camp_software/data/videos/IMG_0419.MOV", "/home/mfclabber/yandex_camp_software/data/videos/IMG_0422.MOV"]  # Замените на свои пути
    output_combined_video = "combined_video.mp4"

    # Шаг 1: Объединение видео
    combine_videos(video_paths, output_combined_video)

    # Шаг 2: Сохранение фреймов из объединенного видео
    output_frames_dir = "frames_output"
    save_frames_from_video(output_combined_video, output_frames_dir, frame_interval=30)
