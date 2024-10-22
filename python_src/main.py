from server_camera_up import starting_server_and_client
from auto_coordination import Coordinator
from xr_ultrasonic import Ultrasonic

# low control mode
from test_move import RobotDirection
from ctrl_servo import CTRL_Servo

# control module
from control.follow2object import follow2cube

# different led mode
from led_function import LED



# initialization classes
led = LED()
servo = CTRL_Servo()
go = RobotDirection()
ult = Ultrasonic()

COLOR = "green"

if COLOR == "red":
    led.red_team_both_led()
else:
    led.green_team_both_led()


#try:

    #matrix_objects = list(starting_server_and_client())
    #matrix_objects.append(ult)
    #matrix_objects.append(go)

    #coordinator = Coordinator(*matrix_objects)
coordinator = Coordinator([[0,4]], 0, [[2,4]], [[0,2]], [[4,4]], [False,False], ult,go)


coordinator.first_moves()
coordinator.show_field()

coordinator.go_to_cube()
follow2cube()

coordinator.return_to_wall()

#except:
#    pass