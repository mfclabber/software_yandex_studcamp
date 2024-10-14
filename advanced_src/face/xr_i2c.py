# coding:utf-8
"""
@version: python3.7
@Author  : xiaor
@Explain :I2C与单片机通信
@contact :
@Time    :2020/05/09
@File    :XiaoR_i2c.py
@Software: PyCharm
"""
import os
import time
from builtins import IOError, object, len

import smbus


# # smbus
# self.device = smbus.SMBus(1)  # 0代表/dev/i2c0  1代表/dev/i2c1
# # I2C通信地址
# address = 0x18


class I2c(object):
	def __init__(self):
		self.mcu_address = 0x18
		self.ps2_address = 0x19
		self.device = smbus.SMBus(1)
		pass

	def writedata(self, address, values):
		'''
		# 向I2C地址写入指令
		'''
		try:
			self.device.write_i2c_block_data(address, values[0],
											 values[1:len(values)])  # 连续写入，第一个参数：器件地址，第二个参数：写入寄存器地址，
			# 小R的MCU没有寄存器地址故写入的是第一帧数据，第三个参数：要写入的数据
			time.sleep(0.01)
		except Exception as e:  # 写入出错
			print('i2c write error:', e)
			os.system('sudo i2cdetect -y 1')

	def readdata(self, address, index):
		'''
		#从I2C读取一个字节的数据
		'''
		try:
			value = self.device.read_byte_data(address, index)  # 读取从设备偏移处index的一个字节
			time.sleep(0.08)
			return value  # 返回读取到的数据
		except Exception as e:  # 读取出错
			print('i2c read error:', e)
			os.system('sudo i2cdetect -y 1')
