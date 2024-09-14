"""* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
*                                                                            *
*                         Developed by Javier Bolanos                        *
*                  https://github.com/javierbolanosllano                     *
*                                                                            *
*                      UAXSAT IV Project - 2024                              *
*                   https://github.com/UAXSat/UAXSat                         *
*                                                                            *
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *"""

# e220.py
import serial
import time
from gpiozero import DigitalOutputDevice, DigitalInputDevice
import logging

# CONSTANTS
M0 = 17     # GPIO 17
M1 = 27     # GPIO 27
AUX = 22    # GPIO 22

# Define operating modes
MODE_NORMAL = (0, 0)
MODE_WOR_TRANSMIT = (0, 1)
MODE_WOR_RECEIVE = (1, 0)
MODE_SLEEP = (1, 1)

# Specify your devices' VID and PID
VID_PID_LIST = [
    (0x10C4, 0xEA60),  # Device 1 VID and PID
    (0x1A86, 0x7523)   # Device 2 VID and PID
]

# UART and other configurations
UART_BAUDRATE = 9600

# Configuración del logger
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

class E220:
    def __init__(self, m0_pin, m1_pin, aux_pin, uart_port):
        logger.debug(f"Inicializando el módulo E220 en el puerto UART {uart_port}...")
        
        self.m0 = DigitalOutputDevice(m0_pin)
        self.m1 = DigitalOutputDevice(m1_pin)
        self.aux = DigitalInputDevice(aux_pin)

        try:
            self.uart = serial.Serial(uart_port, baudrate=UART_BAUDRATE, timeout=3)
            logger.debug(f"Puerto UART {uart_port} abierto con éxito.")
        except serial.SerialException as e:
            logger.error(f"Error al abrir el puerto UART {uart_port}: {e}")
            raise e
        
        # Establecer el modo inicial a normal
        self.set_mode(MODE_NORMAL)
        
        # Esperar a que el módulo esté listo
        self.wait_for_aux()

    def set_mode(self, mode):
        """ Establece el modo del módulo E220 """
        logger.debug(f"Estableciendo modo {mode} (M0={mode[0]}, M1={mode[1]})...")
        self.m0.value = mode[0]
        self.m1.value = mode[1]
        self.wait_for_aux()  # Asegúrate de que el módulo esté listo
        logger.info(f"Modo {mode} establecido correctamente.")

    def wait_for_aux(self):
        """ Espera a que el pin AUX esté alto """
        logger.debug("Esperando a que AUX esté listo...")
        while not self.aux.value:
            logger.debug("Pin AUX aún bajo, esperando...")
            time.sleep(0.1)  # Reduce el uso de CPU
        logger.debug("Pin AUX está alto, módulo listo.")

    def send_data(self, data):
        """ Envía datos a través del puerto UART """
        logger.debug(f"Enviando datos: {data}")
        try:
            self.uart.write(data.encode('utf-8'))
            self.wait_for_aux()  # Esperar hasta que AUX esté listo para el siguiente comando
            logger.info("Datos enviados correctamente.")
        except serial.SerialTimeoutException as e:
            logger.error(f"Error de timeout al enviar datos: {e}")
        except Exception as e:
            logger.error(f"Error inesperado al enviar datos: {e}")

    def receive_data(self):
        """ Recibe datos del puerto UART """
        logger.debug(f"Bytes esperando en UART: {self.uart.in_waiting}")
        
        if self.uart.in_waiting > 0:
            logger.debug(f"Bytes disponibles para lectura: {self.uart.in_waiting}")
            try:
                data = self.uart.read(self.uart.in_waiting).decode('utf-8')
                logger.info(f"Datos recibidos: {data}")
                return data
            except serial.SerialException as e:
                logger.error(f"Error al leer desde UART: {e}")
                return None
        else:
            logger.debug("No hay datos disponibles en el buffer UART.")
            return None

    def sleep(self):
        """ Pone el módulo en modo de sueño """
        logger.debug("Poniendo el módulo en modo SLEEP...")
        self.set_mode(MODE_SLEEP)

    def wake(self):
        """ Despierta el módulo y lo pone en modo normal """
        logger.debug("Despertando el módulo al modo NORMAL...")
        self.set_mode(MODE_NORMAL)

    def close(self):
        """ Cierra el puerto UART """
        logger.debug(f"Cerrando el puerto UART {self.uart.port}...")
        self.uart.close()
        logger.info(f"Puerto UART {self.uart.port} cerrado correctamente.")
