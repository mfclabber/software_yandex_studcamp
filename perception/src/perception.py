import cv2
import torch
import numpy as np

import time
import pathlib
from typing import List
from PIL import Image, ImageDraw

import threading
import queue

from ultralytics import YOLO



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


class Perception():
    def __init__(self, 
                 path2weights: pathlib.Path,
                 port_camera: str="/dev/video2"):
        
        self.camera_matrix = np.array([[446.60079798, 0., 341.79583523],
                                [0., 446.7382697, 226.97034584],
                                [0., 0., 1.]], dtype=np.float32)
            
        self.dist_coeffs = np.array([-0.19424606, -0.15660945, -0.00413803, -0.00207618,  0.18147172])

        width = 0.05
        height = 0.05

        self.object_points = np.array([
            [-width / 2, -height / 2, 0],
            [width / 2, -height / 2, 0],
            [width / 2, height / 2, 0],
            [-width / 2, height / 2, 0] 
        ], dtype=np.float32)

        self.model = YOLOv8n(path2weights)
        self.confidence = 50

        self.PORT_CAMERA = port_camera

        self.data_perception_queue = queue.Queue()


    @staticmethod
    def calculate_center(bbox: np.array):
        x_min, y_min, x_max, y_max = bbox
        x_center = (x_min + x_max) / 2
        y_center = (y_min + y_max) / 2
        return np.array([x_center, y_center], dtype=np.float32)


    @staticmethod
    def get_bbox_corners(bbox: np.array):
        x_min, y_min, x_max, y_max = bbox
        corners_2d = np.array([
            [x_min, y_min],  # левый нижний угол
            [x_max, y_min],  # правый нижний угол
            [x_max, y_max],  # правый верхний угол
            [x_min, y_max]   # левый верхний угол
        ], dtype=np.float32)
        return corners_2d
    

    @staticmethod
    def solve_pnp_for_bbox(self,bbox_2d, object_points_3d, camera_matrix, dist_coeffs):
        image_points = np.array([
            [bbox_2d[0], bbox_2d[1]],  # верхний левый угол
            [bbox_2d[2], bbox_2d[1]],  # верхний правый угол
            [bbox_2d[2], bbox_2d[3]],  # нижний правый угол
            [bbox_2d[0], bbox_2d[3]]   # нижний левый угол
        ], dtype=np.float32)

        success, rotation_vector, translation_vector = cv2.solvePnP(object_points_3d, image_points, camera_matrix, dist_coeffs)

        if success:
            return rotation_vector, translation_vector
        else:
            print("PnP не удалось выполнить")
            return None, None
        

    @staticmethod    
    def show_image(image: np.array, 
                   bboxes_: torch.Tensor, 
                   labels: torch.Tensor=None, 
                   scores: torch.Tensor=None,
                   distances: np.ndarray=None) -> np.ndarray:
    
        COLORS = dict([
            ("red_cube", (255, 0, 0)),
            ("red_button", (255, 0, 0)),
            ("blue_button", (0, 0, 255)),
            ("green_button", (0, 255, 0)),
            ("button_box", (255, 255, 255))
        ])

        ID2LABEL = dict([
            (2, "blue_button"),
            (0, "red_cube"), 
            (3, "green_button"),
            (1, "red_button")
        ])

        image = Image.fromarray(image)
            
        for i in range(len(bboxes_)):
            bboxes = bboxes_[i].flatten()
            draw = ImageDraw.Draw(image)
        
            draw.rectangle(bboxes.numpy(), outline = COLORS[ID2LABEL[int(labels[i])]], width=2)

            if scores != None:
                draw.text((bboxes[0], bboxes[1]-28), 
                            f"{ID2LABEL[int(labels[i])]}   {scores[i]:.2f}\ndistance {distances[i]:.2f}", 
                                COLORS[ID2LABEL[int(labels[i])]])
        return np.array(image)
    
    
    def process(self, image: np.ndarray):
        bboxes, labels, scores = self.model.predict(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), 
                                                    confidence=self.confidence)
        positions_in_world = list()
        distances = list()

        for bbox, score, label in zip(bboxes, scores, labels):
            
            corners_2d = self.get_bbox_corners(bbox)

            success, rvec, tvec = cv2.solvePnP(self.object_points, 
                                               corners_2d, 
                                               self.camera_matrix, 
                                               self.dist_coeffs)
            
            positions_in_world.append(cv2.Rodrigues(rvec)[0] @ tvec)
            distances.append(np.linalg.norm(tvec))

        image = self.show_image(image, bboxes, labels, scores, distances)

        target = dict([
            ("bboxes", bboxes),
            ("labels", labels),
            ("scores", scores)
        ])

        return image, target, positions_in_world, distances
    

    def process_video(self, port_camera: str="/dev/video2"):
        cap = cv2.VideoCapture(port_camera)

        if not cap.isOpened():
            print("Не удалось открыть камеру")
            exit()

        frame_count = 0
        fps_count = 0
        start_time = time.time()
        fps = 0 
        print("YOLOv8 RUN!!!")
        while True:
            ret, frame = cap.read()

            # CLAHE
            # lab_img = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)

            # # Применение CLAHE к каналу L (Lightness - Яркость)
            # clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
            # lab_img[:, :, 0] = clahe.apply(lab_img[:, :, 0])

            # # Преобразование обратно в BGR
            # frame = cv2.cvtColor(lab_img, cv2.COLOR_LAB2BGR)


                        # Преобразование в цветовую модель YUV
            # yuv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)

            # # Выравнивание гистограммы только по яркостному каналу (Y)
            # yuv_img[:, :, 0] = cv2.equalizeHist(yuv_img[:, :, 0])

            # # Преобразование обратно в BGR
            # frame= cv2.cvtColor(yuv_img, cv2.COLOR_YUV2BGR)


            channels = cv2.split(frame)

            equalized_channels = []
            for channel in channels:
                equalized_channels.append(cv2.equalizeHist(channel))

            frame = cv2.merge(equalized_channels)
            lab_img = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)

            lab_img[:, :, 1] = cv2.add(lab_img[:, :, 1], 5)
            frame = cv2.cvtColor(lab_img, cv2.COLOR_LAB2BGR)


            # height, width = frame.shape[:2]
            # mask = np.zeros((height, width), dtype=np.float32)

            # # Верхняя часть затемнена, нижняя - без изменений (градиентная маска)
            # for i in range(height):
            #     mask[i, :] = i / height

            # # Преобразование изображения в HSV для работы с яркостью
            # hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # # Применение маски к каналу яркости (Value)
            # hsv_image[:, :, 2] = (hsv_image[:, :, 2] * (1 - 0.5 * mask)).astype(np.uint8)

            # # Преобразование обратно в BGR
            # corrected_image = cv2.cvtColor(frame, cv2.COLOR_HSV2BGR)
            

            if not ret:
                print("Не удалось получить кадр")
                break

            frame_count += 1

            if frame_count % 5 == 0:
                image, target, positions_in_world, distances = self.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                
                current_time = time.time()
                fps = fps_count / (current_time - start_time) if current_time > start_time else 0

                # cv2.putText(image, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                # cv2.imshow('YOLOv8 Detection', cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

                fps_count = 0
                start_time = current_time

                self.data_perception_queue.put((image, target, positions_in_world, distances))
                print("Данные отправлены в очередь")
                time.sleep(0.01)

            fps_count += 1 

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        # cv2.destroyAllWindows()

    
    def process_thread(self, port_camera: str="/dev/video2"):
        yolo_thread = threading.Thread(target=self.process_video, args=(port_camera, ))
        yolo_thread.start()

        return yolo_thread


    def get_data(self, yolo_thread: threading.Thread):

        while yolo_thread.is_alive() or not self.data_perception_queue.empty():
            if not self.data_perception_queue.empty():
                image, target, positions_in_world, distances = self.data_perception_queue.get()
                print(target)
            else:
                time.sleep(0.1)
        print("Поток завершен, данные больше не поступают")
