"""- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - *

                         Developed by Javier Bolanos
                    https://github.com/javierbolanosllano

                           UAXSAT IV Project - 2024
                       https://github.com/UAXSat/UAXSat

* - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - """

#!/usr/bin/env python3

# E220900T30D.py
import serial
import time
import logging
import RPi.GPIO as GPIO
import sys
import os

# Agregar la carpeta anterior (/home/cubesat/UAXSat/Software/Lora) al sys.path
sys.path.append("/home/cubesat/UAXSat/Software/Lora")

# Ahora puedes importar el módulo lora_functions
from Utils.lora_functions import wait_aux_high, wait_aux_low, enter_config_mode, enter_normal_mode

# Logger configuration
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# GPIO Pins definition
M0_PIN = 17
M1_PIN = 27
AUX_PIN = 22

# Serial port configuration
SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(M0_PIN, GPIO.OUT)
GPIO.setup(M1_PIN, GPIO.OUT)
GPIO.setup(AUX_PIN, GPIO.IN)

def send_at_command(command):
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
        logger.debug(f"Sending command: {command}")
        ser.write(command.encode('utf-8'))
        wait_aux_low()
        wait_aux_high()
        response = ser.read(ser.in_waiting)
        try:
            return response.decode('utf-8')
        except UnicodeDecodeError:
            return response

def setparam(baudrate=9600, parity='8N1', air_rate=2400, power=30, packet_size=200, channel=18, wor_cycle=2000, lbt=False, rssi=True, address=0, key=0):
    enter_config_mode()

    baudrate_mapping = {1200: '00', 2400: '01', 4800: '02', 9600: '03', 19200: '04', 38400: '05', 57600: '06', 115200: '07'}
    parity_mapping = {'8N1': '00', '8O1': '01', '8E1': '10'}
    air_rate_mapping = {2400: '00', 4800: '01', 9600: '02', 19200: '03', 38400: '04', 62500: '05'}
    power_mapping = {30: '00', 27: '01', 24: '10', 21: '11'}
    packet_size_mapping = {200: '00', 128: '01', 64: '10', 32: '11'}
    wor_cycle_mapping = {500: '00', 1000: '01', 1500: '02', 2000: '03', 2500: '04', 3000: '05', 3500: '06', 4000: '07'}

    baudrate_code = baudrate_mapping.get(baudrate, '03')
    parity_code = parity_mapping.get(parity, '00')
    air_rate_code = air_rate_mapping.get(air_rate, '00')
    power_code = power_mapping.get(power, '00')
    packet_size_code = packet_size_mapping.get(packet_size, '00')
    wor_cycle_code = wor_cycle_mapping.get(wor_cycle, '03')
    lbt_code = '1' if lbt else '0'
    rssi_code = '1' if rssi else '0'
    address_code = f"{address:04X}"
    channel_code = f"{channel:02X}"
    key_code = f"{key:04X}"

    command = f'C0 00 08 {baudrate_code}{parity_code}{air_rate_code}{power_code}{packet_size_code}{channel_code} {wor_cycle_code}{lbt_code}{rssi_code}{address_code}{key_code}'
    
    send_at_command(command)
    logger.info(f"Set parameters: baudrate: {baudrate}, parity: {parity}, air_rate: {air_rate}, power: {power}, packet_size: {packet_size}, channel: {channel}, wor_cycle: {wor_cycle}, LBT: {lbt}, RSSI: {rssi}, address: {address}, key: {key}")

    enter_normal_mode()

def send_message(message):
    message_with_delimiter = message + "\n"
    logger.info(f"Enviando mensaje: {message_with_delimiter.strip()}")
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
            time.sleep(0.1)
            ser.write(message_with_delimiter.encode('utf-8'))
            wait_aux_low()
            wait_aux_high()
        logger.info("Mensaje enviado con éxito.")
    except serial.SerialException as e:
        logger.error(f"Error al enviar el mensaje: {e}")

def receive_message():
    logger.info("Esperando mensajes...")
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
        while True:
            if ser.in_waiting > 0:
                message = ser.readline()
                try:
                    decoded_message = message.decode('utf-8', errors='ignore').strip()
                    logger.info(f"Mensaje recibido: {decoded_message}")
                    return decoded_message
                except UnicodeDecodeError as e:
                    logger.error(f"Error al decodificar el mensaje: {e}")
                    logger.debug(f"Mensaje en bruto: {message}")
                wait_aux_low()
                wait_aux_high()
            else:
                time.sleep(0.1)


def clean_gpio():
    logger.debug("Limpiando GPIO...")
    GPIO.cleanup()
    logger.debug("GPIO limpiado.")