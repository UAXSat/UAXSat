import os
import time
import json
import logging
import sys
import serial
from e220 import E220  # Asegúrate de que el módulo e220 está importado correctamente
from Software.Sensors.UVmodule import initialize_sensor as init_uv_sensor, read_sensor_data as read_uv_data
from Software.Sensors.GPSmodule import GPSHandler
from Software.Sensors.IMUmodule import initialize_sensor as init_icm_sensor, read_sensor_data as read_imu_data
from Software.Sensors.DS18B20module import DallasSensor
from Software.Sensors.BMPmodule import initialize_sensor as init_bmp_sensor, read_sensor_data as read_bmp_data
from gpiozero import CPUTemperature
from psutil import cpu_percent, virtual_memory

# Configuración de parámetros
BAUDRATE = 38400
TIMEOUT = 1
DESCRIPTION = "u-blox GNSS receiver"
HWID = "1546:01A9"
UART_PORT = '/dev/ttyUSB0'  # Cambia esto al puerto UART de tu módulo LoRa
SENSOR_READING_INTERVAL = 10  # Intervalo entre lecturas de sensores en segundos

# Configuración del registro
logging.basicConfig(filename='/home/cubesat/error.log', level=logging.DEBUG,
                    format='%(asctime)s: %(levelname)s: %(message)s')

# Inicializar el módulo LoRa
print("Initializing LoRa module...")
lora_module = E220(m0_pin=23, m1_pin=24, aux_pin=22, uart_port=UART_PORT)
lora_module.set_mode(MODE_NORMAL)  # Establecer el modo de operación

def read_sensors(gps_parser):
    latitude, longitude, altitude, headingMotion, roll, pitch, heading, nmea = read_gps_sensor(gps_parser)
    acceleration, gyro, magnetic = read_imu_sensor()
    uva, uvb, uvc, uv_temp = read_uv_sensor()

    readings = {
        "CPUTemperature": read_CPU(),
        "CPU Usage": read_CPU_usage(),
        "RAM Usage": read_RAM_usage(),
        "Latitude": latitude,
        "Longitude": longitude,
        "Altitude": altitude,
        "Heading of Motion": headingMotion,
        "Roll": roll,
        "Pitch": pitch,
        "Heading": heading,
        "NMEA Sentence": nmea,
        "Acceleration": acceleration,
        "Gyro": gyro,
        "Magnetic": magnetic,
        "UVA": uva,
        "UVB": uvb,
        "UVC": uvc,
        "UV Temp": uv_temp,
        "Temperature": read_dallas_sensor()
    }
    return prepare_sensor_data(readings)

def prepare_sensor_data(readings):
    sensors_data = {"Date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}
    for sensor, data in readings.items():
        if data:
            sensors_data[sensor] = data
        else:
            sensors_data[sensor] = "Error"
    return sensors_data

def read_gps_sensor(gps_reader):
    try:
        if not gps_reader.gps or not gps_reader.serial_port:
            logging.debug("Attempting to reconnect to GPS...")
            gps_reader = GPSHandler(BAUDRATE, TIMEOUT, description=DESCRIPTION, hwid=HWID)
            if not gps_reader.gps or not gps_reader.serial_port:
                log_status("GPS Sensor", "Disconnected")
                return (None, None, None, None, None, None, None, None)
        data = gps_reader.GPSprogram()
        if data:
            log_status("GPS Sensor", "OK")
            return data['Latitude'], data['Longitude'], data['Altitude'], data['Heading of Motion'], data['Roll'], data['Pitch'], data['Heading'], data['NMEA Sentence']
        else:
            log_status("GPS Sensor", "Disconnected")
            return (None, None, None, None, None, None, None, None)
    except Exception as e:
        log_status("GPS Sensor", "Disconnected")
        logging.error(f"Error reading GPS Sensor: {e}")
        return (None, None, None, None, None, None, None, None)

def send_data_lora(data):
    try:
        json_data = json.dumps(data, indent=4)  # Convertir a JSON
        print(f"Sending data: {json_data}")  # Imprimir para depuración
        lora_module.send_data(json_data)  # Enviar datos a través de LoRa
    except Exception as e:
        logging.error(f"Error sending data via LoRa: {e}")

if __name__ == "__main__":
    try:
        logging.info("Starting sensor data collection and transmission.")

        gps_parser = GPSHandler(BAUDRATE, TIMEOUT, description=DESCRIPTION, hwid=HWID)

        while True:
            logging.debug("Reading sensor data...")
            sensor_data = read_sensors(gps_parser)
            send_data_lora(sensor_data)
            time.sleep(SENSOR_READING_INTERVAL)  # Esperar antes de la siguiente lectura

    except KeyboardInterrupt:
        logging.info("Program stopped by the user.")
    except Exception as e:
        logging.error(f"Unexpected error while sending data: {e}")
