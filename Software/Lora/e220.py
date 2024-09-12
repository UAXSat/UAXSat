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

class E220:
    def __init__(self, m0_pin, m1_pin, aux_pin, uart_port):
        self.m0 = DigitalOutputDevice(m0_pin)
        self.m1 = DigitalOutputDevice(m1_pin)
        self.aux = DigitalInputDevice(aux_pin)
        self.uart = serial.Serial(uart_port, baudrate=UART_BAUDRATE, timeout=3)
        
        # Establecer el modo inicial a normal
        self.set_mode(MODE_NORMAL)
        
        # Esperar a que el m  dulo est   listo
        self.wait_for_aux()

    def set_mode(self, mode):
        """ Establece el modo del m  dulo E220 """
        self.m0.value = mode[0]
        self.m1.value = mode[1]
        self.wait_for_aux()  # Aseg  rate de que el m  dulo est   listo

    def wait_for_aux(self):
        """ Espera a que el pin AUX est   alto """
        while not self.aux.value:
            print("Esperando que el pin AUX est   alto...")
            time.sleep(0.1)  # Reduce el uso de CPU

    def send_data(self, data):
        """ Env  a datos a trav  s del puerto UART """
        self.uart.write(data.encode('utf-8'))
        self.wait_for_aux()  # Esperar hasta que AUX est   listo para el siguiente comando

    def receive_data(self):
        """ Recibe datos del puerto UART """
        if self.uart.in_waiting > 0:
            data = self.uart.read(self.uart.in_waiting).decode('utf-8')
            return data

    def sleep(self):
        """ Pone el m  dulo en modo de sue  o """
        self.set_mode(MODE_SLEEP)

    def wake(self):
        """ Despierta el m  dulo y lo pone en modo normal """
        self.set_mode(MODE_NORMAL)

    def close(self):
        """ Cierra el puerto UART """
        self.uart.close()
