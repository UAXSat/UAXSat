import serial
import time
import logging
from gpiozero import DigitalOutputDevice, DigitalInputDevice

from constants import *
from lora_functions import *

# Configuración del logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Inicialización de los pines GPIO
m0 = DigitalOutputDevice(M0_PIN)
m1 = DigitalOutputDevice(M1_PIN)
aux = DigitalInputDevice(AUX_PIN, pull_up=True)

def receive_message():
    """Recibe mensajes a través de LoRa."""
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
        while True:
            if ser.in_waiting > 0:
                message = ser.readline()
                try:
                    decoded_message = message.decode('utf-8', errors='ignore').strip()
                    logger.info(f"Mensaje recibido: {decoded_message}")
                except UnicodeDecodeError as e:
                    logger.error(f"Error al decodificar el mensaje: {e}")
                    logger.debug(f"Mensaje en bruto: {message}")
                wait_aux_low()
                wait_aux_high()
            else:
                time.sleep(0.1)

def main():
    try:
        enter_normal_mode()
        receive_message()
    except KeyboardInterrupt:
        logger.info("Programa interrumpido por el usuario.")
    finally:
        logger.debug("Limpiando GPIO...")
        m0.close()
        m1.close()
        aux.close()
        logger.debug("GPIO limpiado.")

if __name__ == '__main__':
    main()
