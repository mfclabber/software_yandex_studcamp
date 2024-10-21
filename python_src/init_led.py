from builtins import bytes, int

import os
import time
import threading
from threading import Timer
from subprocess import call

from led_function import LED
led = LED()
from xr_power import Power
pw = Power()

# led.red_team_both_led()
# led.show_vol()
#

        #time.sleep(1)
#time.sleep(10)
#led.green_team_both_led()
#led.red_team_second_led()
led.red_team_both_led()
# led.off_both_led()
#led.rainbow(1)
# while True:
#     pw.show_vol()
