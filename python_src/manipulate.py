import numpy as np
# from roboticstoolbox import DHRobot, RevoluteDH
# from spatialmath import SE3
from xr_servo import Servo

def coordinate (x, y, z):
    # Определяем параметры Денавита-Хартенберга для каждого звена
    link1 = RevoluteDH(a=0.053, alpha=0, d=0.5)   # первое звено
    link2 = RevoluteDH(a=0.095, alpha=0, d=0)   # второе звено
    link3 = RevoluteDH(a=0.04, alpha=0, d=0)   # третье звено

    # Создаем модель манипулятора
    robot = DHRobot([link1, link2, link3], name='3-DOF Robot')

    # Выводим параметры манипулятора
    #print(robot)

    # Задаем целевую позицию (гомогенная матрица трансформации) для нахождения обратной кинематики
    T = SE3(x, y, z)  # целевая позиция

    # Находим решение обратной кинематики
    sol = robot.ikine_LM(T)
    return list(sol)

# angle_servo = coordinate(1, 1, 0.5)[0]
# for i in range(len(angle_servo)):
#     servo.set(i+1, x[i])
#     print(x[i])\

servo = Servo()

for num in range(1, 5):
    servo.set(num, 10)