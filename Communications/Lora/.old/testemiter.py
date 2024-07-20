import time
import serial
from serial.tools import list_ports
from e220 import E220
from constants import MODE_NORMAL, UART_BAUDRATE

def find_serial_port(VID=0x10C4, PID=0xEA60):
    """ Find and return the serial port for a device with the given VID and PID. """
    ports = list_ports.comports()
    for port in ports:
        if port.vid == VID and port.pid == PID:
            return port.device
    return None

# Find the serial port automatically
VID, PID = 0x10C4, 0xEA60  # Adjust these values based on your device's specifications
uart_port = find_serial_port(VID, PID)
if uart_port is None:
    print("Device not found. Please check your connections.")
    exit(1)

print(f"Device found at {uart_port}, initializing E220 module...")
lora_module = E220(m0_pin=23, m1_pin=24, aux_pin=22, uart_port=uart_port)

# Set to normal operation
lora_module.set_mode(MODE_NORMAL)
print("Setting module to normal operation mode...")

while True:  # Infinite loop for sending messages
    try:
        with open('latest_sensor_data.txt', 'r') as file:
            data_to_send = file.read()
    except FileNotFoundError:
        print("Waiting for data file...")
        time.sleep(1)
        continue
    
    print(f"Sending data: {data_to_send}")
    lora_module.send_data(data_to_send)
    time.sleep(1)  # Adjust the timing based on your requirements
