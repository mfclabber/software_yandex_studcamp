import numpy as np
from xr_infrared import Infrared
from xr_ultrasonic import Ultrasonic
import time

class Cell:
    def __init__(self, pos, walls, cell_obj):
        self.pos = np.array(pos)
        self.walls = walls
        self.cell_obj = cell_obj
    
    def print_cell(self):
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
    def __init__(self, robot_pos, robot_dir, base_pos, rg_pos, rg_conf, bm_conf, cube_pos, walls_conf, infr, sonic):
        
        self.infr = infr
        self.sonic = sonic
        self.MAX_SONIC_DIST = 40 #
        self.MIN_SONIC_DIST = 70 #

        self.field_map = [[0]*5 for i in range(5)]

        self.directions = [
            np.array( [0, 1] ),     # 0 north
            np.array( [1, 0] ),     # 1 east
            np.array( [0, -1] ),    # 2 south
            np.array( [-1, 0] )     # 3 west
        ]


        self.robot_dir = robot_dir

        for x in range(5):
            for y in range(5):
                self.field_map[x][y] = Cell([x,y],[],["  "])
        
        self.walls_conf = walls_conf
        self.init_out_walls()
        
        if walls_conf:
            self.tmo = [[0,2],[4,2]]
            self.tmi = [[1,2],[3,2]]
        else:
            self.tmo = [[2,0],[2,4]]
            self.tmi = [[2,1],[2,3]]

        self.robot_pos = np.array(robot_pos)
        self.robot_pos_e = np.array(self.inv_pos(robot_pos))
        self.field_map[robot_pos[0]][robot_pos[1]].cell_obj.append("r1")
        self.field_map[self.robot_pos_e[0]][self.robot_pos_e[1]].cell_obj.append("r2")


        self.base_pos = np.array(base_pos)
        self.base_pos_e = self.inv_pos(base_pos)
        self.field_map[base_pos[0]][base_pos[1]].cell_obj.append("b1")
        self.field_map[self.base_pos_e[0]][self.base_pos_e[1]].cell_obj.append("b2")


        self.rg_pos = np.array(rg_pos)
        self.bm_pos = self.inv_pos(rg_pos)
        
        self.field_map[rg_pos[0]][rg_pos[1]].cell_obj.append(rg_conf)
        self.field_map[self.bm_pos[0]][self.bm_pos[1]].cell_obj.append(bm_conf)

        self.rg_conf = rg_conf
        self.bm_conf = bm_conf

        self.cube_pos = np.array(cube_pos)
        self.cube_pos_e = self.inv_pos(cube_pos)
        self.field_map[cube_pos[0]][cube_pos[1]].cell_obj.append("c1")
        self.field_map[self.cube_pos_e[0]][self.cube_pos_e[1]].cell_obj.append("c2")

        self.next_point = self.robot_pos+self.directions[self.robot_dir]


    def rotate(self,direction):
        self.robot_dir = (self.robot_dir+direction)%4
        self.next_point = self.robot_pos+self.directions[self.robot_dir]
    
    def move(self):
        if self.can_move():
            if [self.next_point[0],self.next_point[1]] in self.tmo and not ([self.robot_pos[0],self.robot_pos[1]] in self.tmi):
                self.init_inner_walls(self.check_sonic() ^ self.walls_conf)

            self.field_map[self.robot_pos[0]][self.robot_pos[1]].cell_obj.pop()
            self.robot_pos += self.directions[self.robot_dir]
            self.field_map[self.robot_pos[0]][self.robot_pos[1]].cell_obj.append("r1")
            self.next_point = self.robot_pos+self.directions[self.robot_dir]

            self.show_field()
    
    def movement_detector(self):
        if self.can_move():
            npt_w = []
            for i in self.field_map[self.next_point[0]][self.next_point[1]].walls:
                npt_w.append((i-self.robot_dir)%4)
            if (([self.robot_pos[0],self.robot_pos[1]] in self.tmo)) and ([self.next_point[0],self.next_point[1]] in self.tmi):
                if self.check_sonic():
                    self.move()
            elif (([self.robot_pos[0],self.robot_pos[1]] in self.tmi)) and ([self.next_point[0],self.next_point[1]] in self.tmo):
                if not (self.check_sonic()):
                    self.move()
            elif (self.check_r() == (1 in npt_w)) and (self.check_l() == (3 in npt_w)):
                self.move()
    
    def check_r(self):
        print(not self.infr.get_data("r"))
        return not self.infr.get_data("r")

    def check_l(self):
        print(not self.infr.get_data("l"))
        return not self.infr.get_data("l")
    
    def check_sonic(self):
        for i in self.field_map[self.next_point[0]][self.next_point[1]].walls:
            if (i-self.robot_dir)%4 == 1:
                self.sonic.rotate_sensor_l()
                break
        else:
            self.sonic.rotate_sensor_r()
        time.sleep(0.3)

        dist = self.sonic.get_distance()
        print(dist)
        if (dist < self.MAX_SONIC_DIST): #and (dist > self.MIN_SONIC_DIST):
            return 1
        return 0

    def can_move(self):
        min_check = min(self.robot_pos+self.directions[self.robot_dir]) > -1
        max_check = min(self.robot_pos+self.directions[self.robot_dir]) < 5
        return not(self.robot_dir in self.field_map[self.robot_pos[0]][self.robot_pos[1]].walls) and min_check and max_check

    def inv_pos(self,pos):
        return np.array([abs(4-pos[0]),abs(4-pos[1])])

    def init_inner_walls(self,walls_conf):
        self.init_out_walls()
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
        
        # внешние границы

        # for x in range(5):
        #     self.field_map[x][0].walls.append(2)
        #     self.field_map[x][4].walls.append(0)
        
        # for y in range(5):
        #     self.field_map[0][y].walls.append(3)
        #     self.field_map[4][y].walls.append(1)
        
        # переопределяем стены

        for x in range(5):
            for y in range (5):
                self.field_map[x][y].walls = []

        # определяем корзинки и кнопки как препядствия, чтобы сверять местоположение по ним

        self.field_map[2][0].walls.append(2)
        self.field_map[0][2].walls.append(3)
        self.field_map[2][4].walls.append(0)
        self.field_map[4][2].walls.append(1)

        # углы

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

        # стены внешнего квадрата

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

infr = Infrared()
sonic = Ultrasonic()
coordinator = Coordinator([0,0], 0, [2,4], [0,2], "rg", "mb", [4,0], True, infr, sonic)
coordinator.show_field()
ans = input()
while ans!="":
    if ans == "m":
        coordinator.movement_detector()
    elif ans == "r":
        coordinator.rotate(1)
    elif ans == "l":
        coordinator.rotate(-1)
    coordinator.show_field()
    ans = input()