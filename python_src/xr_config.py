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
@Explain : конфигурационный файл
@contact :
@Time    :2020/05/09
@File    :xr_config.py
@Software: PyCharm
"""

from socket import *
import numpy as np


CRUISING_FLAG = 0  # Текущий режим круиза, разные флаги означают разные режимы, задаются управляющим программным обеспечением.
PRE_CRUISING_FLAG = 0  # Предварительный режим круиза
CRUISING_SET = {'normal': 0, 'irfollow': 1, 'trackline': 2, 'avoiddrop': 3, 'avoidbyragar': 4, 'send_distance': 5,
		 'maze': 6, 'camera_normal': 7, 'camera_linepatrol': 8, 'facefollow':9, 'colorfollow':10, 'qrcode_detection':11}
CAMERA_MOD_SET = {'camera_normal': 0, 'camera_linepatrol': 1, 'facefollow':2, 'colorfollow':3, 'qrcode_detection':4}

ANGLE_MAX = 160  # Максимальный угол сервопривода, предотвращающий блокировку, можно установить значение меньше 180
ANGLE_MIN = 15  # Минимальный угол сервопривода, предотвращающий блокировку, можно установить значение больше 0

VOICE_MOD = 0
VOICE_MOD_SET = {'normal': 0, 'openlight': 1, 'closelight': 2, 'forward': 3, 'back': 4, 'left': 5,
		 'right': 6, 'stop': 7, 'nodhead': 8, 'shakehead':9}

PATH_DECT_FLAG = 0  # Флаг для отслеживания линии камерой: 0 - черная линия (светлая поверхность, темная линия); 1 - белая линия (темная поверхность, светлая линия)

LEFT_SPEED = 80  # Скорость левой стороны робота
RIGHT_SPEED = 80  # Скорость правой стороны робота
LASRT_LEFT_SPEED = 100  # Предыдущая скорость левой стороны робота
LASRT_RIGHT_SPEED = 100  # Предыдущая скорость правой стороны робота

SERVO_NUM = 1  # Номер сервопривода
SERVO_ANGLE = 90  # Угол сервопривода
SERVO_ANGLE_LAST = 90  # Предыдущий угол сервопривода
ANGLE = [90, 90, 90, 90, 90, 90, 90, 5]  # Углы для 8 сервоприводов

DISTANCE = 0  # Значение измерения расстояния ультразвуковым датчиком
AVOID_CHANGER = 1  # Флаг активации ультразвукового избегания препятствий
AVOIDDROP_CHANGER = 1  # Флаг активации инфракрасного предотвращения падения

MAZE_TURN_TIME = 400  # Время поворота в режиме лабиринта

CAMERA_MOD = 0  # Режим камеры
LINE_POINT_ONE = 320  # Координата x для первой линии при отслеживании линии камерой
LINE_POINT_TWO = 320  # Координата x для второй линии при отслеживании линии камерой

CLAPPER = 4  # Музыкальный ритм для зуммера
BEET_SPEED = 50  # Скорость воспроизведения зуммером
TUNE = 0  # Настройка тона для пианино, по умолчанию на C, от 0 до 6 соответствует CDEFGAB

VREF = 5.12  # Опорное значение напряжения
POWER = 3  # Значение уровня заряда 0-3
LOOPS = 0  # Параметр для циклической проверки
PS2_LOOPS = 0  # Параметр для циклической проверки

PROGRAM_ABLE = True  # Статус выполнения программы

LIGHT_STATUS = 0  # Статус фар
LIGHT_LAST_STATUS = 0  # Предыдущий статус фар
LIGHT_OPEN_STATUS = 0  # Статус включения фар
STOP = 1  # Статус остановки фар
TURN_FORWARD = 2  # Статус движения вперед для фар
TURN_BACK = 3  # Статус движения назад для фар
TURN_LEFT = 4  # Статус поворота налево для фар
TURN_RIGHT = 5  # Статус поворота направо для фар
POWER_LIGHT = 1  # Флаг для индикации уровня заряда
CAR_LIGHT = 2  # Флаг для фар автомобиля

# Установки цветов для RGB-светодиодов, доступны только эти цвета
COLOR = {'black': 0, 'red': 1, 'orange': 2, 'yellow': 3, 'green': 4, 'Cyan': 5,
		 'blue': 6, 'violet': 7, 'white': 8}

LOGO = "XiaoR GEEK"  # Информация, отображаемая на OLED-дисплее на английском
OLED_DISP_MOD = ["Нормальный режим", "Инфракрасное следование", "Инфракрасное отслеживание линии", "Инфракрасное предотвращение падения", "Ультразвуковое избегание препятствий",
				 "Отображение расстояния ультразвука", "Ультразвуковая навигация по лабиринту", "Камера отладки",
				 "Отслеживание линии камерой", "Распознавание лиц и следование", "Следование за цветом", "Распознавание QR-кода",
				 ]  # Режимы отображаются на китайском
OLED_DISP_MOD_SIZE = 16  # Один китайский иероглиф занимает 16 пикселей; если поменять шрифт на английский, значение нужно изменить на 8

BT_CLIENT = False  # Bluetooth-клиент
TCP_CLIENT = False  # TCP-клиент
RECV_LEN = 5  # Длина принимаемых символов

# Настройки для Bluetooth-сервера
BT_SERVER = socket(AF_INET, SOCK_STREAM)
BT_SERVER.bind(('', 2002))  # Привязка Bluetooth к порту 2002
BT_SERVER.listen(1)

# Настройки для TCP-сервера
TCP_SERVER = socket(AF_INET, SOCK_STREAM)
TCP_SERVER.bind(('', 2001))  # Привязка WiFi к порту 2002
TCP_SERVER.listen(1)

# Определения кнопок контроллера PS2
PS2_ABLE = False  # Флаг нормального подключения контроллера PS2
PS2_READ_KEY = 0  # Значение, считанное с контроллера PS2
PS2_LASTKEY = 0  # Значение, считанное с контроллера PS2 в предыдущий раз
PS2_KEY = {'PSB_PAD_UP': 1, 'PSB_PAD_DOWN': 2, 'PSB_PAD_LEFT': 3, 'PSB_PAD_RIGHT': 4,
'PSB_RED': 5, 'PSB_PINK': 6, 'PSB_GREEN': 7, 'PSB_BLUE': 8}  # Левый джойстик: вверх, вниз, влево, вправо, и кнопки функций справа

# Диапазоны цветов для функции следования за цветом
# Нижний порог диапазона цветов
COLOR_LOWER = [
	# Красный
	np.array([0, 43, 46]),
	# Зеленый
	np.array([35, 43, 46]),
	# Синий
	np.array([100, 43, 46]),
	# Фиолетовый
	np.array([125, 43, 46]),
	# Оранжевый
	np.array([11, 43, 46])
]
# Верхний порог диапазона цветов
COLOR_UPPER = [
	# Красный
	np.array([10, 255, 255]),
	# Зеленый
	np.array([77, 255, 255]),
	# Синий
	np.array([124, 255, 255]),
	# Фиолетовый
	np.array([155, 255, 255]),
	# Оранжевый
	np.array([25, 255, 255])
]
COLOR_FOLLOW_SET = {'red': 0, 'green': 1, 'blue': 2, 'violet': 3, 'orange': 4}  # Индексы цветовых диапазонов для функции следования, используются при сок
COLOR_INDEX = 0  # Индекс порога цветового диапазона, изменяется при сокетном соединении

BARCODE_DATE = None  # Данные распознавания QR-кода
BARCODE_TYPE = None  # Тип данных распознавания QR-кода