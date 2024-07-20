import json
import sys
import time
import serial
from serial.tools import list_ports
from e220 import E220
from constants import MODE_NORMAL, UART_BAUDRATE
from datetime import datetime

sys.path.append('../')  # Permite importar módulos de la carpeta vecinos

# Importa los módulos para leer los sensores
from Sensors.UVmodule import initialize_sensor as init_uv_sensor, read_sensor_data as read_uv_data
from Sensors.GPS2 import GPSHandler
from Sensors.IMUmodule import initialize_sensor as init_icm_sensor, read_sensor_data as read_imu_data
from Sensors.DS18B20module import DallasSensor
from gpiozero import CPUTemperature
from psutil import cpu_percent, virtual_memory

# Parámetros para LoRa
vid = 0x10C4
pid = 0xEA60

def initialize_sensors():
    UV = init_uv_sensor()
    IMU = init_icm_sensor()
    DS = DallasSensor()
    GPS = GPSHandler(baudrate=38400, timeout=1, description=None, hwid="1546:01A9")
    return UV, IMU, DS, GPS

def collect_sensor_data(UV, IMU, DS, GPS):
    data = {}
    try:
        data['UV'] = read_uv_data(UV)
    except Exception as e:
        data['UV'] = None  # Cambiado para evitar enviar datos erróneos

    try:
        data['IMU'] = read_imu_data(IMU)
    except Exception as e:
        data['IMU'] = None

    try:
        data['DS18B20'] = DS.get_sensor_info()
    except Exception as e:
        data['DS18B20'] = None

    try:
        GPSdata = GPS.get_location()
        data['GPS'] = GPSdata if GPSdata else None
    except Exception as e:
        data['GPS'] = None

    data['CPU'] = {'Temperature': CPUTemperature().temperature, 'Usage': cpu_percent(interval=1)}
    data['RAM'] = {'Usage': virtual_memory().percent}

    return {k: v for k, v in data.items() if v is not None}  # Filtrar datos nulos

def send_data(lora_module, data):
    if data:  # Verifica que hay datos para enviar
        data_string = json.dumps(data, separators=(',', ':')) + "\n"  # Comprime el JSON
        print(f"Sending data: {data_string}")
        lora_module.send_data(data_string.encode('utf-8'))

def find_serial_port(vid=0x10C4, pid=0xEA60):
    ports = list_ports.comports()
    for port in ports:
        if port.vid == vid and port.pid == pid:
            return port.device
    return None

# Inicialización del módulo LoRa
uart_port = find_serial_port(vid, pid)
if uart_port is None:
    print("Device not found. Please check your connections.")
    sys.exit(1)

lora_module = E220(m0_pin=23, m1_pin=24, aux_pin=22, uart_port=uart_port)
lora_module.set_mode(MODE_NORMAL)

def main():
    UV, IMU, DS, GPS = initialize_sensors()
    interval = 5  # Intervalo de tiempo entre lecturas

    try:
        while True:
            data = collect_sensor_data(UV, IMU, DS, GPS)
            send_data(lora_module, data)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Program interrupted by user.")
    finally:
        if GPS.serial_port and GPS.serial_port.is_open:
            GPS.serial_port.close()
        print("GPS port closed and program terminated cleanly.")

if __name__ == '__main__':
    main()
