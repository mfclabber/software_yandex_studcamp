import threading
import subprocess

from led_function import LED
led = LED()

# Функция для запуска первого скрипта
def run_script_1():
    subprocess.run(['python3', 'BUZZER.py'])

# Функция для запуска второго скрипта
def run_script_2():
    subprocess.run(['python3', 'init_led.py'])

# Создание потоков
thread1 = threading.Thread(target=run_script_1)
thread2 = threading.Thread(target=run_script_2)

# Запуск потоков
thread1.start()
thread2.start()

# Ожидание завершения обоих потоков
thread1.join()
thread2.join()

led.off_both_led()

print("Оба скрипта завершили работу.")