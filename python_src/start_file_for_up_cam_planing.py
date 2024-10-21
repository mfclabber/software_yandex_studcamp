from Setka import setka
from model_test_up_cam import YOLO_UP_CAM
from gate_detection import gate_detection
import cv2 as cv



ID2LABEL_UPCAM = dict([
            (0, "G_O button"),
            (1, "P_B button"), 
            (2, "cube"),
            (3, "green base"),
            (4, "red base"),
            (5, "robot with green"),
            (6, "robot with red")
        ])


# rtsp_url = "/home/sruwer/python_opencv_venv/jupyter-venv/output_left_data_another_combination_1.avi"
rtsp_url = "rtsp://Admin:rtf123@192.168.2.250:554/1/1"
def UP_CAM(color = 'red'):
    frame, list_of_points, annotated_frame = YOLO_UP_CAM(rtsp_url)

    print(list_of_points)


    cv.imshow('YOLO Detected Frame', annotated_frame)
    cv.waitKey(0)
    cv.destroyAllWindows()

    """
        robot_pos - позиция робота на сетке в виде [x,y]
        robot_dir - направление робота (число от 0 до 3)
        base_pos - позиция базы
        rg_pos - позиция красно-зеленой кнопки
        cube_pos - позиция ближайшего кубика
        walls_conf - конфигурация внешних стен 
            True (сверху и снизу) / False (стены справа и слева)
            [внешние_стенки, внутренние_стенки]
    """
    grid_matrix, list_of_points_with_pos = setka(list_of_points, frame)

    #print(grid_matrix)
    """
        list_of_points_with_pos
        [x_centr, y_centr, class, x_pos, y_pos]
    """
    print(list_of_points_with_pos)

    red_robot_pos = [pos[3:] for pos in list_of_points_with_pos if pos[2] == 6]
    green_robot_pos = [pos[3:] for pos in list_of_points_with_pos if pos[2] == 5]

    green_base_pos = [pos[3:] for pos in list_of_points_with_pos if pos[2] == 3]
    red_base_pos = [pos[3:] for pos in list_of_points_with_pos if pos[2] == 4]

    cube_pos = [pos[3:] for pos in list_of_points_with_pos if pos[2] == 2]

    rg_pos = [pos[3:] for pos in list_of_points_with_pos if pos[2] == 0]

    pb_pos = [pos[3:] for pos in list_of_points_with_pos if pos[2] == 1]

    # задаём как-то цвет робота

    robot_pos = None
    base_pos = None

    if color == 'green':
        robot_pos = green_robot_pos
        base_pos = green_base_pos
    elif color == 'red':
        robot_pos = red_robot_pos
        base_pos = red_base_pos

    external_wall, internal_wall = gate_detection(frame)

    walls_conf = [external_wall, internal_wall]

    """
    robot_dir
    0 - up
    1 - right
    2 - down
    3 - left
   """
    robot_dir = None
    if robot_pos == [0,4]:
        robot_dir = 0
    elif robot_dir == [4,0]:
        robot_dir = 2

    # параметры котоыре надо передать в класс Тимура 
    return(robot_pos, base_pos, robot_dir ,rg_pos, cube_pos, walls_conf)

UP_CAM('green')