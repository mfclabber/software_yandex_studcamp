from builtins import float, object

import os
import time
import xr_gpio as gpio

from xr_configparser import HandleConfig


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

	def forward_with_angle(self, speed, angle): 

		angle = min(100, angle)
		angle = max(-100, angle)
		
		speed2 = round(speed*(1-abs(angle)/50))
		
		if angle > 0: 
			self.set_speed(2, speed) # left
			self.set_speed(1, abs(speed2)) # right
			
			self.m3m4_reverse() # left? 
			if speed2>0: 
				self.m1m2_reverse() # right? 
			else: 
				self.m1m2_forward() # right? 
		
		else: 
			self.set_speed(2, abs(speed2)) # left
			self.set_speed(1, speed) # right
			
			self.m1m2_reverse() # right? 
			if speed2>0: 
				self.m3m4_reverse() # left? 
			else: 
				self.m3m4_forward() # left?

	def reverse(self, speed): 

		self.set_speed(2, speed) # left
		self.set_speed(1, speed) # right
			
		self.m3m4_forward() # left? 
		self.m1m2_forward() # right? 

go = RobotDirection()

go.forward_with_angle(50, 100)
time.sleep(0.6)
go.forward_with_angle(75, -20)
# go.reverse(100)
time.sleep(5)
go.forward_with_angle(50,-100)
time.sleep(1)
go.stop()