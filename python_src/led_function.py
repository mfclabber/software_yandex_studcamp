import xr_config as cfg

from xr_i2c import I2c
i2c = I2c()

from xr_power import Power
pw = Power()

import time


class LED():
    def init(self):
        pass

    ############################################
    #              Базовые функции             #
    ############################################

    # Выставление цвета для одного светодиода
    def set_led(self, group, num, color):
        if 0 < num < 9 and 0 < group < 3 and color < 9:
            buf = [0xff, group + 3, num, color, 0xff]
            i2c.writedata(i2c.mcu_address, buf)
            time.sleep(0.005)
    
    # Выставление цвета для группы светодиодов
    def set_ledgroup(self, group, count, color):
        if 0 < count < 9 and 0 < group < 3 and color < 9:
            buf = [0xff, group + 1, count, color, 0xff]
            i2c.writedata(i2c.mcu_address, buf)
            time.sleep(0.005)
    
    #############################################
    #               Цвета команды               #
    #############################################

    # Все светодиоды горят красным на первом леде (Обозначение команды)
    def red_team_first_led(self):
        self.set_ledgroup(cfg.POWER_LIGHT, 8, cfg.COLOR['red'])
    
    # Все светодиоды горят зеленым на первом леде (Обозначение команды)
    def green_team_first_led(self):
        self.set_ledgroup(cfg.POWER_LIGHT, 8, cfg.COLOR['green'])

    # Все светодиоды горят красным на втором леде (Обозначение команды)
    def red_team_second_led(self):
        self.set_ledgroup(cfg.CAR_LIGHT, 8, cfg.COLOR['red'])
    
    # Все светодиоды горят зеленым на втором леде (Обозначение команды)
    def green_team_second_led(self):
        self.set_ledgroup(cfg.CAR_LIGHT, 8, cfg.COLOR['green'])
    
    # Все светодиоды горят красным на обоих ледах (Обозначение команды)
    def red_team_both_led(self):
        self.set_ledgroup(cfg.POWER_LIGHT, 8, cfg.COLOR['red'])
        self.set_ledgroup(cfg.CAR_LIGHT, 8, cfg.COLOR['red'])

    # Все светодиоды горят зеленым на обоих ледах (Обозначение команды)
    def green_team_both_led(self):
        self.set_ledgroup(cfg.POWER_LIGHT, 8, cfg.COLOR['green'])
        self.set_ledgroup(cfg.CAR_LIGHT, 8, cfg.COLOR['green'])

    #############################################
    #          Индикация заряда банки           #
    #############################################

    def show_vol(self):
        vol = pw.got_vol()
        print(vol)
        # 70-100%
        if (417 < vol <= 430) or (835 < vol <= 860) or (1255 < vol <= 1290):  
            self.set_ledgroup(cfg.POWER_LIGHT, 8, cfg.COLOR['green'])
            cfg.POWER = 3		#
        elif (404 < vol <= 417) or (810 < vol <= 835) or (1220 < vol <= 1255):  
            self.set_ledgroup(cfg.POWER_LIGHT, 7, cfg.COLOR['green'])		
            cfg.POWER = 3		
        elif (391 < vol <= 404) or (785 < vol <= 810) or (1185 < vol <= 1220):
            self.set_ledgroup(cfg.POWER_LIGHT, 6, cfg.COLOR['green'])		
            cfg.POWER = 3
        # 30-70% 		
        elif (378 < vol <= 391) or (760 < vol <= 785) or (1150 < vol <= 1185):  	
            self.set_ledgroup(cfg.POWER_LIGHT, 5, cfg.COLOR['yellow'])
            cfg.POWER = 2		
        elif (365 < vol <= 378) or (735 < vol <= 760) or (1115 < vol <= 1150):  	
            self.set_ledgroup(cfg.POWER_LIGHT, 4, cfg.COLOR['yellow'])
            cfg.POWER = 2		
        elif (352 < vol <= 365) or (710 < vol <= 735) or (1080 < vol <= 1115):
            self.set_ledgroup(cfg.POWER_LIGHT, 3, cfg.COLOR['yellow'])
            cfg.POWER = 2
        # 10-30%		
        elif (340 < vol <= 352) or (680 < vol <= 710) or (1040 < vol <= 1080):
            self.set_ledgroup(cfg.POWER_LIGHT, 2, cfg.COLOR['red'])
            cfg.POWER = 1
        # <10%
        elif (vol <= 340) or (vol <= 680) or (vol <= 1040):
            self.set_ledgroup(cfg.POWER_LIGHT, 1, cfg.COLOR['red'])
            cfg.POWER = 0

    #############################################
    #             Отключение ледов              #
    #############################################

    def off_first_led(self):
        self.set_ledgroup(cfg.POWER_LIGHT, 8, cfg.COLOR['black'])

    def off_second_led(self):
        self.set_ledgroup(cfg.CAR_LIGHT, 8, cfg.COLOR['black'])
    
    def off_both_led(self):
        self.set_ledgroup(cfg.POWER_LIGHT, 8, cfg.COLOR['black'])
        self.set_ledgroup(cfg.CAR_LIGHT, 8, cfg.COLOR['black'])

    #############################################
    #               Всякая хрень                #
    #############################################
    
    # Гейская тематика
    def rainbow(self, count):
        match count:
            case 1:
                self.set_led(cfg.POWER_LIGHT, 1, cfg.COLOR[list(cfg.COLOR.keys())[1]])
                time.sleep(0.001)
                for i in range(2,9):
                    self.set_led(cfg.POWER_LIGHT, i-1, cfg.COLOR['black'])
                    self.set_led(cfg.POWER_LIGHT, i, cfg.COLOR[list(cfg.COLOR.keys())[i]])
                    time.sleep(0.001)
                self.set_led(cfg.POWER_LIGHT, 8, cfg.COLOR['black'])    
            case 2:
                self.set_led(cfg.CAR_LIGHT, 1, cfg.COLOR[list(cfg.COLOR.keys())[1]])
                time.sleep(1)
                for i in range(2,9):
                    self.set_led(cfg.CAR_LIGHT, i-1, cfg.COLOR['black'])
                    self.set_led(cfg.CAR_LIGHT, i, cfg.COLOR[list(cfg.COLOR.keys())[i]])
                    time.sleep(1)
                self.set_led(cfg.CAR_LIGHT, 8, cfg.COLOR['black'])
            case _:
                self.set_led(cfg.CAR_LIGHT, 1, cfg.COLOR[list(cfg.COLOR.keys())[1]])
                self.set_led(cfg.POWER_LIGHT, 1, cfg.COLOR[list(cfg.COLOR.keys())[1]])
                time.sleep(1)
                self.set_led(cfg.CAR_LIGHT, 1, cfg.COLOR['black'])
                self.set_led(cfg.POWER_LIGHT, 1, cfg.COLOR['black'])
                for i in range(2,9):
                    self.set_led(cfg.CAR_LIGHT, i-1, cfg.COLOR['black'])
                    self.set_led(cfg.POWER_LIGHT, i-1, cfg.COLOR['black'])
                    self.set_led(cfg.CAR_LIGHT, i, cfg.COLOR[list(cfg.COLOR.keys())[i]])
                    self.set_led(cfg.POWER_LIGHT, i, cfg.COLOR[list(cfg.COLOR.keys())[i]])
                    time.sleep(1)
                self.set_led(cfg.CAR_LIGHT, 8, cfg.COLOR['black'])    
                self.set_led(cfg.POWER_LIGHT, 8, cfg.COLOR['black'])
                
    
    # Берегите глаза
    def epilepsy(self, count):
        match count:
            case 1:
                for i in range(1, 9):
                    if i % 2 == 0:
                        self.set_led(cfg.POWER_LIGHT, i, cfg.COLOR['white'])
                    else:
                        self.set_led(cfg.POWER_LIGHT, i, cfg.COLOR['black'])
                time.sleep(0.0000000001)    
            case 2:
                for i in range(1, 9):
                    if i % 2 == 0:
                        self.set_led(cfg.POWER_LIGHT, i, cfg.COLOR['black'])
                    else:
                        self.set_led(cfg.POWER_LIGHT, i, cfg.COLOR['white'])
                time.sleep(0.0000000001)