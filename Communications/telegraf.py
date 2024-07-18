#!/usr/bin/env python3
import time
import logging
import os
import sys
from Sensors.UVmodule import initialize_sensor as init_uv_sensor, read_sensor_data as read_uv_data
from Sensors.GPSmodule import GPSParser
from Sensors.IMUmodule import initialize_sensor as init_icm_sensor, read_sensor_data as read_imu_data
from Sensors.DS18B20module import DallasSensor
from gpiozero import CPUTemperature
from psutil import cpu_percent, virtual_memory

sys.path.append('../')  # Permite importar módulos de la carpeta vecinos

# GPS parameters
BAUDRATE = 38400
TIMEOUT = 1
DESCRIPTION = "u-blox GNSS receiver"
HWID = "1546:01A9"

# Logging configuration
logging.basicConfig(filename='/home/cubesat/error.log', level=logging.DEBUG,
                    format='%(asctime)s: %(levelname)s: %(message)s')

def log_status(sensor, status):
    logging.info(f"{sensor}: {status}")

## Functions to read the sensors
def read_uv_sensor():
    try:
        sensor = init_uv_sensor()
        data = read_uv_data(sensor)
        log_status("UV Sensor", "OK")
        return data
    except Exception as e:
        log_status("UV Sensor", "Disconnected")
        logging.error(f"Error reading UV Sensor: {e}")
        return None

def read_imu_sensor():
    try:
        sensor = init_icm_sensor()
        data = read_imu_data(sensor)
        log_status("IMU Sensor", "OK")
        return data
    except Exception as e:
        log_status("IMU Sensor", "Disconnected")
        logging.error(f"Error reading IMU Sensor: {e}")
        return None

def read_dallas_sensor():
    try:
        sensor = DallasSensor()
        sensor_info = sensor.get_sensor_info()
        if sensor_info:
            log_status("DallasSensor", "OK")
            return {"Temperature": sensor_info}
        else:
            log_status("DallasSensor", "Disconnected")
            return None
    except Exception as e:
        log_status("DallasSensor", "Disconnected")
        logging.error(f"Error reading Dallas Sensor: {e}")
        return None

def read_CPU():
    try:
        cpu = CPUTemperature().temperature
        log_status("CPUTemperature", "OK")
        return {"Temperature": cpu}
    except Exception as e:
        log_status("CPUTemperature", "Disconnected")
        logging.error(f"Error reading CPU Temperature: {e}")
        return None

def read_CPU_usage():
    try:
        cpu = cpu_percent(interval=1)
        log_status("CPU Usage", "OK")
        return {"Usage": cpu}
    except Exception as e:
        log_status("CPU Usage", "Disconnected")
        logging.error(f"Error reading CPU Usage: {e}")
        return None

def read_RAM_usage():
    try:
        ram = virtual_memory().percent
        log_status("RAM Usage", "OK")
        return {"Usage": ram}
    except Exception as e:
        log_status("RAM Usage", "Disconnected")
        logging.error(f"Error reading RAM Usage: {e}")
        return None

def read_gps_sensor(gps_parser):
    try:
        if not gps_parser.gps or not gps_parser.serial_port:
            logging.debug("Attempting to reconnect to GPS...")
            gps_parser = GPSParser(BAUDRATE, TIMEOUT, description=DESCRIPTION, hwid=HWID)
            if not gps_parser.gps or not gps_parser.serial_port:
                log_status("GPS Sensor", "Disconnected")
                return None

        nmea_data = gps_parser.read_nmea_data()
        if nmea_data:
            extracted_data = gps_parser.extract_relevant_data(nmea_data)
            log_status("GPS Sensor", "OK")
            return extracted_data
        else:
            log_status("GPS Sensor", "Disconnected")
            return None
    except Exception as e:
        log_status("GPS Sensor", "Disconnected")
        logging.error(f"Error reading GPS Sensor: {e}")
        return None

def read_sensors(gps_parser):
    readings = {
        "CPUTemp": read_CPU(),
        "CPUUsage": read_CPU_usage(),
        "RAMUsage": read_RAM_usage(),
        "GPS": read_gps_sensor(gps_parser),
        "IMU": read_imu_sensor(),
        "UV": read_uv_sensor(),
        "DallasTemp": read_dallas_sensor(),
    }
    return readings

def format_for_influx(measurement, fields, tags=None):
    field_strings = [f"{key}={value}" for key, value in fields.items()]
    field_set = ",".join(field_strings)
    if tags:
        tag_strings = [f"{key}={value}" for key, value in tags.items()]
        tag_set = ",".join(tag_strings)
        return f"{measurement},{tag_set} {field_set}"
    else:
        return f"{measurement} {field_set}"

if __name__ == "__main__":
    gps_parser = GPSParser(BAUDRATE, TIMEOUT, description=DESCRIPTION, hwid=HWID)
    while True:
        sensor_readings = read_sensors(gps_parser)

        influx_lines = []
        for sensor, data in sensor_readings.items():
            if data:
                for key, value in data.items():
                    influx_line = format_for_influx(sensor, {key: value})
                    influx_lines.append(influx_line)

        for line in influx_lines:
            print(line)
 
        # Esperar 10 segundos antes de la próxima lectura
        time.sleep(5)
