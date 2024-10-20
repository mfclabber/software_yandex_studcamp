from xr_i2c import I2c
import time

# 1 4 3 2

i2c = I2c()

# max_angles = [130, 290, 65, 130] # 1 2 3 4
# get_object_angles = [45, 320, 65, 160]
# getup_object_angles = [130, 290, 65, 160]
# starting_take_ball_object_angles = [-30, 440, 65, 200]


class CTRL_Servo():
    def __init__(self):

        self.INIT_ANGLES = [130, 290, 65, 140]

        self.NOW_ANGLES = [130, 290, 65, 140]

        self.OPENED_CLAW_ANGLE = 140
        self.CLOSED_CLAW_ANGLE = 160

        self.ROTATED_S3 = 155
        self.NOT_ROTATED_S3 = 65

        self.HIGH_S1 = 130 # init pose
        self.HIGH_S2 = 290 # init pose

        self.MIDDLE_S1 = 50 # S1 for cube
        self.MIDDLE_S2 = 320 # S2 for cube

        self.LOW_S1 = 130 # S1 for ball
        self.LOW_S2 = 290 # S2 for ball

        self.PUSH_S1 = 130
        self.PUSH_S2 = 260
        # self.max_angles = []

        self.standart_pose()
        # self.max_angles = [130, 290, 65, 130]  # 1 2 3 4
        # self.get_object_angles = [45, 320, 65, 160]
        # self.getup_object_angles = [130, 290, 65, 160]
        # self.starting_take_ball_object_angles = [-30, 440, 65, 200]

    def set_s1(self,angle):
        buf = [0xff, 0x01, 1, angle, 0xff]  # соответствует S1 проводу (нижний двигатель)
        i2c.writedata(i2c.mcu_address, buf)
        self.NOW_ANGLES[0] = angle

    def set_s2(self,angle):
        buf = [0xff, 0x01, 2, angle, 0xff]  # соответствует S2 проводу (cгибание/разгибание в "логте")
        i2c.writedata(i2c.mcu_address, buf)
        self.NOW_ANGLES[1] = angle

    def set_s3(self,angle):
        buf = [0xff, 0x01, 3, angle, 0xff]  # соответствует S3 проводу (вращающий клешню двигатель)
        i2c.writedata(i2c.mcu_address, buf)
        self.NOW_ANGLES[2] = angle

    def set_s4(self,angle):
        buf = [0xff, 0x01, 4, angle, 0xff]  # соответствует S4 проводу (клешня)
        i2c.writedata(i2c.mcu_address, buf)
        self.NOW_ANGLES[3] = angle
    
    def set_angles(self, angles):
        self.set_s1(angles[0])
        self.set_s2(angles[1])
        self.set_s3(angles[2])
        self.set_s4(angles[3])

    def standart_pose(self):
        self.set_angles(self.INIT_ANGLES)

    def set_claw(self,state):
        if state:
            self.set_s4(self.CLOSED_CLAW_ANGLE)
        else:
            self.set_s4(self.OPENED_CLAW_ANGLE)

    def high_pose(self):
        self.set_s1(self.HIGH_S1)
        self.set_s2(self.HIGH_S2)

    def middle_pose(self):
        self.set_s1(self.MIDDLE_S1)
        self.set_s2(self.MIDDLE_S2)

    def low_pose(self):
        self.set_s1(self.LOW_S1)
        self.set_s2(self.LOW_S2)

    def set_pose(self, s1, s2):
        self.set_s1(s1)
        self.set_s2(s2)

    def gently_change(self, angle):
        s10 = self.NOW_ANGLES[0]
        s20 = self.NOW_ANGLES[1]
        s30 = self.NOW_ANGLES[2]
        s40 = self.NOW_ANGLES[3]

        n = 10

        for i in range(n+1):
            
            
            #print(round(s10+(angle[0]-s10)*i/10),round(s20+(angle[1]-s20)*i/10),round(s30+(angle[2]-s30)*i/10),round(s40+(angle[3]-s40)*i/10))

            if angle[0]:
                self.set_s1(round(s10+(angle[0]-s10)*i/n))
            if angle[1]:
                self.set_s2(round(s20+(angle[1]-s20)*i/n))
            if angle[2]:
                self.set_s3(round(s30+(angle[2]-s30)*i/n))
            if angle[3]:
                self.set_s4(round(s40+(angle[3]-s40)*i/n))
            time.sleep(0.05)

    def take_cube(self):
        self.standart_pose()
        time.sleep(0.5)
        self.middle_pose()
        time.sleep(0.5)
        self.set_claw(True)
        time.sleep(0.5)
        self.set_s1(self.HIGH_S1)
        time.sleep(0.5)
        self.gently_change([False, self.HIGH_S2, False, False])
        time.sleep(0.5)
        self.high_pose()

    def push_button(self):
        self.set_claw(True)
        self.set_s3(self.ROTATED_S3)
        self.high_pose()
        time.sleep(0.5)
        self.gently_change([self.HIGH_S1-50, self.HIGH_S2+90, False, False])
        time.sleep(1)
        #self.set_pose(self.HIGH_S1, self.HIGH_S2 + 30)
        #time.sleep(0.5)
        # self.set_claw(True)
        #self.set_pose(self.HIGH_S1 - 50, self.HIGH_S2 + 90)
        #time.sleep(0.5)
        self.set_pose(self.HIGH_S1 - 80, self.HIGH_S2 + 80)
        time.sleep(1)
        self.set_pose(self.HIGH_S1-60, self.HIGH_S2+90)
        time.sleep(0.5)

    def drop_object(self):
        self.set_pose(self.HIGH_S1, self.HIGH_S2)
        time.sleep(0.5)
        self.set_pose(self.HIGH_S1, self.HIGH_S2+40)
        time.sleep(0.5)
        self.set_pose(self.HIGH_S1-60, self.HIGH_S2+90)
        time.sleep(0.5)
        self.set_claw(False)

    # def heil(self):
    #     self.set_pose(self.HIGH_S1, self.HIGH_S2)
    #     time.sleep(0.5)
    #     self.set_pose(self.HIGH_S1-80, self.HIGH_S2+140)
    #     time.sleep(0.5)
    #     # self.set_claw(False)

    def take_ball(self):
        self.set_pose(self.HIGH_S1, self.HIGH_S2)
        time.sleep(0.5)
        self.set_pose(self.HIGH_S1-80, self.HIGH_S2+100)
        time.sleep(0.5)
        self.set_pose(self.HIGH_S1-130, self.HIGH_S2+140)
        time.sleep(0.8)
        self.set_claw(True)
        time.sleep(0.5)
        self.set_pose(self.HIGH_S1-80, self.HIGH_S2+100)
        time.sleep(0.5)
        self.set_pose(self.HIGH_S1, self.HIGH_S2)
        time.sleep(0.5)

    def hit(self):
        self.set_pose(self.HIGH_S1, self.HIGH_S2)
        time.sleep(0.5)
        self.set_claw(True)
        for i in range(5):
            self.set_pose(self.HIGH_S1-80, self.HIGH_S2+140)
            time.sleep(0.3)
            self.set_pose(self.HIGH_S1, self.HIGH_S2)
            time.sleep(0.2)



control_s = CTRL_Servo()

control_s.standart_pose()
#time.sleep(1)
# control_s.hit()

# control_s.push_button()
# time.sleep(1)
# control_s.standart_pose()
# control_s.take_cube()
# time.sleep(1)
# control_s.drop_object()
# time.sleep(1)
# control_s.standart_pose()

# control_s.drop_object()
# time.sleep(1)
# time.sleep(2)
# control_s.set_claw(False)
# control_s.high_pose()
# control_s.high_pose()


#control_s.gently_change([control_s.HIGH_S1,control_s.MIDDLE_S2,65,130])


# servo.starting_take_ball()
# take_ball()
# start_take_object()
# take_object()

# servo.getup_object()
# servo.starting_pose()