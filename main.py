import pathlib
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import cv2

from perception.src.perception import Perception

if __name__ == "__main__":
    path2model_weight = pathlib.Path("/home/mfclabber/yandex_camp_software/perception/weights/main_model_weights.pt")
    
    perception = Perception(path2weights=path2model_weight)

    # for first testing
    # image, target, positions_in_world, distances = perception.process(image=np.array(Image.open("/home/mfclabber/yandex_camp_software/data/main_train_data/train/images/frame_0232.jpg")))
    # cv2.imwrite("image.png", cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    # perception.process_thread(port_camera="/home/mfclabber/yandex_camp_software/data/videos/IMG_0419.MOV")
    perception.process_thread(port_camera="/dev/video0")

    perception.get_data()