# constants.py

import RPi.GPIO as GPIO

# Definiciones de pines GPIO
M0_PIN = 17
M1_PIN = 27
AUX_PIN = 22

initial_lat = 37.76922  # Latitud Inicial (Jaén)
initial_lon = -3.79028  # Longitud Final (Jaén)

# Configuración del puerto serial
SERIAL_PORT = '/dev/ttyUSB0'  # Ajusta según tu sistema
BAUD_RATE = 9600  # Debe coincidir con la configuración del módulo LoRa

# Inicializar GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(M0_PIN, GPIO.OUT)
GPIO.setup(M1_PIN, GPIO.OUT)
GPIO.setup(AUX_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)