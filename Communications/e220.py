import serial
from gpiozero import DigitalOutputDevice, DigitalInputDevice
from constants import UART_BAUDRATE

class E220:
    def __init__(self, m0_pin, m1_pin, aux_pin, uart_port):
        self.m0 = DigitalOutputDevice(m0_pin)
        self.m1 = DigitalOutputDevice(m1_pin)
        self.aux = DigitalInputDevice(aux_pin)
        self.uart = serial.Serial(uart_port, baudrate=UART_BAUDRATE, timeout=1)

    def set_mode(self, mode):
        self.m0.value = mode[0]
        self.m1.value = mode[1]

    def send_data(self, data):
        """Send data which should be a bytes object"""
        self.uart.write(data)
    def sleep(self):
        self.set_mode((1, 1))  # Assuming sleep mode corresponds to (1, 1)

    def wake(self):
        self.set_mode((0, 0))  # Assuming normal mode corresponds to (0, 0)
