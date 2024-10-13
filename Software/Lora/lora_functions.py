# lora_functions.py

import RPi.GPIO as GPIO
import logging
import time
from constants import M0_PIN, M1_PIN, AUX_PIN

# Configuración del logger
logger = logging.getLogger(__name__)

def wait_aux_high():
    while GPIO.input(AUX_PIN) == GPIO.LOW:
        time.sleep(0.01)

def wait_aux_low():
    while GPIO.input(AUX_PIN) == GPIO.HIGH:
        time.sleep(0.01)

def enter_config_mode():
    GPIO.output(M0_PIN, GPIO.HIGH)
    GPIO.output(M1_PIN, GPIO.HIGH)
    wait_aux_high()
    time.sleep(0.1)
    logger.debug("Entered configuration mode.")

def enter_normal_mode():
    GPIO.output(M0_PIN, GPIO.LOW)
    GPIO.output(M1_PIN, GPIO.LOW)
    wait_aux_high()
    time.sleep(0.1)
    logger.debug("Entered normal mode.")