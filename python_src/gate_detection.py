from collections import deque
import cv2
import numpy as np
from skimage.draw import line


def gate_detection(img, show_flag = False):
    def edge_dilated(img):
        # num номер варианта обработки изображеняи

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Определяем диапазон для чёрного цвета
        # Настройте эти значения в зависимости от освещения
        lower_black = np.array([0, 0, 100])
        upper_black = np.array([255, 255, 255])

        # Создаём маску для чёрных областей (стен и границ)
        mask = cv2.bitwise_not(cv2.inRange(hsv, lower_black, upper_black))
        # Используем метод Canny для обнаружения границ
        blurred = cv2.GaussianBlur(mask, (5, 5), 0)
        # th3 = cv2.bitwise_not(cv2.adaptiveThreshold(blurred,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,cv.THRESH_BINARY,11,2))

        
        _,thresh = cv2.threshold(blurred,10,255,cv2.THRESH_BINARY)
        kernel = np.ones((6,6), np.uint8)
        # # Используем дилатацию для соединения разорванных линий стен лабиринта
        # edges = cv.Canny(dilated, 50, 150)

        
        
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

        kernel1 = np.ones((3,3), np.uint8)
        
        morph_close = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel1)
        dilated = cv2.dilate(morph_close, kernel, iterations=1)
        
        kernel2 = np.ones((3,3), np.uint8)
        morph_close = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, kernel2)


        return dilated

    def find_next_0(xy,dir):
        directions={"up":np.array([0,-1]), "down":np.array([0,1]),"left":np.array([-1,0]),"right":np.array([1,0])}
        # directions={"right":np.array([0,1]), "left":np.array([0,-1]),"down":np.array([-1,0]),"up":np.array([1,0])}
        xy = xy + directions[dir]*10
        while binary_image_outer[xy[1],xy[0]] == 0:
            # print(xy)
            xy += directions[dir]
        return xy[0],xy[1]

    def check_box(xy1,xy2,dir):
        directions={"up":np.array([0,-1]), "down":np.array([0,1]),"left":np.array([-1,0]),"right":np.array([1,0])}
        # xy2 = xy2 + directions[dir]*15
        count_rect = 0
        depth = 30
        for i in range(depth):
            xy2_ = xy2 + directions[dir]*i
            xy1_ = xy1 + directions[dir]*i
            # print(xy1_,xy2_)
            line_list = list(line(xy1_[0], xy1_[1], xy2_[0], xy2_[1]))
            for j in range(len(line_list[0])):
                if binary_image_outer[line_list[1][j],line_list[0][j]] == 255:
                    count_rect += 1

        return count_rect

    def is_valid(grid, visited, x, y):
        rows, cols = len(grid), len(grid[0])
        return 0 <= x < rows and 0 <= y < cols and grid[x][y] == 0 and not visited[x][y]

    def bfs_farthest_point(grid, start_x, start_y, dir):
        # Размеры массива
        rows, cols = len(grid), len(grid[0])
        
        if dir == "lb":
            directions = [(1, 0), (0, -1)]
        elif dir == "rb":
            directions = [(1, 0), (0, 1)]
        elif dir == "lt":
            directions = [(-1, 0), (0, -1)]
        elif dir == "rt":
            directions = [(-1, 0), (0, 1)]
        
        # Массив для отслеживания посещенных клеток
        visited = [[False for _ in range(cols)] for _ in range(rows)]
        
        # Очередь для BFS, начинаем с точки (x, y)
        queue = deque([(start_x, start_y)])
        visited[start_x][start_y] = True
        
        # Переменная для хранения самой удаленной точки
        farthest_point = (start_x, start_y)
        
        # Выполняем BFS
        while queue:
            x, y = queue.popleft()
            
            # Обновляем самую удаленную точку
            farthest_point = (x, y)
            
            # Проверяем всех соседей
            for dx, dy in directions:
                new_x, new_y = x + dx, y + dy
                
                if is_valid(grid, visited, new_x, new_y):
                    visited[new_x][new_y] = True
                    queue.append((new_x, new_y))
        
        # Возвращаем самую удаленную точку
        return farthest_point[::-1]



    # Загрузка изображения в градациях серого
    image_col = img
    image_gray = cv2.cvtColor(image_col, cv2.COLOR_BGR2GRAY)
    _, binary_image_inner = cv2.threshold(image_gray, 127, 255, cv2.THRESH_BINARY)
    binary_image_outer = edge_dilated(image_col)

    # kernel = np.ones((5, 5), np.uint8)
    # Применение дилатации
    # dilated_image = cv2.dilate(binary_image, kernel, iterations=1)

    # cv2.imshow('Binary Image', binary_image)

    grid = binary_image_inner
    # print(binary_image_inner.shape)
    start_y, start_x = binary_image_inner.shape[1]//2, binary_image_inner.shape[0]//2  # Стартовая точка

    farthest_points_lb = np.array(bfs_farthest_point(grid, start_x, start_y, "lb"))
    farthest_points_rb = np.array(bfs_farthest_point(grid, start_x, start_y, "rb"))
    farthest_points_lt = np.array(bfs_farthest_point(grid, start_x, start_y, "lt"))
    farthest_points_rt = np.array(bfs_farthest_point(grid, start_x, start_y, "rt"))
    # print(f"Наиболее удаленные точки:")
    # print(f"Вверх-влево: {farthest_points_lt}")
    # print(f"Вверх-вправо: {farthest_points_rt}")
    # print(f"Вниз-влево: {farthest_points_lb}")
    # print(f"Вниз-вправо: {farthest_points_rb}")

    rgb_image = cv2.cvtColor(binary_image_inner, cv2.COLOR_GRAY2RGB)
    # cv2.line(rgb_image,farthest_points_lb,farthest_points_rb,(255,0,0),1)
    # cv2.line(rgb_image,farthest_points_lt,farthest_points_rt,(255,0,0),1)
    # cv2.line(rgb_image,farthest_points_rb,farthest_points_rt,(255,0,0),1)
    # cv2.line(rgb_image,farthest_points_lt,farthest_points_lb,(255,0,0),1)

    count_lb_rb, count_lt_rt, count_rb_rt, count_lb_lt = 0,0,0,0

    # being start and end two points (x1,y1), (x2,y2)
    depth = 5
    for i in range(depth):
        lb_rb = list(line(farthest_points_lb[0], farthest_points_lb[1]-i, farthest_points_rb[0],farthest_points_rb[1]-i))
        # cv2.line(rgb_image,[farthest_points_lb[0], farthest_points_lb[1]-i], [farthest_points_rb[0],farthest_points_rb[1]-i], (255,0,0), 1)
        for i in range(len(lb_rb[0])):
            if binary_image_inner[lb_rb[1][i],lb_rb[0][i]] == 0:
                count_lb_rb += 1

    for i in range(depth):
        lt_rt = list(line(farthest_points_lt[0], farthest_points_lt[1]+i, farthest_points_rt[0], farthest_points_rt[1]+i))
        # cv2.line(rgb_image,[farthest_points_lt[0], farthest_points_lt[1]+i], [farthest_points_rt[0], farthest_points_rt[1]+i], (255,0,0), 1)
        for i in range(len(lt_rt[0])):
            if binary_image_inner[lt_rt[1][i],lt_rt[0][i]] == 0:
                count_lt_rt += 1

    for i in range(depth):
        rb_rt = list(line(farthest_points_rb[0]-i, farthest_points_rb[1], farthest_points_rt[0]-i, farthest_points_rt[1]))
        # cv2.line(rgb_image,[farthest_points_rb[0]-i, farthest_points_rb[1]], [farthest_points_rt[0]-i, farthest_points_rt[1]], (255,0,0), 1)
        for i in range(len(rb_rt[0])):
            if binary_image_inner[rb_rt[1][i],rb_rt[0][i]] == 0:
                count_rb_rt += 1

    for i in range(depth):
        lb_lt = list(line(farthest_points_lb[0]+i, farthest_points_lb[1], farthest_points_lt[0]+i, farthest_points_lt[1]))
        # cv2.line(rgb_image,[farthest_points_lb[0]+i, farthest_points_lb[1]], [farthest_points_lt[0]+i, farthest_points_lt[1]], (255,0,0), 1)
        for i in range(len(lb_lt[0])):
            if binary_image_inner[lb_lt[1][i],lb_lt[0][i]] == 0:
                count_lb_lt += 1


    # print(count_lb_rb, count_lt_rt, count_rb_rt, count_lb_lt)

    #  = createLineIterator(farthest_points_lt,farthest_points_rt, binary_image)
    #  = createLineIterator(farthest_points_rb,farthest_points_rt, binary_image)
    #  = createLineIterator(farthest_points_lb,farthest_points_lt, binary_image)

    external_wall = None
    internal_wall = None

    print("Внутренние:")
    if count_lt_rt+count_lb_rb > count_lb_lt + count_rb_rt:
        print("сверху и снизу")
        internal_wall = True
    else:
        print("слева и справа")
        internal_wall = False

    b_line_left = find_next_0(farthest_points_lb,"down")
    l_line_bottom = find_next_0(farthest_points_lb,"left")
    b_line_right = find_next_0(farthest_points_rb,"down")
    r_line_bottom = find_next_0(farthest_points_rb,"right")
    t_line_right = find_next_0(farthest_points_rt,"up")
    r_line_top = find_next_0(farthest_points_rt,"right")
    t_line_left = find_next_0(farthest_points_lt,"up")
    l_line_top = find_next_0(farthest_points_lt,"left")
    

    down = check_box(b_line_left,b_line_right, "down")
    up = check_box(t_line_left,t_line_right, "up")
    left = check_box(l_line_top,l_line_bottom, "left")
    right = check_box(r_line_top,r_line_bottom, "right")

    print("Наружние:")
    if up + down > left + right:
        print("Сверху и снизу")
        external_wall = True
    else:
        print("Слева и справа")
        external_wall = False

    if show_flag:
        cv2.imshow("Binary", binary_image_outer)
        cv2.imshow("Binary_2", binary_image_inner)
        cv2.imshow("RGB", rgb_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        cv2.line(rgb_image,[b_line_left[0], b_line_left[1]], [b_line_right[0], b_line_right[1]], (255,0,0), 1)
        cv2.line(rgb_image,[l_line_bottom[0], l_line_bottom[1]], [l_line_top[0], l_line_top[1]], (255,0,0), 1)
        cv2.line(rgb_image,[t_line_left[0], t_line_left[1]], [t_line_right[0], t_line_right[1]], (255,0,0), 1)
        cv2.line(rgb_image,[r_line_bottom[0], r_line_bottom[1]], [r_line_top[0], r_line_top[1]], (255,0,0), 1)

    return external_wall, internal_wall