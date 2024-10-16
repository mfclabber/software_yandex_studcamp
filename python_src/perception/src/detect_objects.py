import cv2
import torch
import pathlib

import numpy as np
from ultralytics import YOLO
from PIL import Image, ImageDraw

from typing import List


class YOLOv8n(torch.nn.Module):
    def __init__(self, path2weights: pathlib.Path, num_classes: int=4) -> None:
        super().__init__()

        self.model = YOLO(str(path2weights))

    def predict(self, X: np.ndarray, confidence=50) -> List[torch.Tensor]:

        results = self.model.predict(X, conf=confidence/100, verbose=False)
        bboxes = results[0].boxes.data[:, :4]
        labels = results[0].boxes.cls
        scores = results[0].boxes.conf
            
        return bboxes.detach().cpu(), labels.detach().cpu(), scores.detach().cpu()
    

def calculate_pnp(bboxes, object_3d_points, camera_matrix, dist_coeffs):
    # Преобразуем координаты граничной рамки в центры
    object_2d_points = np.array([
        [(bboxes[0, 0] + bboxes[0, 2]) / 2, (bboxes[0, 1] + bboxes[0, 3]) / 2],  # Центр первой рамки
        [(bboxes[1, 0] + bboxes[1, 2]) / 2, (bboxes[1, 1] + bboxes[1, 3]) / 2],  # Центр второй рамки
        [(bboxes[2, 0] + bboxes[2, 2]) / 2, (bboxes[2, 1] + bboxes[2, 3]) / 2],  # Центр третьей рамки
        [(bboxes[3, 0] + bboxes[3, 2]) / 2, (bboxes[3, 1] + bboxes[3, 3]) / 2]   # Центр четвертой рамки
    ], dtype=np.float32)

    # Применяем solvePnP для получения позиции и ориентации объекта
    success, rvec, tvec = cv2.solvePnP(object_3d_points, object_2d_points, camera_matrix, dist_coeffs)
    
    if success:
        print(f"Rotation Vector (rvec): {rvec}")
        print(f"Translation Vector (tvec): {tvec}")
        return rvec, tvec
    else:
        print("solvePnP failed!")
        return None, None
    
    
def show_image(image: np.array, 
               bboxes_: torch.Tensor, 
               labels: torch.Tensor=None, 
               scores: torch.Tensor=None,
               type_object: str="red_cube") -> np.ndarray:
    
    COLORS = dict([
        ("red_cube", (255, 0, 0)),
        ("red_button", (255, 0, 0)),
        ("blue_button", (0, 0, 255)),
        ("green_button", (0, 255, 0)),
        ("button_box", (255, 255, 255))
    ])
    
    ID2LABEL = dict([
        (0, "blue_button"),
        (1, "button_box"), 
        (2, "green_button"),
        (3, "red_button")
    ])
    
    image = Image.fromarray(image)
        
    for i in range(len(bboxes_)):
        bboxes = bboxes_[i].flatten()
        draw = ImageDraw.Draw(image)
    
        if type_object == "red_cube":
            draw.rectangle(bboxes.numpy(), outline = COLORS["red_cube"], width=2)
        else:
            draw.rectangle(bboxes.numpy(), outline = COLORS[ID2LABEL[int(labels[i])]], width=2)

        if scores != None:
            if type_object == "red_cube":
                draw.text((bboxes[0], bboxes[1]-10), 
                        f"red_cube   {scores[i]:.2f}", 
                            COLORS["red_cube"])
            else:
                draw.text((bboxes[0], bboxes[1]-10), 
                           f"{ID2LABEL[int(labels[i])]}   {scores[i]:.2f}", 
                              COLORS[ID2LABEL[int(labels[i])]])
    return np.array(image)



if __name__ == "__main__":

    CAMERA_PORT = "dev/video0"

    model = YOLOv8n(path2weights="/home/mfclabber/yandex_camp_software/perception/weights/main_model_weights.pt")

    # image = np.array(Image.open("/home/mfclabber/yandex_camp_software/data/buttons/train/images/IMG_7941_jpeg.rf.515455dada5c47bced0d88ebb4126044.jpg").convert('RGB'))
    # bboxes, labels, scores = model.predict(image, confidence=20)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Не удалось открыть камеру")
        exit()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Не удалось получить кадр")
            break

        bboxes, labels, scores = model.predict(frame, confidence=20)
        annotated_frame = show_image(frame, bboxes, labels, scores, type_object="buttons")

        if len(bboxes) >= 4:
            rvec, tvec = calculate_pnp(bboxes[:4], object_3d_points, camera_matrix, dist_coeffs)
            
            if rvec is not None and tvec is not None:
                print(f"Object Position: {tvec}, Rotation: {rvec}")

        # cv2.imshow('YOLOv8 Detection', annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    # cv2.destroyAllWindows()
