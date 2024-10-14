import time
import math
from builtins import float, object

import xr_gpio as gpio


class RobotDirection(object):
	def __init__(self):
		pass

	def set_speed(self, num, speed):
	
		if num == 1:  # 调节左侧
			gpio.ena_pwm(speed)
		elif num == 2:  # 调节右侧
			gpio.enb_pwm(speed)

	def m1m2_forward(self):
		# 设置电机组M1、M2正转
		gpio.digital_write(gpio.IN1, True)
		gpio.digital_write(gpio.IN2, False)

	def m1m2_reverse(self):
		# 设置电机组M1、M2反转
		gpio.digital_write(gpio.IN1, False)
		gpio.digital_write(gpio.IN2, True)

	def m1m2_stop(self):
		# 设置电机组M1、M2停止
		gpio.digital_write(gpio.IN1, False)
		gpio.digital_write(gpio.IN2, False)

	def m3m4_forward(self):
		# 设置电机组M3、M4正转
		gpio.digital_write(gpio.IN3, True)
		gpio.digital_write(gpio.IN4, False)

	def m3m4_reverse(self):
		# 设置电机组M3、M4反转
		gpio.digital_write(gpio.IN3, False)
		gpio.digital_write(gpio.IN4, True)

	def m3m4_stop(self):
		# 设置电机组M3、M4停止
		gpio.digital_write(gpio.IN3, False)
		gpio.digital_write(gpio.IN4, False)

	
	def stop(self):
		"""
		#设置机器人运动方向为停止
		"""
		self.set_speed(1, 0)
		self.set_speed(2, 0)
		self.m1m2_stop()
		self.m3m4_stop()
	
	def forward_r_l(self, speedr, speedl):

		self.set_speed(1,abs(round(speedr)))
		self.set_speed(2,abs(round(speedl)))

		if speedr>0:
			self.m1m2_reverse()
		else:
			self.m1m2_forward()
		if speedl>0:
			self.m3m4_reverse()
		else:
			self.m3m4_forward()

go = RobotDirection()


def vector_length(v):
	return (v[0]**2+v[1]**2)**0.5
def vector_sub(a,b):
	return [a[0]-b[0],a[1]-b[1]]
def vector_a(v):
	if (v[0]!=0):
		return math.atan(v[1]/v[0])
	return (math.pi/2)

def go_xy(x,y):
	UT_TO_RADIANS = 0.01

	r = 10
	B = 25

	points = [[x,y]]
	point = points[0]
	theta = 0

	robot = [0,0]
	p = vector_sub(point,robot)
	fi = math.atan2(p[1],p[0])
	a = fi-theta
	time0 = time.time()
	ang_l = 0
	ang_r = 0
	t = 0

	k_1 = 10
	k_2 = 150
	
	ang_l = 0
	ang_r = 0

	print("---------------------------------")
	print("non-linear")
	print("point:",point[0],point[1])
	while (vector_length(p)>10):
		#print(p,a)
		p = vector_sub(point,robot)
		fi = math.atan2(p[1],p[0])
		a = fi-theta

		if a <= -math.pi:
			a += 2 * math.pi
		elif a >= math.pi:
			a -= 2 * math.pi
		
		ang_l_pr = ang_l
		ang_r_pr = ang_r
		theta_pr = theta
		t_pr = t
		x_pr = robot[0]
		y_pr = robot[1]
		u_v = k_1*vector_length(p)*math.cos(a)
		u_w = k_1*math.cos(a)*math.sin(a)+k_2*a
		Ul = u_v-u_w
		Ur = u_v+u_w
		print(Ul,Ur)
		if Ul>100:
			Ul = 100
		if Ul<-100:
			Ul = -100
		if Ur>100:
			Ur = 100
		if Ur<-100:
			Ur = -100
		t = time.time()-time0

		go.forward_r_l(Ul,Ur)

		ang_l += UT_TO_RADIANS*Ul*t
		ang_r += UT_TO_RADIANS*Ur*t
		d_ang_l = ang_l-ang_l_pr
		d_ang_r = ang_r-ang_r_pr
		theta = theta_pr+(d_ang_r-d_ang_l)*r/B
		robot[0] = x_pr+(d_ang_l+d_ang_r)*r*math.cos(theta)/2
		robot[1] = y_pr+(d_ang_l+d_ang_r)*r*math.sin(theta)/2
		
		print("x:"+str(robot[0])+" y:"+str(robot[1]))
		time.sleep(0.1)
        
	print("Yay! I did it :3")
	go.stop()

go_xy(0,500)