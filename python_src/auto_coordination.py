
import numpy as np
from test_move import RobotDirection
from xr_ultrasonic import Ultrasonic
import time

class Cell:
    '''
    Класс клетки графа
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

        self.walls_conf = walls_conf
        self.init_out_walls()
        

        ### КОСТЫЛИ (но рабочие)

        # Обозначаем клетки внешнего (tmo от trouble maker out) 
        # и внутреннего (tmi от trouble maker in) квадрата,
        # стоящие при пустотах во внешней стенке

        if walls_conf:
            self.tmo = [[0,2],[4,2]]
            self.tmi = [[1,2],[3,2]]
            self.pass_points = [[2,0],[2,4]]
        else:
            self.tmo = [[2,0],[2,4]]
            self.tmi = [[2,1],[2,3]]
            self.pass_points = [[0,2],[4,2]]


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
    
    def move_in_graph(self):
        
        '''
        Продвигает робота в графе вперед по направлению

        Если есть возможность определить конфигурацию 
        внутренних стен ультразвуком - определяет её
        '''
        
        # Проверка возможности продвижения (чтобы не выйти за пределы сетки)
        if self.can_move():
            
            # Проверка возможности определения конфигурации внутренних стен
            if [self.next_point[0],self.next_point[1]] in self.tmo and not ([self.robot_pos[0],self.robot_pos[1]] in self.tmi):
                self.init_inner_walls(self.check_sonic() ^ self.walls_conf)
            
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


        # Проверяем, можем ли сейчас двигаться вдоль стены
        # (если можем, то вдоль какой; по умолчанию - левой (ИСПРАВИТЬ) )

        side = 'none'
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
            self.go.follow_till_wall(50,side_next,self.sonic)
        else:
            self.go.follow_wall(30,side,self.sonic)
        
        
        ### КОСТЫЛЬ (проезжаем еще немного +- вглубь клетки)
        self.go.forward_with_angle(50,0)
        time.sleep(1)
        self.go.stop()

        # Продвигаем робота в графе
        self.move_in_graph()
    

    def rotate(self,dir):
        self.go.forward_with_angle(0,dir*100)
        time.sleep(0.5)
        self.go.stop()
        self.rotate_in_graph(1)

    
    def check_sonic(self):

        '''
        Проверка ультразвуком наличия стенки в удалении (для определения внутренних стен)
        '''

        for i in self.field_map[self.robot_pos[0]][self.robot_pos[1]].walls:
            print((i-self.robot_dir)%4)
            print(i)
            if (i-self.robot_dir)%4 == 1:
                self.sonic.rotate_sensor_r()
                break
        else:
            self.sonic.rotate_sensor_l()
        time.sleep(1)

        dist = self.sonic.get_distance()
        print("SONIC:",dist)
        if (dist < self.MAX_SONIC_MIDDLE_DIST) and (dist > self.MIN_SONIC_MIDDLE_DIST):
            return 1
        return 0

    def can_move(self):
        
        '''
        Проверка возможности продвижения по графу
        (нет ли стены перед нами и не закончилась ли сетка)
        '''

        min_check = min(self.robot_pos+self.directions[self.robot_dir]) > -1
        max_check = min(self.robot_pos+self.directions[self.robot_dir]) < 5
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


ult = Ultrasonic()
go = RobotDirection()

coordinator = Coordinator([0,0], 0, [2,4], [0,2], [4,0], False, ult,go)
coordinator.show_field()

while True:
    comm = input()
    if comm == "0":
        coordinator.move_forward()
    elif comm == "1":
        coordinator.rotate(1)
    elif comm == "-1":
        coordinator.rotate(-1)
    elif comm == "q":
        break