import serial
from e220 import E220
from constants import MODE_NORMAL, UART_BAUDRATE

# Setup UART
uart = serial.Serial('/dev/ttyUSB0', baudrate=UART_BAUDRATE)

# Initialize E220 module
lora_module = E220(m0_pin=23, m1_pin=24, aux_pin=22, uart=uart)

# Set to normal operation
lora_module.set_mode(MODE_NORMAL)

# Send some data
lora_module.send_data("Hello, E220!")

# Switch to sleep when done
lora_module.sleep()
