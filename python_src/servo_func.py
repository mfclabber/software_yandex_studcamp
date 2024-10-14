from xr_i2c import I2c
import time

i2c = I2c()

max_angles = [130, 330, 65, 35] # 1 4 3 2
get_object_angles = [50, 160, 65, 60] # 1 4 3 2
getup_object_angles = [130, 160, 65, 35] 
starting_take_ball_object_angles = [0, 330, 65, 200] 

class Servo_Func_CLASS():
    def starting_pose(self):
        '''Исходное положение манипулятора (вверх)'''
        for num, angle in enumerate(max_angles):

            buf = [0xff, 0x01, num+1, angle, 0xff]
            i2c.writedata(i2c.mcu_address, buf)

        time.sleep(1)


    def start_take_object(self):
        '''Взять объект'''

        for num, angle in enumerate(get_object_angles):

            if num+1 == 2:
                angle = max_angles[1]

            buf = [0xff, 0x01, num+1, angle, 0xff]
            i2c.writedata(i2c.mcu_address, buf)

        time.sleep(1)


    def take_object(self):
        for num, angle in enumerate(get_object_angles):

            buf = [0xff, 0x01, num+1, angle, 0xff]
            i2c.writedata(i2c.mcu_address, buf)

        time.sleep(1)


    def getup_object(self):
        '''Поднять объект'''

        for num, angle in enumerate(get_object_angles):

            #if num+1 == 4:
            #    angle = get_object_angles[3] + 30
            if num+1 == 1:
                angle = max_angles[0]

            buf = [0xff, 0x01, num+1, angle, 0xff]
            i2c.writedata(i2c.mcu_address, buf)

        time.sleep(0.7)

        for num, angle in enumerate(getup_object_angles):
            
            if num == 3:

                for range_angle in range(get_object_angles[-1], angle, -5):
                    buf = [0xff, 0x01, num+1, range_angle, 0xff]
                    i2c.writedata(i2c.mcu_address, buf)
                    time.sleep(0.1)


    def starting_take_ball(self):

        # buf = [0xff, 0x01, 4, starting_take_ball_object_angles[-1], 0xff]
        # i2c.writedata(i2c.mcu_address, buf)

        # time.sleep(1)

        for num, angle in enumerate(starting_take_ball_object_angles):
            if num == 0:
                angle += 20
            buf = [0xff, 0x01, num+1, angle, 0xff]
            i2c.writedata(i2c.mcu_address, buf)

        time.sleep(1)


    def take_ball(self):
        for num, angle in enumerate(starting_take_ball_object_angles):
            if num == 1:
                
                buf = [0xff, 0x01, num+1, get_object_angles[1], 0xff]
                i2c.writedata(i2c.mcu_address, buf)

        time.sleep(1)

servo = Servo_Func_CLASS()
servo.starting_pose()
# starting_take_ball()
# take_ball()
# start_take_object()
# take_object()
# getup_object()