import time
import serial
from serial.tools import list_ports
from e220 import E220
from constants import MODE_NORMAL
import json

def find_serial_port(vid, pid):
    ports = list_ports.comports()
    for port in ports:
        if port.vid == vid and port.pid == pid:
            return port.device
    return None

def extract_json_objects(buffer):
    json_objects = []
    temp_buffer = buffer
    while True:
        newline_index = temp_buffer.find('\n')
        if newline_index == -1:
            break
        json_str = temp_buffer[:newline_index].strip()
        temp_buffer = temp_buffer[newline_index + 1:]
        try:
            json_obj = json.loads(json_str)
            json_objects.append(json_obj)
        except json.JSONDecodeError as e:
            print(f"JSONDecodeError: {e} - Buffer: {json_str}")
    return json_objects, temp_buffer

VID = 0x10C4
PID = 0xEA60
uart_port = find_serial_port(VID, PID)
if uart_port is None:
    print("Device not found. Please check your connections.")
    exit(1)

print(f"Device found at {uart_port}, initializing E220 module...")
lora_module = E220(m0_pin=23, m1_pin=24, aux_pin=22, uart_port=uart_port)
lora_module.set_mode(MODE_NORMAL)

buffer = ""
print("Waiting to receive data...")
while True:
    data = lora_module.receive_data()
    if data:
        buffer += data  # data ya es una cadena de texto, a  adir directamente al buffer
        json_objects, buffer = extract_json_objects(buffer)
        for json_obj in json_objects:
            print("Complete data received:", json_obj)

    time.sleep(0.1)  # Ajusta el temporizador seg  n sea necesario basado en la tasa de datos y la capacidad del dispositivo



