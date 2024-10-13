"""* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
*                                                                            *
*                         Developed by Javier Bolanos                        *
*                  https://github.com/javierbolanosllano                     *
*                                                                            *
*                      UAXSAT IV Project - 2024                              *
*                   https://github.com/UAXSat/UAXSat                         *
*                                                                            *
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *"""

# emitter.py

import serial
import time
import json
import logging
import RPi.GPIO as GPIO
import psycopg2

# Logger configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import sensor modules
from Modules.IMUmodule import get_IMU_data
from Modules.UVmodule import get_UV_data
from Modules.BMPmodule import get_BMP_data
from Modules.DS18B20module import get_DS18B20_data
from Modules.GPSmodule import get_GPS_data
from Modules.SYSTEMmodule import get_system_data

# GPIO pin definitions
M0_PIN = 17
M1_PIN = 27
AUX_PIN = 22

# Serial port configuration
SERIAL_PORT = '/dev/ttyUSB0'  # Adjust according to your system
BAUD_RATE = 9600  # Must match the LoRa module configuration

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(M0_PIN, GPIO.OUT)
GPIO.setup(M1_PIN, GPIO.OUT)
GPIO.setup(AUX_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def wait_aux_high(timeout=10):
    """Wait until the AUX pin is HIGH."""
    logger.debug("Waiting for AUX to be HIGH...")
    end_time = time.time() + timeout
    while GPIO.input(AUX_PIN) == GPIO.LOW:
        if time.time() > end_time:
            logger.error("Timeout waiting for AUX to be HIGH.")
            return False
        time.sleep(0.01)
    logger.debug("AUX is HIGH.")
    return True

def wait_aux_low(timeout=10):
    """Wait until the AUX pin is LOW."""
    logger.debug("Waiting for AUX to be LOW...")
    end_time = time.time() + timeout
    while GPIO.input(AUX_PIN) == GPIO.HIGH:
        if time.time() > end_time:
            logger.error("Timeout waiting for AUX to be LOW.")
            return False
        time.sleep(0.01)
    logger.debug("AUX is LOW.")
    return True

def enter_normal_mode():
    """Configure the LoRa module in normal (transparent) mode."""
    logger.info("Configuring the module in NORMAL mode...")
    GPIO.output(M0_PIN, GPIO.LOW)
    GPIO.output(M1_PIN, GPIO.LOW)
    if wait_aux_high():
        time.sleep(0.1)
        logger.info("Module configured in NORMAL mode.")
    else:
        logger.error("Failed to configure the module in NORMAL mode.")

def get_all_sensor_data():
    sensor_data = {}
    try:
        logger.info("Collecting sensor data...")
        initial_lat = None  # Define your initial latitude if necessary
        initial_lon = None  # Define your initial longitude if necessary

        sensor_data['IMU'] = get_IMU_data()
        logger.debug(f"IMU data: {sensor_data['IMU']}")

        sensor_data['UV'] = get_UV_data()
        logger.debug(f"UV data: {sensor_data['UV']}")

        sensor_data['BMP'] = get_BMP_data()
        logger.debug(f"BMP data: {sensor_data['BMP']}")

        sensor_data['Dallas'] = get_DS18B20_data()
        logger.debug(f"Dallas data: {sensor_data['Dallas']}")

        sensor_data['GPS'] = get_GPS_data(initial_lat, initial_lon)
        logger.debug(f"GPS data: {sensor_data['GPS']}")

        sensor_data['System'] = get_system_data()
        logger.debug(f"System data: {sensor_data['System']}")

        sensor_data['timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        logger.debug(f"Timestamp: {sensor_data['timestamp']}")

        logger.info("Sensor data collected successfully.")
        return sensor_data
    except Exception as e:
        logger.error(f"Error obtaining sensor data: {e}")
        return None

def serialize_sensor_data(sensor_data):
    try:
        logger.info("Serializing sensor data...")
        serialized_data = json.dumps(sensor_data)
        logger.debug(f"Serialized data: {serialized_data}")
        return serialized_data
    except Exception as e:
        logger.error(f"Error serializing data: {e}")
        return None

def connect_to_db():
    """Connect to the database and return the connection and cursor."""
    try:
        logger.info("Connecting to the database...")
        connection = psycopg2.connect(
            database="cubesat",
            user="cubesat",
            password="cubesat",
            host="localhost",
            port="5432"
        )
        cursor = connection.cursor()
        logger.info("Database connection established.")
        return connection, cursor
    except psycopg2.Error as error:
        logger.error(f"Error connecting to the database: {error}")
        return None, None

def insert_data_to_db(cursor, connection, data):
    """Insert the received data into the database."""
    try:
        logger.info("Inserting data into the database...")
        insert_query = """
        INSERT INTO sensor_readings (
            imu_acelx, imu_acely, imu_acelz, imu_girox, imu_giroy, imu_giroz,
            imu_magx, imu_magy, imu_magz, uv_uva, uv_uvb, uv_uvc, uv_uv_temp,
            bmp_pressure, bmp_temperature, bmp_altitude, bmp_vertical_speed,
            dallas_28_03a0d446ef0a, dallas_28_6fc2d44578f0,
            gps_rmc_utc_time, gps_rmc_speed_mps, gps_vtg_speed_kmh,
            gps_gga_utc_time, gps_gga_latitude, gps_gga_longitude, gps_distance,
            gps_gga_altitude, gps_gga_height_geoid, gps_gsv_total_satellites,
            gps_gsv_total_azimuth, gps_gsv_total_elevation, gps_gsv_total_SNR,
            system_cpu_usage_percent, system_ram_usage_percent,
            system_temp_cpu_thermal, timestamp
        ) VALUES (
            %(imu_acelx)s, %(imu_acely)s, %(imu_acelz)s, %(imu_girox)s, %(imu_giroy)s, %(imu_giroz)s,
            %(imu_magx)s, %(imu_magy)s, %(imu_magz)s, %(uv_uva)s, %(uv_uvb)s, %(uv_uvc)s, %(uv_uv_temp)s,
            %(bmp_pressure)s, %(bmp_temperature)s, %(bmp_altitude)s, %(bmp_vertical_speed)s,
            %(dallas_28_03a0d446ef0a)s, %(dallas_28_6fc2d44578f0)s,
            %(gps_rmc_utc_time)s, %(gps_rmc_speed_mps)s, %(gps_vtg_speed_kmh)s,
            %(gps_gga_utc_time)s, %(gps_gga_latitude)s, %(gps_gga_longitude)s, %(gps_distance)s,
            %(gps_gga_altitude)s, %(gps_gga_height_geoid)s, %(gps_gsv_total_satellites)s,
            %(gps_gsv_total_azimuth)s, %(gps_gsv_total_elevation)s, %(gps_gsv_total_SNR)s,
            %(system_cpu_usage_percent)s, %(system_ram_usage_percent)s,
            %(system_temp_cpu_thermal)s, %(timestamp)s
        );
        """

        # Helper function to convert values to float
        def to_float(value):
            try:
                return float(value)
            except (TypeError, ValueError):
                return None

        # Data mapping for the query
        data_map = {
            'imu_acelx': data.get('IMU', {}).get('ACELX'),
            'imu_acely': data.get('IMU', {}).get('ACELY'),
            'imu_acelz': data.get('IMU', {}).get('ACELZ'),
            'imu_girox': data.get('IMU', {}).get('GIROX'),
            'imu_giroy': data.get('IMU', {}).get('GIROY'),
            'imu_giroz': data.get('IMU', {}).get('GIROZ'),
            'imu_magx': data.get('IMU', {}).get('MAGX'),
            'imu_magy': data.get('IMU', {}).get('MAGY'),
            'imu_magz': data.get('IMU', {}).get('MAGZ'),
            'uv_uva': data.get('UV', {}).get('UVA'),
            'uv_uvb': data.get('UV', {}).get('UVB'),
            'uv_uvc': data.get('UV', {}).get('UVC'),
            'uv_uv_temp': data.get('UV', {}).get('UV Temp'),
            'bmp_pressure': data.get('BMP', {}).get('pressure'),
            'bmp_temperature': data.get('BMP', {}).get('temperature'),
            'bmp_altitude': data.get('BMP', {}).get('altitude'),
            'bmp_vertical_speed': to_float(data.get('BMP', {}).get('vertical_speed')),
            'dallas_28_03a0d446ef0a': data.get('Dallas', {}).get('28-03a0d446ef0a'),
            'dallas_28_6fc2d44578f0': data.get('Dallas', {}).get('28-6fc2d44578f0'),
            'gps_rmc_utc_time': data.get('GPS', {}).get('RMC', {}).get('utc_time'),
            'gps_rmc_speed_mps': to_float(data.get('GPS', {}).get('RMC', {}).get('speed_mps')),
            'gps_vtg_speed_kmh': to_float(data.get('GPS', {}).get('VTG', {}).get('speed_kmh')),
            'gps_gga_utc_time': data.get('GPS', {}).get('GGA', {}).get('utc_time'),
            'gps_gga_latitude': to_float(data.get('GPS', {}).get('GGA', {}).get('latitude')),
            'gps_gga_longitude': to_float(data.get('GPS', {}).get('GGA', {}).get('longitude')),
            'gps_distance': to_float(data.get('GPS', {}).get('distance')),
            'gps_gga_altitude': to_float(data.get('GPS', {}).get('GGA', {}).get('altitude')),
            'gps_gga_height_geoid': to_float(data.get('GPS', {}).get('GGA', {}).get('height_geoid')),
            'gps_gsv_total_satellites': data.get('GPS', {}).get('GSV', {}).get('total_satellites'),
            'gps_gsv_total_azimuth': to_float(data.get('GPS', {}).get('GSV', {}).get('total_azimuth')),
            'gps_gsv_total_elevation': to_float(data.get('GPS', {}).get('GSV', {}).get('total_elevation')),
            'gps_gsv_total_SNR': to_float(data.get('GPS', {}).get('GSV', {}).get('total_SNR')),
            'system_cpu_usage_percent': data.get('System', {}).get('CPU Usage (%)'),
            'system_ram_usage_percent': data.get('System', {}).get('RAM Usage (%)'),
            'system_temp_cpu_thermal': data.get('System', {}).get('CPU Temperature'),
            'timestamp': data.get('timestamp')
        }

        # Execute the insert query
        cursor.execute(insert_query, data_map)
        connection.commit()
        logger.info("Data inserted successfully into the database.")

    except Exception as e:
        logger.error(f"Error inserting data into the database: {e}")
        connection.rollback()

def send_message(message):
    """Send a message via LoRa."""
    logger.info(f"Sending message: {message}")
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
            ser.write(message.encode('utf-8'))
            if not wait_aux_low():
                logger.error("Failed to send message: AUX did not go LOW.")
                return
            if not wait_aux_high():
                logger.error("Failed to send message: AUX did not return HIGH.")
                return
        logger.info("Message sent.")
    except serial.SerialException as e:
        logger.error(f"Serial communication error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error sending the message: {e}")

def send_sensor_data(cursor, connection):
    sensor_data = get_all_sensor_data()
    if sensor_data:
        message_content = serialize_sensor_data(sensor_data)
        if message_content:
            # Wrap the message with markers <<< and >>>
            full_message = f'<<<{message_content}>>>'
            send_message(full_message)
            # Save data to the database
            insert_data_to_db(cursor, connection, sensor_data)
        else:
            logger.error("Could not serialize the data.")
    else:
        logger.error("Data not sent due to an error in collection.")

def main():
    connection = None
    cursor = None
    try:
        logger.info("Starting emitter program...")
        enter_normal_mode()
        connection, cursor = connect_to_db()
        if not connection or not cursor:
            logger.error("Could not establish connection to the database.")
            return
        while True:
            send_sensor_data(cursor, connection)
            time.sleep(5)  # Wait 5 seconds before sending again
    except KeyboardInterrupt:
        logger.info("Program interrupted by the user.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        if cursor:
            cursor.close()
            logger.debug("Database cursor closed.")
        if connection:
            connection.close()
            logger.debug("Database connection closed.")
        logger.info("Ending emitter program. Cleaning up GPIO...")
        GPIO.cleanup()
        logger.debug("GPIO cleaned up.")

if __name__ == '__main__':
    main()