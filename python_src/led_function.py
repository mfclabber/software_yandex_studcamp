import xr_config as cfg

from xr_i2c import I2c
import time
i2c = I2c()

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

    # Все светодиоды горят красным (Обозначение команды)
    def red_team(self):
        self.set_ledgroup(cfg.CAR_LIGHT, 8, cfg.COLOR['red'])
    
    # Все светодиоды горят зеленым (Обозначение команды)
    def green_team(self):
        self.set_ledgroup(cfg.CAR_LIGHT, 8, cfg.COLOR['green'])

    #############################################
    #               Всякая хрень                #
    #############################################
    
    # Гейская тематика
    def rainbow(self, count):
        match count:
            case 1:
                for i in range(1,9):
                    self.set_led(cfg.POWER_LIGHT, i, cfg.COLOR[i])
                    time.sleep(0.1)
            case 2:
                for i in range(1,9):
                    self.set_led(cfg.CAR_LIGHT, i, cfg.COLOR[i])
                    time.sleep(0.12)
            case _:
                for i in range(1,9):
                    self.set_led(cfg.POWER_LIGHT, i, cfg.COLOR[i])
                    self.set_led(cfg.CAR_LIGHT, i, cfg.COLOR[i])
                    time.sleep(0.12)
    
    # Берегите глаза
    def epilepsy(self, count):
        match count:
            case 1:
                for i in range(1, 9):
                    if i % 2 == 0:
                        self.set_led(cfg.POWER_LIGHT, i, cfg.COLOR['white'])
                    else:
                        self.set_led(cfg.POWER_LIGHT, i, cfg.COLOR['black'])
                time.sleep(0.05)    
            case 2:
                for i in range(1, 9):
                    if i % 2 == 0:
                        self.set_led(cfg.POWER_LIGHT, i, cfg.COLOR['black'])
                    else:
                        self.set_led(cfg.POWER_LIGHT, i, cfg.COLOR['white'])
                time.sleep(0.05)