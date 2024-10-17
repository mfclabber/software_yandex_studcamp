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

#led.red_team_both_led()
led.show_vol()
time.sleep(1)
# led.red_team_first_led()
#led.red_team_second_led()
led.off_both_led()

# while True:
#     pw.show_vol()
