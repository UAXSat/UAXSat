import os
import time
import json
import csv
import logging
import sys
import paho.mqtt.client as mqtt
import psycopg2

sys.path.append('../')  # Permite importar módulos de la carpeta vecinos

# Import the modules to read the sensors
from Sensors.UVmodule import initialize_sensor as init_uv_sensor, read_sensor_data as read_uv_data
from Sensors.GPS import GPSHandler
from Sensors.IMUmodule import initialize_sensor as init_icm_sensor, read_sensor_data as read_imu_data
from Sensors.DS18B20module import DallasSensor
from Sensors.BMPmodule import initialize_sensor as init_bmp_sensor, read_sensor_data as read_bmp_data
from gpiozero import CPUTemperature
from psutil import cpu_percent, virtual_memory

# Database configuration
DB_HOST = 'localhost'
DB_PORT = 5432
DB_NAME = 'grafana'
DB_USER = 'grafana'
DB_PASSWORD = '4225'

## MQTT Configuration and interval between sensor readings
broker = "localhost"
port = 1883
sensorReadingInterval = 2
topic = "data"

# GPS parameters
BAUDRATE = 38400
TIMEOUT = 1
DESCRIPTION = "u-blox GNSS receiver"
HWID = "1546:01A9"

# Logging configuration
logging.basicConfig(filename='/home/javil/error.log', level=logging.DEBUG,
                    format='%(asctime)s: %(levelname)s: %(message)s')

# Initialize PostgreSQL connection
def connect_to_db():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        logging.info("Connected to PostgreSQL database.")
        return conn
    except Exception as e:
        logging.error(f"Error connecting to PostgreSQL database: {e}")
        return None

def insert_sensor_data(conn, data):
    try:
        with conn.cursor() as cursor:
            # Convert "Error" or None to NULL for numeric fields
            for key in ['cpu_temp', 'cpu_usage', 'ram_usage', 'latitude', 'longitude', 'altitude',
                        'heading_motion', 'uva', 'uvb', 'uvc', 'uv_temp', 'temperature']:
                if data.get(key) == "Error" or data.get(key) is None:
                    data[key] = None

            # Prepare the query
            query = """
                INSERT INTO sensor_data (
                    timestamp, cpu_temp, cpu_usage, ram_usage, latitude, longitude, altitude,
                    heading_motion, roll, pitch, heading, nmea_sentence, acceleration, gyro,
                    magnetic, uva, uvb, uvc, uv_temp, temperature
                ) VALUES (
                    %(timestamp)s, %(cpu_temp)s, %(cpu_usage)s, %(ram_usage)s, %(latitude)s, %(longitude)s, %(altitude)s,
                    %(heading_motion)s, %(roll)s, %(pitch)s, %(heading)s, %(nmea_sentence)s, %(acceleration)s, %(gyro)s,
                    %(magnetic)s, %(uva)s, %(uvb)s, %(uvc)s, %(uv_temp)s, %(temperature)s
                )
            """
            cursor.execute(query, data)
            conn.commit()
            logging.info("Sensor data inserted into PostgreSQL database.")
    except psycopg2.Error as e:
        conn.rollback()  # Rollback the transaction if an error occurs
        logging.error(f"Error inserting data into PostgreSQL database: {e.pgerror}")
        logging.error(f"Error details: {e.diag.message_primary}")
    except Exception as e:
        conn.rollback()  # Rollback the transaction if a non-psycopg2 error occurs
        logging.error(f"Unexpected error inserting data: {e}")

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
            log_status("GPS Sensor", "OK")
            return data['Latitude'], data['Longitude'], data['Altitude'], data['Heading of Motion'], data['Roll'], data['Pitch'], data['Heading'], data['NMEA Sentence']
        else:
            log_status("GPS Sensor", "Disconnected")
            return None, None, None, None, None, None, None, None
        
    except Exception as e:
        log_status("GPS Sensor", "Disconnected")
        logging.error(f"Error reading GPS Sensor: {e}")
        return None, None, None, None, None, None, None, None

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
    latitude, longitude, altitude, headingMotion, roll, pitch, heading, nmea = read_gps_sensor(gps_parser)
    acceleration, gyro, magnetic = read_imu_sensor()
    # pressure, temperature, bmp_altitude = read_bmp3xx_sensor()
    uva, uvb, uvc, uv_temp = read_uv_sensor()

    readings = {
        "CPUTemp"           : read_CPU(),
        "CPU Usage"         : read_CPU_usage(),
        "RAM Usage"         : read_RAM_usage(),
        "Latitude"          : latitude,
        "Longitude"         : longitude,
        "Altitude"          : altitude,
        "Heading of Motion" : headingMotion,
        "Roll"              : roll,
        "Pitch"             : pitch,
        "Heading"           : heading,
        "NMEA Sentence"     : nmea,
        "Acceleration"      : acceleration,
        "Gyro"              : gyro,
        "Magnetic"          : magnetic,
        # "Pressure"        : pressure,
        # "BMP Temp"        : temperature,
        # "BMP Altitude"    : bmp_altitude,
        "UVA"               : uva,
        "UVB"               : uvb,
        "UVC"               : uvc,
        "UV Temp"           : uv_temp,
        "Temperature"       : read_dallas_sensor(),
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

        gps_parser = GPSHandler(BAUDRATE, TIMEOUT, description=DESCRIPTION, hwid=HWID)

        # MQTT Client
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_publish = on_publish
        client.connect(broker, port, 60)
        client.loop_start()

        # Database Connection
        db_conn = connect_to_db()

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

                # Insert data into PostgreSQL
                if db_conn:
                    data_to_insert = {
                        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        'cpu_temp': sensor_data.get('CPUTemp'),
                        'cpu_usage': sensor_data.get('CPU Usage'),
                        'ram_usage': sensor_data.get('RAM Usage'),
                        'latitude': sensor_data.get('Latitude'),
                        'longitude': sensor_data.get('Longitude'),
                        'altitude': sensor_data.get('Altitude'),
                        'heading_motion': sensor_data.get('Heading of Motion'),
                        'roll': sensor_data.get('Roll'),
                        'pitch': sensor_data.get('Pitch'),
                        'heading': sensor_data.get('Heading'),
                        'nmea_sentence': sensor_data.get('NMEA Sentence'),
                        'acceleration': json.dumps(sensor_data.get('Acceleration')),
                        'gyro': json.dumps(sensor_data.get('Gyro')),
                        'magnetic': json.dumps(sensor_data.get('Magnetic')),
                        'uva': sensor_data.get('UVA'),
                        'uvb': sensor_data.get('UVB'),
                        'uvc': sensor_data.get('UVC'),
                        'uv_temp': sensor_data.get('UV Temp'),
                        'temperature': sensor_data.get('Temperature')
                    }
                    insert_sensor_data(db_conn, data_to_insert)
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
        if db_conn:
            db_conn.close()