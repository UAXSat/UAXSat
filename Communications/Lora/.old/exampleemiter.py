# example1.py
import time
from e220 import E220
from constants import MODE_NORMAL, UART_BAUDRATE

# Initialize E220 module with the correct parameters
lora_module = E220(m0_pin=23, m1_pin=24, aux_pin=22, uart_port='/dev/ttyUSB0')

# Set to normal operation
lora_module.set_mode(MODE_NORMAL)

# Send some data continuously
while True:
    data_to_send = "Hello, E220!"
    print(f"Sending data: {data_to_send}")
    lora_module.send_data(data_to_send)
    time.sleep(1)  # Pause for a second before sending the next message
