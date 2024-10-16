import cv2
import os

def extract_frames(video_path, output_dir, frame_interval=10):
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Не удалось открыть видеофайл {video_path}")
        return
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    frame_count = 0
    saved_count = 0
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            break 
        
        if frame_count % frame_interval == 0:
            frame_filename = os.path.join(output_dir, f"frame_{saved_count:04d}.jpg")
            cv2.imwrite(frame_filename, frame)
            print(f"Сохранили {frame_filename}")
            saved_count += 1
        
        frame_count += 1

    cap.release()
    print(f"Всего сохранено кадров: {saved_count} из {frame_count}")

video_path = "/home/mfclabber/yandex_camp_software/combined_video.mp4" 
output_dir = "output_frames"  
frame_interval = 5           

extract_frames(video_path, output_dir, frame_interval)
