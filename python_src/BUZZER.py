import RPi.GPIO as GPIO
import time

# Пины
BUZZER_PIN = 10  # Пин для подключения к пьезоэлементу

# Настройка GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# Создание PWM объекта для управления частотой пьезоэлемента
buzzer = GPIO.PWM(BUZZER_PIN, 440)  # Начальная частота

# Функция для воспроизведения тона
def play_tone(frequency, duration):
    buzzer.ChangeFrequency(frequency)
    buzzer.start(50)  # 50% duty cycle
    time.sleep(duration)
    buzzer.stop()

notes = {
    'c1':261,
    'd1':293,
    'e1':330,
    'f1':350,
    'g1':392,
    'a1b':415,
    'a1':440,
    'b1':493,
    'c2':523,
    'd2':587,
    'e2':660,
    'f2':700
}


melody = [
    ('a1', 0.5), ('a1', 0.5), ('a1', 0.5),
    ('f1', 0.75/2), ('c2', 0.25/2), ('a1', 0.5),
    ('f1', 0.75/2), ('c2', 0.25/2), ('a1', 1),

    ('e2', 0.5), ('e2', 0.5), ('e2', 0.5),
    ('f2', 0.75/2), ('c2', 0.25/2), ('a1b', 0.5),
    ('f1', 0.75/2), ('c2', 0.25/2), ('a1', 1),
]

# notes = {
#     'C4': 261,
#     'D4': 294,
#     'E4': 329,
#     'F4': 349,
#     'G4': 392,
#     'A4': 440,
#     'B4': 494,
#     'C5': 523,
#     'D5': 587,
#     'E5': 659,
#     'F5': 698,
#     'G5': 784,
# }

# melody = [
#        ('E4', 0.5), ('E4', 0.5), ('E4', 0.5), ('E4', 0.5)
#    ]
# Воспроизведение мелодии
try:
    for note in melody:
        n, duration = note
        frequency = notes[n]
        play_tone(frequency, duration)
        time.sleep(0.1)  # Пауза между нотами

finally:
    GPIO.cleanup()  # Чистим настройки GPIO после выполнения программы

