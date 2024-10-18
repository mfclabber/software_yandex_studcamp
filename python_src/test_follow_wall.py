from xr_ultrasonic import Ultrasonic
from test_move import RobotDirection
import time

def follow_wall(dist,s):
    go = RobotDirection()
    ul = Ultrasonic()
    dt = 0.1
    n = 5
    kp = 2
    kd = 1.5
    speed = 70
    angle_lim = 30

    arr = [ul.get_distance() for i in range(n)]
    m = sum(arr)/n

    if s=="l":
        ul.rotate_sensor_l()
    else:
        ul.rotate_sensor_r()
        kp = -kp
        kd = -kd

    while True:
        go.forward_with_angle(speed,0)
        time.sleep(dt)
        arr.append(ul.get_distance())
        m += arr[-1]/n
        m -= arr.pop(0)/n
        if m < dist:
            break
    
    print("Wall is found!")

    go.stop()
    arr = [ul.get_distance() for i in range(n)]
    m = sum(arr)/n
    diff = [arr[i+1]-arr[i] for i in range(n-1)]
    diff.append (diff[-1])
    m_d = sum(diff)/n

    flag1, flag2 = 0,0
    sign = 1
    change_state = 0
    while True:#(abs(m_d)<30):
        error_correct = (dist-m)*kp+m_d*kd
        err = max(-angle_lim, min(error_correct,angle_lim))

        if m>50 and flag1==0:
            flag1 = 1
        if m<=50 and flag1==1:
            flag1 = 0
        if flag1 != flag2:
            change_state +=1
            flag1=flag2
        if change_state % 4 == 0:
            sign = sign*-1

        go.forward_with_angle(speed,err*sign)
        print("angle:", round(err),"dist:",m )
        new_d = ul.get_distance()
        if new_d == -1:
            pass
        arr.append(new_d)
        m += arr[-1]/n
        m -= arr.pop(0)/n
        diff.append(arr[-1]-arr[-2])
        m_d += diff[-1]/n
        m_d -= diff.pop(0)/n
    go.stop()
    print(m_d, m)
    print(arr, diff)
    print("stopped")

follow_wall(25, 'r')
