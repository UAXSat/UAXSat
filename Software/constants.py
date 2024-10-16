"""- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - *

                         Developed by Javier Bolanos
                    https://github.com/javierbolanosllano

                           UAXSAT IV Project - 2024
                       https://github.com/UAXSat/UAXSat

* - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - """

# constants.py
import RPi.GPIO as GPIO

# Definiciones de pines GPIO
M0_PIN = 17
M1_PIN = 27
AUX_PIN = 22

initial_lat = 37.76922  # Latitud Inicial (Jaén)
initial_lon = -3.79028  # Longitud Final (Jaén)

# Configuración del puerto UART para el módulo LoRa
SERIAL_PORT = '/dev/ttyAMA0'  # UART port LoRa Module
BAUD_RATE = 9600  # Debe coincidir con la configuración del módulo LoRa

# Inicializar GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(M0_PIN, GPIO.OUT)
GPIO.setup(M1_PIN, GPIO.OUT)
GPIO.setup(AUX_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
