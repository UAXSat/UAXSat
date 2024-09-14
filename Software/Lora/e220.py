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
import logging
from gpiozero import DigitalOutputDevice, DigitalInputDevice
from serial.tools import list_ports
from constants import MODE_NORMAL, MODE_SLEEP, MODE_WOR_RECEIVE, MODE_WOR_TRANSMIT, VID_PID_LIST

# Setup logging
logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG level for more detailed logs
logger = logging.getLogger(__name__)

class E220:
    """
    This class handles communication with the E220 LoRa module, including mode configuration,
    sending, and receiving data over UART, as well as controlling the M0, M1, and AUX pins.
    """

    def __init__(self, m0_pin, m1_pin, aux_pin, uart_port):
        """
        Initialize the E220 LoRa module, set up GPIO pins, and open UART communication.
        :param m0_pin: GPIO pin number for M0
        :param m1_pin: GPIO pin number for M1
        :param aux_pin: GPIO pin number for AUX
        :param uart_port: The UART port for communication
        """
        logger.debug("Initializing E220 LoRa module.")
        self.m0 = DigitalOutputDevice(m0_pin)
        self.m1 = DigitalOutputDevice(m1_pin)
        self.aux = DigitalInputDevice(aux_pin)
        self.uart = serial.Serial(uart_port, baudrate=9600, timeout=3)

        # Set module to normal mode by default
        self.set_mode(MODE_NORMAL)

        # Ensure AUX pin is ready before proceeding
        self.wait_for_aux()

    def set_mode(self, mode):
        """
        Set the operation mode of the E220 module (Normal, WOR Transmit, WOR Receive, Sleep).
        :param mode: Tuple representing the mode (e.g., MODE_NORMAL, MODE_SLEEP)
        """
        logger.debug(f"Setting mode to {mode}.")
        self.m0.value = mode[0]
        self.m1.value = mode[1]
        self.wait_for_aux()

    def wait_for_aux(self):
        """
        Wait for the AUX pin to be high (indicating that the module is ready).
        """
        logger.debug("Waiting for AUX pin to be ready.")
        while not self.aux.value:
            time.sleep(0.1)
        logger.debug("AUX pin is ready.")

    def send_data(self, data):
        """
        Send data to the LoRa module over UART.
        :param data: The string data to be sent
        """
        logger.debug(f"Sending data: {data}")
        self.uart.write(data.encode('utf-8'))  # Send data as UTF-8 encoded string
        self.wait_for_aux()
        logger.debug("Data sent successfully.")

    def receive_data(self):
        """
        Receive data from the LoRa module over UART.
        :return: The string data received or None if no data is available
        """
        if self.uart.in_waiting > 0:
            data = self.uart.read(self.uart.in_waiting).decode('utf-8')  # Read and decode data
            logger.debug(f"Data received: {data}")
            return data
        return None

    def sleep(self):
        """
        Put the module in sleep mode to save power.
        """
        logger.debug("Putting the module in sleep mode.")
        self.set_mode(MODE_SLEEP)

    def wake(self):
        """
        Wake up the module from sleep mode and set it back to normal mode.
        """
        logger.debug("Waking up the module and setting it to normal mode.")
        self.set_mode(MODE_NORMAL)

    def close(self):
        """
        Close the UART communication and release resources.
        """
        logger.debug("Closing UART communication.")
        self.uart.close()

    @staticmethod
    def find_serial_port(vendor_id, product_id):
        """
        Find and return the serial port for a device with the given VID and PID.
        :param vendor_id: Vendor ID of the USB device
        :param product_id: Product ID of the USB device
        :return: The device's serial port (string) or None if not found
        """
        logger.debug(f"Searching for device with VID={vendor_id} and PID={product_id}.")
        ports = list_ports.comports()
        for port in ports:
            if port.vid == vendor_id and port.pid == product_id:
                logger.debug(f"Device found at port: {port.device}")
                return port.device
        logger.debug("Device not found.")
        return None
