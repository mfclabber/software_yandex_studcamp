# coding:utf-8
"""
Драйвер исходного кода для робота с Wi-Fi на базе Raspberry Pi
Автор: Sence
Правообладатель: XiaoR Technology (Shenzhen XiaoerGeek Technology Co., Ltd www.xiao-r.com); Форум WiFi Robots www.wifi-robots.com
Этот код может свободно модифицироваться, но запрещено использовать его в коммерческих целях!
Этот код защищён авторскими правами на программное обеспечение, любое нарушение будет немедленно преследоваться по закону!
"""
"""
@version: python3.7
@Author  : xiaor
@Explain : управление сервоприводом
@contact :
@Time    :2020/05/09
@File    :XiaoR_servo.py
@Software: PyCharm
"""
from builtins import hex, eval, int, object
from xr_i2c import I2c
import os

i2c = I2c()
import xr_config as cfg

from xr_configparser import HandleConfig
path_data = os.path.dirname(os.path.realpath(__file__)) + '/data.ini'
cfgparser = HandleConfig(path_data)


class Servo(object):
	"""
	Класс для управления сервоприводом
	"""
	def __init__(self):
		pass

	def angle_limit(self, angle):
		"""
		Ограничение угла сервопривода, чтобы предотвратить блокировку и перегрев сервопривода
		"""
		if angle > cfg.ANGLE_MAX:  # Ограничение максимального угла
			angle = cfg.ANGLE_MAX
		elif angle < cfg.ANGLE_MIN:  # Ограничение минимального угла
			angle = cfg.ANGLE_MIN
		return angle

	def set(self, servonum, servoangle):
		"""
		Установка угла сервопривода
		:param servonum: номер сервопривода
		:param servoangle: угол сервопривода
		:return:
		"""
		angle = self.angle_limit(servoangle)
		buf = [0xff, 0x01, servonum, angle, 0xff]
		try:
			i2c.writedata(i2c.mcu_address, buf)
		except Exception as e:
			print('Ошибка записи в сервопривод:', e)

	def store(self):
		"""
		Сохранение угла сервопривода
		:return:
		"""
		cfgparser.save_data("servo", "angle", cfg.ANGLE)

	def restore(self):
		"""
		Восстановление угла сервопривода
		:return:
		"""
		cfg.ANGLE = cfgparser.get_data("servo", "angle")
		for i in range(0, 8):
			cfg.SERVO_NUM = i + 1
			cfg.SERVO_ANGLE = cfg.ANGLE[i]
			self.set(i + 1, cfg.ANGLE[i])
