import serial
import time
import logging
from gpiozero import DigitalOutputDevice, DigitalInputDevice

# Configuración del logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Definición de pines GPIO
M0_PIN = 17
M1_PIN = 27
AUX_PIN = 22

# Configuración del puerto serial
SERIAL_PORT = '/dev/ttyUSB0'  # Ajusta según tu sistema
BAUD_RATE = 9600  # Debe coincidir con la configuración del módulo LoRa

# Inicialización de los pines GPIO
m0 = DigitalOutputDevice(M0_PIN)
m1 = DigitalOutputDevice(M1_PIN)
aux = DigitalInputDevice(AUX_PIN, pull_up=True)

def wait_aux_high():
    """Espera hasta que el pin AUX esté en HIGH."""
    logger.debug("Esperando a que AUX esté en HIGH...")
    while not aux.value:
        time.sleep(0.01)
    logger.debug("AUX está en HIGH.")

def wait_aux_low():
    """Espera hasta que el pin AUX esté en LOW."""
    logger.debug("Esperando a que AUX esté en LOW...")
    while aux.value:
        time.sleep(0.01)
    logger.debug("AUX está en LOW.")

def enter_normal_mode():
    """Configura el módulo LoRa en modo normal (transparente)."""
    logger.debug("Configurando el módulo en modo NORMAL...")
    m0.off()
    m1.off()
    wait_aux_high()
    time.sleep(0.1)
    logger.debug("Módulo configurado en modo NORMAL.")

def receive_message():
    """Recibe mensajes a través de LoRa."""
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
        while True:
            if ser.in_waiting > 0:
                message = ser.readline()
                try:
                    decoded_message = message.decode('utf-8', errors='replace').strip()
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
