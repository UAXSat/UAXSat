"""*********************************************************************************************************
*                                                                                                          *
*                                     UAXSAT IV Project - 2024                                             *
*                       Developed by Javier Bolaños Llano and Javier Lendinez                              *
*                                https://github.com/UAXSat                                                 *
*                                                                                                          *
*********************************************************************************************************"""

import os
import time
import json
import csv
import logging

import sys
sys.path.append('/home/javil/UAXSat') # permite importar modulos de la carpeta vecinos

# Import the modules to read the sensors
from UAXSat.Software.RaspberryPi.UVmodule import initialize_sensor as init_uv_sensor, read_sensor_data as read_uv_data
from UAXSat.Software.RaspberryPi.GPSmodule import connect_gps, parse_nmea_sentence
from UAXSat.Software.RaspberryPi.GPSmodule_complicated import connect_gps as connect_gps_complicated, parse_nmea_sentence as parse_nmea_sentence_complicated
from UAXSat.Software.RaspberryPi.IMUmodule import initialize_sensor as init_icm_sensor, read_sensor_data as read_imu_data
from UAXSat.Software.RaspberryPi.DS18B20module import DallasSensor
from UAXSat.Software.RaspberryPi.BMPmodule import initialize_sensor as init_bmp_sensor, read_sensor_data as read_bmp_data
from gpiozero import CPUTemperature

# Importa el módulo para publicar mensajes MQTT
import paho.mqtt.publish as publish  

logging.basicConfig(filename='/home/javil/error.log', level=logging.DEBUG,
                    format='%(asctime)s: %(levelname)s: %(message)s')

def clear_screen():
    """Clears the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def log_status(sensor_name, status):
    """
    Prints the sensor status in the console with colors and logs it.

    Parameters:
    - sensor_name: Name of the sensor (string).
    - status: Sensor status ('OK' or 'Disconnected') (string).

    Uses colors for the console output:

    Green: 'OK'
    Red:  'Disconnected'
    """

    RED     = "\033[91m"
    GREEN   = "\033[92m"
    RESET   = "\033[0m"
    status_message = f"{sensor_name}: {status}"
    if status == "OK":
        print(f"{GREEN}{status_message}{RESET}", end=" | ")
        logging.info(status_message)
    else:
        print(f"{RED}{status_message}{RESET}", end=" | ")
        logging.warning(status_message)

## Functions to read the sensors
# UV Sensor
def read_uv_sensor():
    try:
        sensor = init_uv_sensor()
        uv_data = read_uv_data(sensor)
        log_status("UV Sensor", "OK")
        return uv_data
    except Exception as e:
        log_status("UV Sensor", "Disconnected")
        logging.error(f"Error reading UV Sensor: {e}")
        return None

# GPS Sensor
def read_gps_sensor():
    try:
        port, gps = connect_gps()
        data = None
        while not data:
            nmea_data = gps.stream_nmea().strip()
            for sentence in nmea_data.splitlines():
                data, error = parse_nmea_sentence(sentence)
                if data:
                    log_status("GPS Sensor", "OK")
                    return data['latitude'], data['longitude']
        log_status("GPS Sensor", "Disconnected")
    except Exception as e:
        log_status("GPS Sensor", "Disconnected")
        logging.error(f"Error reading GPS Sensor: {e}")
        return None
    
# GPS Sensor
def read_gpscomplicated_sensor():
    try:
        port, gps = connect_gps_complicated()
        data = None
        while not data:
            nmea_data = gps.stream_nmea().strip()
            for sentence in nmea_data.splitlines():
                data, error = parse_nmea_sentence_complicated(sentence)
                if data:
                    log_status("GPS Sensor", "OK")
                    return data
        log_status("GPS Sensor", "Disconnected")
    except Exception as e:
        log_status("GPS Sensor", "Disconnected")
        logging.error(f"Error reading GPS Sensor: {e}")
        return None

# ICM20948 Sensor
def read_imu_sensor():
    try:
        sensor = init_icm_sensor()
        sensor_data = read_imu_data(sensor)
        log_status("IMU Sensor", "OK")
        return sensor_data
    except Exception as e:
        log_status("IMU Sensor", "Disconnected")
        logging.error(f"Error reading IMU Sensor: {e}")
        return None

# Dallas Sensor
def read_dallas_sensor():
    try:
        sensor = DallasSensor()
        sensor_info = sensor.get_sensor_info()
        if sensor_info:
            log_status("DallasSensor", "OK")
            return sensor_info
        else:
            log_status("DallasSensor", "Disconnected")
            return None
    except Exception as e:
        log_status("DallasSensor", "Disconnected")
        logging.error(f"Error reading Dallas Sensor: {e}")
        return None

# BMP3XX Sensor
def read_bmp3xx_sensor():
    try:
        sensor = init_bmp_sensor()
        sensor_data = read_bmp_data(sensor)
        log_status("BMP3XX", "OK")
        return sensor_data
    except Exception as e:
        log_status("BMP3XX", "Disconnected")
        logging.error(f"Error reading Dallas Sensor: {e}")
        return None

# CPU Temperature
def read_CPU():
    """Lee las temperaturas de varios sensores."""
    try:
        cpu = CPUTemperature().temperature
        log_status("CPUTemperature", "OK")
        return cpu
    except Exception as e:
        log_status("CPUTemperature", "Err")
        logging.error(f"Error reading CPU Temperature: {e}")
        return None

## Prepare the data to be sent
def prepare_sensor_data(readings):
    sensors_data = {"Date": time.strftime("%H:%M:%S", time.localtime())}
    for sensor, data in readings.items():
        sensors_data[sensor] = data if data else "Error"
    return sensors_data

## Read all the sensors
def read_sensors():
    latitude, longitude = read_gps_sensor()
    readings = {
        "latitude": latitude,
        "longitude": longitude,
        "UV Sensor": read_uv_sensor(),
        "ICM20948": read_imu_sensor(),
        "DallasSensor": read_dallas_sensor(),
        "BMP3XX": read_bmp3xx_sensor(),
        "CPUTemp": read_CPU(),
        "GPS Sensor": read_gpscomplicated_sensor(),
    }
    return prepare_sensor_data(readings)

## Save the data to a CSV file
def save_json_to_csv(json_data, csv_file_path):
    # Parse the JSON data
    data = json.loads(json_data)

    # Check if the CSV file already exists
    file_exists = os.path.isfile(csv_file_path)

    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.writer(file)

        # If the file doesn't exist, write the header
        if not file_exists:
            header = data.keys()
            writer.writerow(header)

        # Write the data
        writer.writerow(data.values())


## MQTT Configuration and interval between sensor readings
hostname_mqtt = "localhost"
sensorReadingInterval = 2

# Path to save the CSV file
csv_file_path = "/home/javil/sensor_data.csv"

if __name__ == "__main__":
    try:
        while True:
            clear_screen()
            sensor_data = read_sensors()
            sensorDataJSON = json.dumps(read_sensors())

            if sensorDataJSON:
                # Publish the data via MQTT
                publish.single("data", sensorDataJSON, hostname=hostname_mqtt)
                print("Data sent successfully.")

                # Save the JSON data to CSV
                save_json_to_csv(sensorDataJSON, csv_file_path)
                print("Data saved to CSV successfully.")
            else:
                print("Error sending data.")

            time.sleep(sensorReadingInterval)
    except KeyboardInterrupt:
        print("\n Program stopped by the user.")
    except Exception as e:
        print(f"Unexpected error while publishing data: {e}")

