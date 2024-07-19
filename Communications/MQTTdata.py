import os
import time
import json
import csv
import logging
import sys
import paho.mqtt.client as mqtt

sys.path.append('../')  # Permite importar módulos de la carpeta vecinos

# Import the modules to read the sensors
from Sensors.UVmodule import initialize_sensor as init_uv_sensor, read_sensor_data as read_uv_data
from Sensors.GPS import GPSHandler
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

## MQTT Configuration and interval between sensor readings
broker = "localhost"
port = 1883
sensorReadingInterval = 2
topic = "data"

# Logging configuration
logging.basicConfig(filename='/home/javil/error.log', level=logging.DEBUG,
                    format='%(asctime)s: %(levelname)s: %(message)s')

def initialize_csv_folder():
    """Create the folder to save the CSV files if it doesn't exist."""
    if not os.path.exists(csv_folder):
        os.makedirs(csv_folder)
        logging.info(f"Carpeta '{csv_folder}' creada.")

def log_status(sensor_name, status):
    """
    Logs the sensor status.

    Parameters:
    - sensor_name: Name of the sensor (string).
    - status: Sensor status ('OK' or 'Disconnected') (string).
    """
    status_message = f"{sensor_name}: {status}"
    if status == "OK":
        logging.info(status_message)
    else:
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
# def read_bmp3xx_sensor():
#     try:
#         sensor = init_bmp_sensor()
#         data = read_bmp_data(sensor)
#         log_status("BMP3XX", "OK")
#         return data['pressure'], data['temperature'], data['altitude']
#     except Exception as e:
#         log_status("BMP3XX", "Disconnected")
#         logging.error(f"Error reading BMP3XX Sensor: {e}")
#         return None, None, None

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
def read_gps_sensor(gps_reader):
    try:
        if not gps_reader.gps or not gps_reader.serial_port:
            # Try to reconnect to the GPS
            logging.debug("Attempting to reconnect to GPS...")
            gps_reader = GPSHandler(BAUDRATE, TIMEOUT, description=DESCRIPTION, hwid=HWID)
            if not gps_reader.gps or not gps_reader.serial_port:
                log_status("GPS Sensor", "Disconnected")
                return None, None, None, None, None, None, None

        data = gps_reader.GPSprogram()
        if data:
            extracted_data = gps_reader.GPSprogram(data)
            log_status("GPS Sensor", "OK")
            return extracted_data['Latitude'], extracted_data['Longitude'], extracted_data['Heading of Motion'], extracted_data['Roll'], extracted_data['Pitch'], extracted_data['Heading'], extracted_data['NMEA Sentence']
        else:
            log_status("GPS Sensor", "Disconnected")
            return None, None, None, None, None, None, None
        
    except Exception as e:
        log_status("GPS Sensor", "Disconnected")
        logging.error(f"Error reading GPS Sensor: {e}")
        return None, None, None, None, None, None, None

## Prepare the data to be sent
def prepare_sensor_data(readings):
    sensors_data = {"Date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}
    for sensor, data in readings.items():
        if data:
            sensors_data[sensor] = data
        else:
            sensors_data[sensor] = "Error"
    return sensors_data

## Read all the sensors
def read_sensors(gps_parser):
    latitude, longitude, altitude, satellites, elevation, azimuth, utc_time = read_gps_sensor(gps_parser)
    acceleration, gyro, magnetic = read_imu_sensor()
    # pressure, temperature, bmp_altitude = read_bmp3xx_sensor()
    uva, uvb, uvc, uv_temp = read_uv_sensor()

    readings = {
        "CPUTemp"       : read_CPU(),
        "CPU Usage"     : read_CPU_usage(),
        "RAM Usage"     : read_RAM_usage(),
        "Latitude"      : latitude,
        "Longitude"     : longitude,
        "Altitude"      : altitude,
        "Satellites"    : satellites,
        "Acceleration"  : acceleration,
        "Gyro"          : gyro,
        "Magnetic"      : magnetic,
        # "Pressure"      : pressure,
        # "BMP Temp"      : temperature,
        # "BMP Altitude"  : bmp_altitude,
        "UVA"           : uva,
        "UVB"           : uvb,
        "UVC"           : uvc,
        "UV Temp"       : uv_temp,
        "Temperature"   : read_dallas_sensor(),
    }
    return prepare_sensor_data(readings)

## Save the data to a CSV file
def save_json_to_csv(json_data, csv_file_path):
    # Parse the JSON data
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

## MQTT Callbacks
def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        logging.info("Connected to MQTT Broker!")
    else:
        logging.error("Failed to connect, return code %d\n", reason_code)

def on_publish(client, userdata, mid, reason_codes=None, properties=None):
    logging.info(f"Data published with mid {mid}")

if __name__ == "__main__":
    try:
        logging.info("Starting sensor data collection script.")

        # Generate unique CSV file name
        current_time = time.strftime("%H%M%S", time.localtime())
        current_date = time.strftime("%d%m%Y", time.localtime())

        home_folder = os.path.expanduser('~')
        csv_folder = os.path.join(home_folder, 'CSV', current_date)

        # Ensure the CSV folder exists; create it if it doesn't
        if not os.path.exists(csv_folder):
            os.makedirs(csv_folder)

        csv_filename = f"data_{current_time}.csv"
        csv_file_path = os.path.join(csv_folder, csv_filename)

        gps_parser = GPSParser(BAUDRATE, TIMEOUT, description=DESCRIPTION, hwid=HWID)

        # MQTT Client
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_publish = on_publish
        client.connect(broker, port, 60)
        client.loop_start()

        while True:
            logging.debug("Reading sensor data...")
            sensor_data = read_sensors(gps_parser)
            sensorDataJSON = json.dumps(sensor_data)

            if sensorDataJSON:
                # Publish the data via MQTT
                logging.debug(f"Publishing data via MQTT: {sensorDataJSON}")
                result = client.publish(topic, sensorDataJSON)
                status = result.rc
                if status == mqtt.MQTT_ERR_SUCCESS:
                    logging.info("Data sent successfully.")
                else:
                    logging.error(f"Failed to send message to topic {topic}")

                # Save the JSON data to CSV
                logging.debug(f"Saving data to CSV: {sensorDataJSON}")
                save_json_to_csv(sensorDataJSON, csv_file_path)
                logging.info(f"Data saved to {csv_filename} successfully.")
            else:
                logging.error("Error preparing sensor data.")

            time.sleep(sensorReadingInterval)

    except KeyboardInterrupt:
        logging.info("Program stopped by the user.")
    except Exception as e:
        logging.error(f"Unexpected error while publishing data: {e}")
    finally:
        client.loop_stop()
        client.disconnect()
