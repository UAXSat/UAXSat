import os
import time
import json
import csv
import logging

import sys
sys.path.append('../')  # Permite importar modulos de la carpeta vecinos

# Import the modules to read the sensors
from Sensors.UVmodule import initialize_sensor as init_uv_sensor, read_sensor_data as read_uv_data
from Sensors.GPSmodule import GPSParser  # Asegúrate de que GPSParser esté importado correctamente
from Sensors.IMUmodule import initialize_sensor as init_icm_sensor, read_sensor_data as read_imu_data
from Sensors.DS18B20module import DallasSensor
from Sensors.BMPmodule import initialize_sensor as init_bmp_sensor, read_sensor_data as read_bmp_data
from gpiozero import CPUTemperature
from psutil import cpu_percent, virtual_memory

# GPS parameters
BAUDRATE = 38400
TIMEOUT = 1
DESCRIPTION = "u-blox GNSS receiver"
HWID = "1546:01A9"

# Importa el módulo para publicar mensajes MQTT
import paho.mqtt.publish as publish  

logging.basicConfig(filename='/home/cubesat/error.log', level=logging.DEBUG,
                    format='%(asctime)s: %(levelname)s: %(message)s')

def initialize_csv_folder():
    """Crea la carpeta 'csv' si no existe."""
    if not os.path.exists(csv_folder):
        os.makedirs(csv_folder)
        print(f"Carpeta '{csv_folder}' creada.")

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
        data = read_uv_data(sensor)
        log_status("UV Sensor", "OK")
        return data['UVA'], data['UVB'], data['UVC'], data['temp']
    except Exception as e:
        log_status("UV Sensor", "Disconnected")
        logging.error(f"Error reading UV Sensor: {e}")
        return None, None, None, None

# ICM20948 Sensor
def read_imu_sensor():
    try:
        sensor = init_icm_sensor()
        data = read_imu_data(sensor)
        log_status("IMU Sensor", "OK")
        return data['acceleration'], data['gyro'], data['magnetic']
    except Exception as e:
        log_status("IMU Sensor", "Disconnected")
        logging.error(f"Error reading IMU Sensor: {e}")
        return None, None, None

# BMP3XX Sensor
def read_bmp3xx_sensor():
    try:
        sensor = init_bmp_sensor()
        data = read_bmp_data(sensor)
        log_status("BMP3XX", "OK")
        return data['pressure'], data['temperature'], data['altitude']
    except Exception as e:
        log_status("BMP3XX", "Disconnected")
        logging.error(f"Error reading BMP3XX Sensor: {e}")
        return None, None, None

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

# CPU Temperature
def read_CPU():
    """Reads the CPU temperature."""
    try:
        cpu = CPUTemperature().temperature
        log_status("CPUTemperature", "OK")
        return cpu
    except Exception as e:
        log_status("CPUTemperature", "Disconnected")
        logging.error(f"Error reading CPU Temperature: {e}")
        return None

# CPU Usage
def read_CPU_usage():
    """Reads the CPU usage."""
    try:
        cpu = cpu_percent(interval=1)
        log_status("CPU Usage", "OK")
        return cpu
    except Exception as e:
        log_status("CPU Usage", "Disconnected")
        logging.error(f"Error reading CPU Usage: {e}")
        return None

# RAM Usage
def read_RAM_usage():
    """Reads the RAM usage."""
    try:
        ram = virtual_memory().percent
        log_status("RAM Usage", "OK")
        return ram
    except Exception as e:
        log_status("RAM Usage", "Disconnected")
        logging.error(f"Error reading RAM Usage: {e}")
        return None

# GPS Sensor
def read_gps_sensor(gps_parser):
    try:
        if not gps_parser.gps or not gps_parser.serial_port:
            # Try to reconnect to the GPS
            gps_parser = GPSParser(BAUDRATE, TIMEOUT, description=DESCRIPTION, hwid=HWID)
            if not gps_parser.gps or not gps_parser.serial_port:
                log_status("GPS Sensor", "Disconnected")
                return None, None, None, None, None, None, None

        nmea_data = gps_parser.read_nmea_data()
        if nmea_data:
            extracted_data = gps_parser.extract_relevant_data(nmea_data)
            log_status("GPS Sensor", "OK")
            return extracted_data['Latitude'], extracted_data['Longitude'], extracted_data['Altitude'], extracted_data['Satellites in View'], extracted_data['Elevation'], extracted_data['Azimuth'], extracted_data['Time (UTC)']
        else:
            log_status("GPS Sensor", "Disconnected")
            return None, None, None, None, None, None, None
    except Exception as e:
        log_status("GPS Sensor", "Disconnected")
        logging.error(f"Error reading GPS Sensor: {e}")
        return None, None, None, None, None, None, None

## Prepare the data to be sent
def prepare_sensor_data(readings):
    sensors_data = {"Date": time.strftime("%H:%M:%S", time.localtime())}
    for sensor, data in readings.items():
        sensors_data[sensor] = data if data else "Error"
    return sensors_data

## Read all the sensors
def read_sensors(gps_parser):
    latitude, longitude, altitude, satellites, elevation, azimuth, utc_time = read_gps_sensor(gps_parser)
    acceleration, gyro, magnetic = read_imu_sensor()
    pressure, temperature, bmp_altitude = read_bmp3xx_sensor()
    uva, uvb, uvc, uv_temp = read_uv_sensor()

    readings = {
        "CPUTemp"       : read_CPU(),
        "CPU Usage"     : read_CPU_usage(),
        "RAM Usage"     : read_RAM_usage(),
        "Latitude"      : latitude,
        "Longitude"     : longitude,
        "Altitude"      : altitude,
        "Satellites"    : satellites,
        "Elevation"     : elevation,
        "Azimuth"       : azimuth,
        "UTC Time"      : utc_time,
        "Acceleration"  : acceleration,
        "Gyro"          : gyro,
        "Magnetic"      : magnetic,
        "Pressure"      : pressure,
        "BMP Temp"      : temperature,
        "BMP Altitude"  : bmp_altitude,
        "UVA"           : uva,
        "UVB"           : uvb,
        "UVC"           : uvc,
        "UV Temp"       : uv_temp,
        "Temperature"   : read_dallas_sensor(),
    }
    return prepare_sensor_data(readings)

## Save the data to a CSV file
def save_json_to_csv(json_data, csv_file_path):
    try:
        data = json.loads(json_data)

        # Check if the CSV file already exists
        file_exists = os.path.isfile(csv_file_path)

        with open(csv_file_path, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=data.keys())

            # If the file doesn't exist, write the header
            if not file_exists:
                writer.writeheader()

            # Write the data
            writer.writerow(data)
        
        logging.info(f"Data appended to {csv_file_path} successfully.")

    except Exception as e:
        logging.error(f"Error saving data to CSV: {e}")

## MQTT Configuration and interval between sensor readings
hostname_mqtt = "localhost"
sensorReadingInterval = 2

# Path to save the CSV file

if __name__ == "__main__":
    try:
        # Generar nombre único de archivo CSV
        current_time = time.strftime("%H%M%S", time.localtime())
        current_date = time.strftime("%d%m%Y", time.localtime())

        csv_folder = f"CSV/{current_date}"  # Ruta a la carpeta donde se guardará el CSV
        initialize_csv_folder()  # Asegura que la carpeta CSV exista
        csv_filename = f"data_{current_time}.csv"
        csv_file_path = os.path.join(csv_folder, csv_filename)

        gps_parser = GPSParser(BAUDRATE, TIMEOUT, description=DESCRIPTION, hwid=HWID)
        
        while True:
            #clear_screen()
            logging.debug("Reading sensor data...")
            sensor_data = read_sensors(gps_parser)
            sensorDataJSON = json.dumps(sensor_data)

            if sensorDataJSON:
                # Publish the data via MQTT
                logging.debug(f"Publishing data via MQTT: {sensorDataJSON}")
                publish.single("data", sensorDataJSON, hostname=hostname_mqtt)
                print("Data sent successfully.")

                # Save the JSON data to CSV
                logging.debug(f"Saving data to CSV: {sensorDataJSON}")
                save_json_to_csv(sensorDataJSON, csv_file_path)
                print(f"Data saved to {csv_filename} successfully.")
            else:
                print("Error sending data.")

            time.sleep(sensorReadingInterval)

    except KeyboardInterrupt:
        print("\n Program stopped by the user.")
    except Exception as e:
        logging.error(f"Unexpected error while publishing data: {e}")
        print(f"Unexpected error while publishing data: {e}")
