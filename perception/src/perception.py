import cv2
import torch
import numpy as np

import pathlib
from typing import List
from PIL import Image, ImageDraw

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
    

    def process_thread()