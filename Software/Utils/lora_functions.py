"""- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - *

                         Developed by Javier Bolanos
                    https://github.com/javierbolanosllano

                           UAXSAT IV Project - 2024
                       https://github.com/UAXSat/UAXSat

* - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - """

# lora_functions.py
import RPi.GPIO as GPIO
import logging
import time
from constants import M0_PIN, M1_PIN, AUX_PIN

# Configuración del logger
logger = logging.getLogger(__name__)

def wait_aux_high():

    '''Wait for AUX pin to go high
    - Used to wait for a response from the module'''
    
    while GPIO.input(AUX_PIN) == GPIO.LOW:
        time.sleep(0.01)

def wait_aux_low():

    '''Wait for AUX pin to go low
    - Used to wait for a response from the module'''

    while GPIO.input(AUX_PIN) == GPIO.HIGH:
        time.sleep(0.01)

def enter_config_mode():

    '''Enter configuration mode
    - M0 = HIGH
    - M1 = HIGH'''

    GPIO.output(M0_PIN, GPIO.HIGH)
    GPIO.output(M1_PIN, GPIO.HIGH)
    wait_aux_high()
    time.sleep(0.1)
    logger.debug("Entered configuration mode.")

def enter_normal_mode():

    '''Enter normal mode:
    - M0 = LOW
    - M1 = LOW'''

    GPIO.output(M0_PIN, GPIO.LOW)
    GPIO.output(M1_PIN, GPIO.LOW)
    wait_aux_high()
    time.sleep(0.1)
    logger.debug("Entered normal mode.")