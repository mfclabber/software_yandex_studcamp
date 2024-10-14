"""
Исходный код для управления роботом с видео на Raspberry Pi через WiFi
Автор: Sence
Авторские права: XiaoR Technology (Shenzhen XiaoErGeek Technology Co., Ltd. www.xiao-r.com); Форум WiFi Robot Network www.wifi-robots.com
Этот код можно свободно изменять, но запрещено использовать его в коммерческих целях!
Код защищен авторским правом на программное обеспечение, при обнаружении нарушения будет подан иск!
"""
"""
@version: python3.7
@Author  : xiaor
@Explain : Инфракрасный
@contact :
@Time    : 2020/05/09
@File    : xr_infrared.py
@Software: PyCharm
"""
import xr_gpio as gpio
import xr_config as cfg

from xr_motor import RobotDirection

go = RobotDirection()


class Infrared(object):
	def __init__(self):
		pass

	def trackline(self):
		"""
		Инфракрасное слежение по линии
		"""
		cfg.LEFT_SPEED = 30
		cfg.RIGHT_SPEED = 30
		# print('ir_trackline run...')
		# Оба датчика не обнаружили черную линию
		if (gpio.digital_read(gpio.IR_L) == 0) and (gpio.digital_read(gpio.IR_R) == 0):  # Черная линия - высокий уровень, поверхность - низкий
			go.forward()
		# Правый инфракрасный датчик обнаружил черную линию
		elif (gpio.digital_read(gpio.IR_L) == 0) and (gpio.digital_read(gpio.IR_R) == 1):
			go.right()
		# Левый датчик обнаружил черную линию
		elif (gpio.digital_read(gpio.IR_L) == 1) and (gpio.digital_read(gpio.IR_R) == 0):
			go.left()
		# Оба датчика одновременно обнаружили черную линию
		elif (gpio.digital_read(gpio.IR_L) == 1) and (gpio.digital_read(gpio.IR_R) == 1):
			go.stop()

	def iravoid(self):
		"""
		Инфракрасное избегание препятствий
		"""
		if gpio.digital_read(gpio.IR_M) == 0:		# Если средний датчик обнаружил препятствие
			go.stop()
		# print("Инфракрасное избегание препятствий")

	def irfollow(self):
		"""
		Инфракрасное следование
		"""
		cfg.LEFT_SPEED = 30
		cfg.RIGHT_SPEED = 30
		if  (gpio.digital_read(gpio.IRF_L) == 0 and gpio.digital_read(gpio.IRF_R) == 0 and gpio.digital_read(gpio.IR_M) == 1):
			go.stop()				# Остановка: оба датчика обнаружили препятствие или оба не обнаружили препятствие
		else:
			if gpio.digital_read(gpio.IRF_L) == 1 and gpio.digital_read(gpio.IRF_R) == 0:
				cfg.LEFT_SPEED = 50
				cfg.RIGHT_SPEED = 50
				go.right()			# Левый датчик не обнаружил препятствие, а правый обнаружил
			elif gpio.digital_read(gpio.IRF_L) == 0 and gpio.digital_read(gpio.IRF_R) == 1:
				cfg.LEFT_SPEED = 50
				cfg.RIGHT_SPEED = 50
				go.left()			# Левый датчик обнаружил препятствие, а правый нет
			elif (gpio.digital_read(gpio.IRF_L) == 1 and gpio.digital_read(gpio.IRF_R) == 1) or (gpio.digital_read(gpio.IRF_L) == 1 and gpio.digital_read(gpio.IRF_R) == 1):
				cfg.LEFT_SPEED = 50
				cfg.RIGHT_SPEED = 50
				go.forward()		# Движение вперед: только средний датчик обнаружил препятствие

	def avoiddrop(self):
		"""
		Инфракрасная защита от падений
		"""
		cfg.LEFT_SPEED = 25
		cfg.RIGHT_SPEED = 25
		if (gpio.digital_read(gpio.IR_L) == 0) and (gpio.digital_read(gpio.IR_R) == 0):  # Оба инфракрасных датчика обнаружили поверхность
			cfg.AVOIDDROP_CHANGER = 1		# Флаг установлен в 1, это используется для направления в анализе через последовательный порт
		else:
			if cfg.AVOIDDROP_CHANGER == 1: 	# Остановка происходит только тогда, когда предыдущий статус был нормальным, чтобы избежать повторного выполнения команды остановки и невозможности дальнейшего управления
				go.stop()
				cfg.AVOIDDROP_CHANGER = 0

	def get_data(self, side):
		if side=="l":
			return gpio.digital_read(gpio.IRF_L)
		elif side=="m":
			return gpio.digital_read(gpio.IRF_M)
		elif side=="r":
			return gpio.digital_read(gpio.IRF_R)
