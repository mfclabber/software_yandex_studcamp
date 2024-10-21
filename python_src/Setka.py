import cv2
import numpy as np

def setka(list_of_point, image):
    """
    list_of_point [ [x, y, class] ]
    """

    # Функция для поворота изображения
    def rotate_image(image, angle):
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, matrix, (w, h))
        return rotated

    # Функция для рисования сетки с заданными координатами блоков
    def draw_grid_with_custom_blocks(image, blocks):
        start_points = []
        end_points = []

        # Рисуем сетку на основе заданных блоков
        for (x1, y1, x2, y2) in blocks:
            start_points.append((x1, y1))
            end_points.append((x2, y2))
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

        return image, start_points, end_points

    # Функция для поиска сектора, к которому принадлежит точка
    def find_grid_sector_custom_blocks(blocks, point):
        point_x, point_y = point[:2]
        
        for idx, (x1, y1, x2, y2) in enumerate(blocks):
            if x1 <= point_x <= x2 and y1 <= point_y <= y2:
                return [idx, point[2]]  # Возвращаем индекс блока, к которому принадлежит точка
        return None  # Если точка не принадлежит ни одному блоку

    # Обрезка изображения по оси x в диапазоне 270 до 1520
    #cropped_image = image[:, 270:1520]

    # Поворот изображения на 2 градуса против часовой стрелки
    rotated_image = rotate_image(image, 1)

    # Уменьшение изображения в 2 раза
    small_image = cv2.resize(rotated_image, (rotated_image.shape[1], rotated_image.shape[0]))

    # # Задаем блоки с фиксированными координатами для 5x5 сетки
    #   A   B   C   D   E   F
    # a +---+---+---+---+---+
    #   | 1 | 2 | 3 | 4 | 5 |
    # b +---+---+---+---+---+
    #   | 6 | 7 | 8 | 9 |10 |
    # c +---+---+---+---+---+
    #   |11 |12 |13 |14 |15 |
    # d +---+---+---+---+---+
    #   |16 |17 |18 |19 |20 |
    # e +---+---+---+---+---+
    #   |21 |22 |23 |24 |25 |
    # f +---+---+---+---+---+

    # # Координаты столбцов
    # A = 24; B = 160; C = 250; D = 365; E = 450; F = 580

    # # Координаты строк
    # a = 16; b = 75; c = 170; d = 280; e = 380; f = 430

       # Координаты столбцов
    A = 24*2; B = 160*2; C = 250*2; D = 365*2; E = 450*2; F = 580*2

    # Координаты строк
    a = 16*2; b = 75*2; c = 170*2; d = 280*2; e = 380*2; f = 430*2

    blocks = [
        (A, a, B, b), (B, a, C, b), (C, a, D, b), (D, a, E, b), (E, a, F, b),
        (A, b, B, c), (B, b, C, c), (C, b, D, c), (D, b, E, c), (E, b, F, c),
        (A, c, B, d), (B, c, C, d), (C, c, D, d), (D, c, E, d), (E, c, F, d),
        (A, d, B, e), (B, d, C, e), (C, d, D, e), (D, d, E, e), (E, d, F, e),
        (A, e, B, f), (B, e, C, f), (C, e, D, f), (D, e, E, f), (E, e, F, f)
    ]

    # Рисуем сетку с блоками нестандартных размеров
    grid_image, start_points, end_points = draw_grid_with_custom_blocks(small_image, blocks)

    # Случайная точка, для которой нужно найти сектор
    
    points = []
    list_of_point_with_pos = [_ for _ in list_of_point]
    for i in range(len(list_of_point)):
        # print("point ",list_of_point[i])
        points.append(find_grid_sector_custom_blocks(blocks, list_of_point[i]))
        _x = (points[i][0])%5
        _y = (points[i][0])//5
        list_of_point_with_pos[i].append(_x)
        list_of_point_with_pos[i].append(_y)
        
    print(points)
    
    # Создаём матрицу с количеством блоков
    grid_matrix = np.empty(len(blocks), dtype=object)
    # Отмечаем сектора для точек
    for p in points:
        if p is not None:
            if grid_matrix[p[0]] is None:
                grid_matrix[p[0]] = [p[1]]
            else:
                grid_matrix[p[0]].append(p[1])

    # Выводим изображение с сеткой и точкой
    # cv2.imshow('Final Image with Grid and Random Points', grid_image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # Вывод матрицы с отмеченным сектором
    # print("Сетка с отмеченными секторами:")
    grid_matrix = np.array(grid_matrix).reshape((5,5))
    return grid_matrix, list_of_point_with_pos
