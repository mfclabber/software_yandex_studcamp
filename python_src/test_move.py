from builtins import float, object
from xr_ultrasonic import Ultrasonic

import os
import time
import xr_gpio as gpio
import numpy as np
from xr_infrared import Infrared
from xr_configparser import HandleConfig


ir_sensor = Infrared()

class RobotDirection(object):
	def __init__(self):
		pass

	def set_speed(self, num, speed):
		"""
		设置电机速度，num表示左侧还是右侧，等于1表示左侧，等于右侧，speed表示设定的速度值（0-100）
		"""
		# print(speed)
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

	# def forward_with_angle(self, speed, angle): 
		
	# 	angle = min(100, angle)
	# 	angle = max(-100, angle)
		
	# 	speed2 = np.round(speed * (1 - abs(angle) / 50))
		
	# 	if angle > 0: 
	# 		self.set_speed(2, speed) # left
	# 		self.set_speed(1, abs(speed2)) # right
			
	# 		self.m3m4_reverse() # left? 
	# 		if speed2>0: 
	# 			self.m1m2_reverse() # right? 
	# 		else: 
	# 			self.m1m2_forward() # right? 
		
	# 	else: 
	# 		self.set_speed(2, abs(speed2)) # left
	# 		self.set_speed(1, speed) # right
			
	# 		self.m1m2_reverse() # right? 
	# 		if speed2>0: 
	# 			self.m3m4_reverse() # left? 
	# 		else: 
	# 			self.m3m4_forward() # left?

	def forward_with_angle(self, speed, angle): 
		
		angle = min(100, angle)
		angle = max(-100, angle)
		
		speed_l = max(-100,min(100, speed + angle))
		speed_r = max(-100,min(100, speed - angle))

		self.set_speed(1, abs(speed_r))
		self.set_speed(2, abs(speed_l))
		
		if speed_l<0:
			self.m3m4_forward()
		else:
			self.m3m4_reverse()
		
		if speed_r<0:
			self.m1m2_forward()
		else:
			self.m1m2_reverse()


	def reverse(self, speed): 

		self.set_speed(2, speed) # left
		self.set_speed(1, speed) # right
			
		self.m3m4_forward() # left? 
		self.m1m2_forward() # right? 
	
	def follow_till_wall(self,dist,s,ul):
		n = 3
		speed = 40

		if s=="l":
			ul.rotate_sensor_l()
		else:
			ul.rotate_sensor_r()
		time.sleep(0.5)

		arr = [ul.get_distance() for i in range(n)]
		m = sum(arr)/n
		
		while m > dist+20:
			self.forward_with_angle(speed,0)
			arr.append(ul.get_distance())
			m += arr[-1]/n
			m -= arr.pop(0)/n
		
		print("Wall is found!")

		self.stop()

	def follow_wall(self,dist,s,ul):
		n = 3
		kp = 1
		kd = 5
		speed = 40
		angle_lim = 20

		if s == "r":
			kp = -kp
			kd = -kd
		
		self.follow_till_wall(dist,s,ul)

		arr = [ul.get_distance() for i in range(n)]
		m = sum(arr)/n
		diff = [arr[i+1]-arr[i] for i in range(n-1)]
		diff.append (diff[-1])
		m_d = sum(diff)/n

		# flag1, flag2 = 0,0
		# sign = 1
		# change_state = 0
		while (abs(m_d)<10):
			#print(m_d)
			error_correct = (dist-m)*kp+m_d*kd
			err = max(-angle_lim, min(error_correct,angle_lim))

			# if m>50 and flag1==0:
			# 	flag1 = 1
			# if m<=50 and flag1==1:
			# 	flag1 = 0
			# if flag1 != flag2:
			# 	change_state +=1
			# 	flag1=flag2
			# if change_state % 4 == 0:
			# 	sign = sign*-1

			self.forward_with_angle(speed,err)
			#print("angle:", round(err),"dist:",m )
			new_d = ul.get_distance()
			if new_d == -1:
				pass
			else:
				arr.append(new_d)
				m += arr[-1]/n
				m -= arr.pop(0)/n
				diff.append(arr[-1]-arr[-2])
				m_d += diff[-1]/n
				m_d -= diff.pop(0)/n
		self.stop()
		print(m_d, m)
		#print(arr, diff)
		#print("stopped")

	def gentle_move(self):
		step_angle = 15
		max_angle = 60
		cur_angle = 0
		stop = False
		while (ir_sensor.get_data_m() == 0)and(cur_angle<max_angle):
			if ir_sensor.get_data_m() == 1:
				stop = True
				break
			cur_angle += step_angle
			self.forward_with_angle(0, step_angle)
			time.sleep(0.5)
			self.stop()

		while (ir_sensor.get_data_m() == 0)and(cur_angle>-max_angle):
			if ir_sensor.get_data_m() == 1:
				stop = True
				break
			cur_angle -= step_angle
			self.forward_with_angle(0, -step_angle)
			time.sleep(0.5)
			self.stop()

		if not stop:
			self.reverse(10)
			time.sleep(0.5)
			self.stop()
			while (ir_sensor.get_data_m == 0)and(cur_angle<max_angle):
				if ir_sensor.get_data_m() == 1:
					stop = True
					break
				cur_angle += step_angle
				self.forward_with_angle(step_angle/2, step_angle)
				time.sleep(0.5)
				self.stop()

			while (ir_sensor.get_data_m() == 0)and(cur_angle>-max_angle):
				if ir_sensor.get_data_m() == 1:
					stop = True
					break
				cur_angle -= step_angle
				self.forward_with_angle(step_angle/2, step_angle)
				time.sleep(0.5)
				self.stop()


#ul = Ultrasonic()

# go.follow_wall(30,"r",ul)
#go.gentle_move()

# go.forward_with_angle(30, 0)
# time.sleep(1)
# go.forward_with_angle(75, -20)
# # go.reverse(100)
# time.sleep(5)
# go.forward_with_angle(50,-100)
# time.sleep(1)
# go.stop()