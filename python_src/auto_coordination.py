import numpy as np
from test_move import RobotDirection
from xr_ultrasonic import Ultrasonic
import time
from path_planning import Graph, shortest_path
from smart_rotate import finish_rotate
import cv2


class Cell:
    '''
    Класс клетки сетки
    '''

    def __init__(self, pos, walls, cell_obj):

        '''
        Инициализирует клетку сетки

        Аргументы:
            pos - координаты [x,y] в сетке
            walls - массив направлений, в которых есть стены
            cell_obj - массив строк - названий объектов внутри клетки
        '''

        self.pos = np.array(pos)
        self.walls = walls
        self.cell_obj = cell_obj
    
    def print_cell(self):

        '''
        Выводит строковое представление клетки
        '''

        ans = [
            "    ",
            " ",self.cell_obj[-1]," ",
            "    "
        ]
        if (0 in self.walls):
            ans[0] = "____"
        if (1 in self.walls):
            ans[3] = "|"
        if (2 in self.walls):
            ans[4] = "____"
        if (3 in self.walls):
            ans[1] = "|"
        
        return ans
    

class Coordinator:

    '''
    Класс координатора внутри графа
    '''

    def __init__(self, robot_pos, robot_dir, base_pos, rg_pos, cube_pos, walls_conf, sonic, go):

        '''
        Инициализирует координатор

        Аргументы:
            robot_pos - позиция робота на сетке в виде [x,y]
            robot_dir - направление робота (число от 0 до 3)
            base_pos - позиция базы
            rg_pos - позиция красно-зеленой кнопки
            cube_pos - позиция ближайшего кубика
            walls_conf - конфигурация внешних стен 
                True (сверху и снизу) / False (стены справа и слева)
            sonic - объект класса Ultrasonic для ориентирования
            go - объект класса RobotDirection для движения
        '''
        
        robot_pos = robot_pos[0]
        robot_pos[1] = 4-robot_pos[1]
        robot_dir = robot_dir
        base_pos = base_pos[0]
        base_pos[1] = 4-base_pos[1]
        rg_pos = rg_pos[0]
        rg_pos[1] = 4-rg_pos[1]
        cube_pos = cube_pos[0]
        cube_pos[1] = 4-cube_pos[1]
        
        

        self.go = go
        self.sonic = sonic

        # Пределы расстояния, на которых может 
        # находиться внутренняя стенка 
        # при ее идентификации ультразвуком

        self.MAX_SONIC_MIDDLE_DIST = 120
        self.MIN_SONIC_MIDDLE_DIST = 60


        # Массив соответствия направлений
        # Перемещениям внутри сетки

        self.directions = [
            np.array( [0, 1] ),     # 0 вверх
            np.array( [1, 0] ),     # 1 вправо
            np.array( [0, -1] ),    # 2 вниз
            np.array( [-1, 0] )     # 3 влево
        ]

        self.robot_dir = robot_dir


        # Создаем и заполняем секту
        
        self.field_map = [[0]*5 for i in range(5)]

        for x in range(5):
            for y in range(5):
                self.field_map[x][y] = Cell([x,y],[],["  "])
        

        # Инициализируем стены

        self.walls_conf = walls_conf[0]
        self.init_inner_walls(walls_conf[1])
        

        ### КОСТЫЛИ (но рабочие)

        # Обозначаем клетки внешнего (tmo от trouble maker out) 
        # и внутреннего (tmi от trouble maker in) квадрата,
        # стоящие при пустотах во внешней стенке,
        # а также инверсированные к ним
        # pass_points и tmi_r соответственно

        if walls_conf[0]:
            self.tmo = [[0,2],[4,2]]
            self.tmi = [[1,2],[3,2]]
            self.pass_points = [[2,0],[2,4]]
            self.tmi_r = [[2,1],[2,3]]
        else:
            self.tmo = [[2,0],[2,4]]
            self.tmi = [[2,1],[2,3]]
            self.pass_points = [[0,2],[4,2]]
            self.tmi_r = [[1,2],[3,2]]


        # Задаем начальную позицию нашего робота
        # и, инверсировав ее, позицию вражеского

        self.robot_pos = np.array(robot_pos)
        self.robot_pos_e = np.array(self.inv_pos(robot_pos))
        self.field_map[robot_pos[0]][robot_pos[1]].cell_obj.append("r1")
        self.field_map[self.robot_pos_e[0]][self.robot_pos_e[1]].cell_obj.append("r2")


        # Задаем начальную позицию нашей базы
        # и, инверсировав ее, позицию вражеской

        self.base_pos = np.array(base_pos)
        self.base_pos_e = self.inv_pos(base_pos)
        self.field_map[base_pos[0]][base_pos[1]].cell_obj.append("b1")
        self.field_map[self.base_pos_e[0]][self.base_pos_e[1]].cell_obj.append("b2")


        # Задаем позицию красно-зеленой кнопки
        # и, инверсировав ее, позицию сине-розовой

        self.rg_pos = np.array(rg_pos)
        self.bm_pos = self.inv_pos(rg_pos)
        self.field_map[rg_pos[0]][rg_pos[1]].cell_obj.append("rg")
        self.field_map[self.bm_pos[0]][self.bm_pos[1]].cell_obj.append("bm")


        # Задаем позицию первого кубика
        # и, инверсировав ее, позицию второго

        self.cube_pos = np.array(cube_pos)
        self.cube_pos_e = self.inv_pos(cube_pos)
        self.field_map[cube_pos[0]][cube_pos[1]].cell_obj.append("c1")
        self.field_map[self.cube_pos_e[0]][self.cube_pos_e[1]].cell_obj.append("c2")

        
        # Задаем следующую точку как нынешнее положение + направление
        self.next_point = self.robot_pos+self.directions[self.robot_dir]


    def rotate_in_graph(self,direction):

        '''
        Поворачивает робота в графе
        
        Аргументы:
            direction - направление поворота
                1 для поворота вправо
                -1 для поворота влево
                (формально, можно выставить числа больше, тогда
                робот провернется в графе соответствующее число раз)
        '''

        self.robot_dir = (self.robot_dir+direction)%4
        self.next_point = self.robot_pos+self.directions[self.robot_dir]
    


    def first_moves(self):

        '''
        Начальный подъезд к стенке
        '''

        self.come_to_wall(1)
    


    def return_to_wall(self):
        
        '''
        Вернуться к стенке после забора кубика
        '''

        if (self.cube_pos[0] == 0) or (self.cube_pos[0] == 4):
            cap = cv2.VideoCapture(0)
            self.rotate(-1)
            finish_rotate(self.go,cap)
            self.come_to_wall(-1)
            cap.release()


    def come_to_wall(self,dir):
        
        '''
        Передвижение в удобную точку на карте
        '''

        self.go.forward_with_angle(50,0)
        time.sleep(1)
        self.go.stop()
        time.sleep(0.3)

        self.go.forward_with_angle(0,dir*90)
        time.sleep(0.5)
        self.go.stop()
        time.sleep(0.3)

        self.go.follow_till_wall(20,'r',self.sonic)
        self.go.stop()
        time.sleep(0.3)

        self.go.forward_with_angle(0,-dir*90)
        time.sleep(0.5)
        self.go.stop()
        time.sleep(0.3)

        self.move_in_graph()


    def move_in_graph(self):
        
        '''
        Продвигает робота в графе вперед по направлению

        Если есть возможность определить конфигурацию 
        внутренних стен ультразвуком - определяет её
        '''
        
        # Проверка возможности продвижения (чтобы не выйти за пределы сетки)
        if self.can_move():
            
            # Проверка возможности определения конфигурации внутренних стен
            # if [self.next_point[0],self.next_point[1]] in self.tmo and not ([self.robot_pos[0],self.robot_pos[1]] in self.tmi):
            #     self.init_inner_walls(self.check_sonic() ^ self.walls_conf)
            
            # Убираем из нынешней клетки робота
            self.field_map[self.robot_pos[0]][self.robot_pos[1]].cell_obj.pop(
                self.field_map[self.robot_pos[0]][self.robot_pos[1]].cell_obj.index('r1'))
            

            ### ЕЩЕ КОСТЫЛИ (фактически, нужны, чтобы не менять структуру сетки)

            # Проверка необходимости продвижения по графу трижды
            # (робот продвигается вдоль стенки;
            # если стенка длинная, то продвинуться надо 3 раза)

            if [self.next_point[0], self.next_point[1]] in self.pass_points:
                self.robot_pos += self.directions[self.robot_dir]
                self.robot_pos += self.directions[self.robot_dir]
            
            # Передвижение робота
            self.robot_pos += self.directions[self.robot_dir]
            self.field_map[self.robot_pos[0]][self.robot_pos[1]].cell_obj.append("r1")
            self.next_point = self.robot_pos+self.directions[self.robot_dir]
            
            # При изменении положения робота отрисовываем новый вид сетки
            self.show_field()
    

    def move_forward(self):

        '''
        Продвижение робота вперед
        '''
        
        if self.can_move():
            side = 'none'

            # Если стоим во внутреннем квадрате и направлены в клетку,
            # прилежащую к внешней стене - нужно двигаться, ориентируясь в противоположную сторону

            if [self.next_point[0], self.next_point[1]] in self.tmi_r:
                for i in self.field_map[self.robot_pos[0]][self.robot_pos[1]].walls:
                    if (i-self.robot_dir)%4 == 1:
                        side = "l"
                    elif (i-self.robot_dir)%4 == 3:
                        side = "r"
                self.go.follow_till_wall(40,side,self.sonic)

            else:

                # Проверяем, можем ли сейчас двигаться вдоль стены
                # (если можем, то вдоль какой)

                for i in self.field_map[self.robot_pos[0]][self.robot_pos[1]].walls:
                    if (i-self.robot_dir)%4 == 1:
                        side = "r"
                    elif (i-self.robot_dir)%4 == 3:
                        side = "l"


                # Если сейчас стены рядом нет - проверяем, до какой стены 
                # можем доехать, двигаясь по прямой

                if side == 'none':
                    side_next = 'none'
                    for i in self.field_map[self.next_point[0]][self.next_point[1]].walls:
                        if (i-self.robot_dir)%4 == 1:
                            side_next = "r"
                        elif (i-self.robot_dir)%4 == 3:
                            side_next = "l"
                    self.go.follow_till_wall(40,side_next,self.sonic)
                else:
                    self.go.follow_wall(18,side,self.sonic)
            
            
            ### КОСТЫЛЬ (проезжаем еще немного +- вглубь клетки)
            self.go.stop()
            time.sleep(0.3)
            self.go.forward_with_angle(45,0)
            time.sleep(0.7)
            self.go.stop()
            time.sleep(0.3)

            # Продвигаем робота в графе
            self.move_in_graph()
    

    def rotate(self,dir):
        self.go.forward_with_angle(0,dir*90)
        time.sleep(0.5)
        self.go.stop()
        self.rotate_in_graph(dir)

    
    # def check_sonic(self):

    #     '''
    #     Проверка ультразвуком наличия стенки в удалении (для определения внутренних стен)
    #     '''

    #     for i in self.field_map[self.robot_pos[0]][self.robot_pos[1]].walls:
    #         print((i-self.robot_dir)%4)
    #         print(i)
    #         if (i-self.robot_dir)%4 == 1:
    #             self.sonic.rotate_sensor_r()
    #             break
    #     else:
    #         self.sonic.rotate_sensor_l()
    #     time.sleep(1)

    #     dist = self.sonic.get_distance()
    #     print("SONIC:",dist)
    #     if (dist < self.MAX_SONIC_MIDDLE_DIST) and (dist > self.MIN_SONIC_MIDDLE_DIST):
    #         return 1
    #     return 0

    def can_move(self):
        
        '''
        Проверка возможности продвижения по графу
        (нет ли стены перед нами и не закончилась ли сетка)
        '''

        min_check = min(self.robot_pos+self.directions[self.robot_dir]) > -1
        max_check = max(self.robot_pos+self.directions[self.robot_dir]) < 5
        return not(self.robot_dir in self.field_map[self.robot_pos[0]][self.robot_pos[1]].walls) and min_check and max_check


    def inv_pos(self,pos):

        '''
        Возвращает позицию, противоположную pos
        '''

        return np.array([abs(4-pos[0]),abs(4-pos[1])])


    def init_inner_walls(self,walls_conf):

        '''
        Инициализация внутренних стен внутри графа
        '''


        # Переопределяем стены
        # (чтобы очистить внутренние стены;
        # так, если в прошлый раз 
        # мы определили внутренние стены 
        # неправильно - мы сможем их переопределить)

        self.init_out_walls()


        # Добавляем внутренние стены

        if walls_conf:
            self.field_map[2][1].walls.append(0)
            self.field_map[2][2].walls.append(0)
            self.field_map[2][3].walls.append(2)
            self.field_map[2][2].walls.append(2)
        else:
            self.field_map[1][2].walls.append(1)
            self.field_map[2][2].walls.append(1)
            self.field_map[3][2].walls.append(3)
            self.field_map[2][2].walls.append(3)

    def init_out_walls(self):
        
        '''
        Инициализация внешних стен
        '''

        # Очищаем стены

        for x in range(5):
            for y in range (5):
                self.field_map[x][y].walls = []


        # Добавляем углы

        self.field_map[1][0].walls.append(0)
        self.field_map[0][1].walls.append(1)

        self.field_map[0][3].walls.append(1)
        self.field_map[1][4].walls.append(2)

        self.field_map[3][4].walls.append(2)
        self.field_map[4][3].walls.append(3)

        self.field_map[4][1].walls.append(3)
        self.field_map[3][0].walls.append(0)

        
        self.field_map[1][1].walls.append(2)
        self.field_map[1][1].walls.append(3)

        self.field_map[1][3].walls.append(3)
        self.field_map[1][3].walls.append(0)

        self.field_map[3][3].walls.append(0)
        self.field_map[3][3].walls.append(1)

        self.field_map[3][1].walls.append(1)
        self.field_map[3][1].walls.append(2)

        # Добавляем стены внешнего квадрата

        if self.walls_conf:
            self.field_map[2][4].walls.append(2)
            self.field_map[2][3].walls.append(0)
            self.field_map[2][1].walls.append(2)
            self.field_map[2][0].walls.append(0)
        else:
            self.field_map[0][2].walls.append(1)
            self.field_map[1][2].walls.append(3)
            self.field_map[3][2].walls.append(1)
            self.field_map[4][2].walls.append(3)
    
    def graph_repr(self):

        '''
        Метод, возвращающий текущее состояние сетки в виде графа
        '''

        graph = Graph()

        for x in range(5):
            for y in range(5):
                if (y != 2) or (x != 2):
                    if not (1 in self.field_map[x][y].walls) and x<4:
                        graph.add_edge(x*5+y,(x+1)*5+y)
                    if not (0 in self.field_map[x][y].walls) and y<4:
                        graph.add_edge(x*5+y,x*5+y+1)
        for edge in graph.edges:
            print(edge)
        return graph

    def calculate_path(self,point):

        '''
        Рассчет кратчайшего пути
        '''

        point_1 = int(self.robot_pos[0]*5 + self.robot_pos[1])
        point_2 = int(point[0]*5 + point[1])
        
        path_points = [np.array([i//5,i%5]) for i in shortest_path(self.graph_repr(), point_1, point_2)]
        print(path_points)
        path = []
        dir = self.robot_dir

        for i in range(len(path_points)-1):

            dx = path_points[i+1][0]-path_points[i][0]
            dy = path_points[i+1][1]-path_points[i][1]

            if dx == 1:  # Движение на восток
                desired_direction = 1
            elif dx == -1:  # Движение на запад
                desired_direction = 3
            elif dy == 1:  # Движение на север
                desired_direction = 0
            elif dy == -1:  # Движение на юг
                desired_direction = 2
            
            comm = (desired_direction - dir) % 4
            dir = desired_direction
            path.append(comm)
            if comm != 0:
                path.append(0)
        
        print(path)

        return path

    def execute_path(self,path):
        
        '''
        Выполняет заданный путь
        '''
        
        cap = cv2.VideoCapture(0)

        for comm in path:
            if comm == 0:
                finish_rotate(self.go,cap)
                self.move_forward()
            elif comm == 1:
                self.rotate(1)
            elif comm == 2:
                self.rotate(1)
                self.rotate(1)
            elif comm == 3:
                self.rotate(-1)
        cap.release()
    

    def go_to(self,point):

        '''
        Поехать в координату
        '''

        path = self.calculate_path(point)
        self.execute_path(path)
    

    
    def go_to_cube(self):

        '''
        Подъезд к кубу
        '''

        path1 = self.calculate_path(self.cube_pos)
        path2 = self.calculate_path(self.cube_pos_e)

        path = path1 if len(path2)>len(path1) else path2

        if (self.cube_pos[0] == 0) or (self.cube_pos[0] == 4):
            self.execute_path(path)
            if (self.robot_dir == 0) or (self.robot_dir == 2):
                self.rotate(-1)
            
        else:
            path.pop()

            self.execute_path(path)
            self.move_in_graph()
        


    def go_to_base(self):

        '''
        Подъезд к базе
        '''

        path = self.calculate_path(self.base_pos)
        path.pop()
        self.execute_path(path)
        self.move_in_graph()


    def show_field(self):

        '''
        Вывод текущего состояния сетки в консоль
        '''

        for y in range(4,-1,-1):
            l1 = "      "
            l2 = "      "
            l3 = "      "
            for x in range(5):
                cell_lns = self.field_map[x][y].print_cell()
                l1+=cell_lns[0]
                l2+=cell_lns[1]+cell_lns[2]+cell_lns[3]
                l3+=cell_lns[4]
            print(l1)
            print(l2)
            print(l3)
        print("dir = ",self.robot_dir)
        print("pos = ",self.robot_pos)
        print("next_pos = ",self.next_point)


# ult = Ultrasonic()
# go = RobotDirection()

# coordinator = Coordinator([[0,4]], 0, [[2,4]], [[0,2]], [[4,4]], [False,False], ult,go)
# coordinator.first_moves()
# coordinator.return_to_wall()

# while True:
#     x,y = map(int,input().split())
#     coordinator.go_to(np.array([x,y]))

# cap = cv2.VideoCapture(0)
# while True:
#     coordinator.show_field()
#     comm = input()
#     if comm == "0":
#         coordinator.move_forward()
#     elif comm == "1":
#         coordinator.rotate(1)
#     elif comm == "-1":
#         coordinator.rotate(-1)
#     elif comm == 'q':
#         break
#     finish_rotate(go,cap)
# cap.release()