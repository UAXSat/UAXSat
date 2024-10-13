"""* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
*                                                                            *
*                         Developed by Javier Bolanos                        *
*                  https://github.com/javierbolanosllano                     *
*                                                                            *
*                      UAXSAT IV Project - 2024                              *
*                   https://github.com/UAXSat/UAXSat                         *
*                                                                            *
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *"""

# receiver.py

import serial
import time
import json
import psycopg2
import logging
import RPi.GPIO as GPIO

# Logger configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# GPIO pin definitions
M0_PIN = 17
M1_PIN = 27
AUX_PIN = 22

# Serial port configuration
SERIAL_PORT = '/dev/ttyUSB0'  # Adjust according to your system
BAUD_RATE = 9600

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
        logger.error("Failed to configure module in NORMAL mode.")

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
        logger.error(f"Database connection error: {error}")
        raise

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
            gps_rmc_speed_mps, gps_vtg_speed_kmh,
            gps_gga_latitude, gps_gga_longitude, gps_distance,
            gps_gga_altitude, gps_gga_height_geoid, gps_gsv_total_satellites,
            gps_gsv_total_azimuth, gps_gsv_total_elevation, gps_gsv_total_SNR,
            HDOP, PDOP, VDOP,
            system_cpu_usage_percent, system_ram_usage_percent,
            system_temp_cpu_thermal, timestamp
        ) VALUES (
            %(imu_acelx)s, %(imu_acely)s, %(imu_acelz)s, %(imu_girox)s, %(imu_giroy)s, %(imu_giroz)s,
            %(imu_magx)s, %(imu_magy)s, %(imu_magz)s, %(uv_uva)s, %(uv_uvb)s, %(uv_uvc)s, %(uv_uv_temp)s,
            %(bmp_pressure)s, %(bmp_temperature)s, %(bmp_altitude)s, %(bmp_vertical_speed)s,
            %(dallas_28_03a0d446ef0a)s, %(dallas_28_6fc2d44578f0)s,
            %(gps_rmc_speed_mps)s, %(gps_vtg_speed_kmh)s,
            %(gps_gga_latitude)s, %(gps_gga_longitude)s, %(gps_distance)s,
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
            'gps_rmc_speed_mps': to_float(data.get('GPS', {}).get('RMC', {}).get('speed_mps')),
            'gps_vtg_speed_kmh': to_float(data.get('GPS', {}).get('VTG', {}).get('speed_kmh')),
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

def receive_message(cursor, connection):
    """Receive messages via LoRa and process the data between markers."""
    buffer = ""
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
            logger.info("Serial port opened for reception.")
            while True:
                if ser.in_waiting > 0:
                    chunk = ser.read(ser.in_waiting).decode('utf-8', errors='ignore').strip()
                    buffer += chunk
                    logger.debug(f"Updated buffer: {buffer}")

                    # Process complete messages
                    while '<<<' in buffer and '>>>' in buffer:
                        start = buffer.find('<<<') + 3
                        end = buffer.find('>>>', start)
                        if end != -1:
                            message_content = buffer[start:end]
                            buffer = buffer[end+3:]  # Update the buffer
                            logger.debug(f"Extracted complete message: {message_content}")
                            try:
                                data = json.loads(message_content)
                                logger.info(data)
                                logger.debug(data)
                                logger.info("Sensor data received and deserialized.")
                                logger.debug(f"Deserialized data: {data}")
                                insert_data_to_db(cursor, connection, data)
                            except json.JSONDecodeError as e:
                                logger.error(f"Error deserializing message: {e}")
                        else:
                            break  # Wait for the rest of the message
                else:
                    time.sleep(0.1)
    except serial.SerialException as e:
        logger.error(f"Serial communication error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in receive_message: {e}")

def main():
    try:
        logger.info("Starting receiver program...")
        enter_normal_mode()
        connection, cursor = connect_to_db()
        receive_message(cursor, connection)
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
        logger.info("Ending receiver program. Cleaning up GPIO...")
        GPIO.cleanup()
        logger.debug("GPIO cleaned up.")

if __name__ == '__main__':
    main()
