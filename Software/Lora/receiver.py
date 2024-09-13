# receiver.py
import json
import logging
import psycopg2
from e220 import E220

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

VID_PID_LIST = [
    (0x10C4, 0xEA60),  # Example VID and PID for the E220 module
    (0x1A86, 0x7523)   # Another possible VID and PID
]

def insert_data_to_db(data):
    """
    Insert the sensor data into a PostgreSQL database.
    :param data: Dictionary containing sensor data
    """
    connection = None
    cursor = None
    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(
            database="cubesat",
            user="cubesat",
            password="cubesat",
            host="localhost",
            port="5432"
        )
        cursor = connection.cursor()

        # Define the SQL query to insert sensor data
        insert_query = """
        INSERT INTO sensor_readings (imu_accelx, imu_accely, imu_accelz, imu_gyrox, imu_gyroy, imu_gyroz, 
                                     imu_magx, imu_magy, imu_magz, uv_uva, uv_uvb, uv_uvc, uv_temperature, 
                                     cpu_usage, ram_usage, total_ram, disk_usage, disk_usage_gb, 
                                     total_disk_gb, sys_temperature, lat, lon, alt, headmot, roll, pitch, 
                                     heading, nmea, lat_hp, lon_hp, alt_hp, gps_error, bmp_pressure, 
                                     bmp_temperature, bmp_altitude, ds18b20_temperature_interior, 
                                     ds18b20_temperature_exterior, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        # Extract relevant data from the dictionary
        gps_data = data.get('GPS', {})
        ds18b20_data = data.get('Dallas', {})

        cursor.execute(insert_query, (
            data.get('IMU', {}).get('ACCELX'),
            data.get('IMU', {}).get('ACCELY'),
            data.get('IMU', {}).get('ACCELZ'),
            data.get('IMU', {}).get('GYROX'),
            data.get('IMU', {}).get('GYROY'),
            data.get('IMU', {}).get('GYROZ'),
            data.get('IMU', {}).get('MAGX'),
            data.get('IMU', {}).get('MAGY'),
            data.get('IMU', {}).get('MAGZ'),
            data.get('UV', {}).get('UVA'),
            data.get('UV', {}).get('UVB'),
            data.get('UV', {}).get('UVC'),
            data.get('UV', {}).get('temperature'),
            data.get('System', {}).get('cpu_usage'),
            data.get('System', {}).get('ram_usage'),
            data.get('System', {}).get('total_ram'),
            data.get('System', {}).get('disk_usage'),
            data.get('System', {}).get('disk_usage_gb'),
            data.get('System', {}).get('total_disk_gb'),
            data.get('System', {}).get('sys_temperature'),
            gps_data.get('lat'),
            gps_data.get('lon'),
            gps_data.get('alt'),
            gps_data.get('headmot'),
            gps_data.get('roll'),
            gps_data.get('pitch'),
            gps_data.get('heading'),
            gps_data.get('nmea'),
            gps_data.get('lat_hp'),
            gps_data.get('lon_hp'),
            gps_data.get('alt_hp'),
            gps_data.get('gps_error'),
            data.get('BMP', {}).get('pressure'),
            data.get('BMP', {}).get('temperature'),
            data.get('BMP', {}).get('altitude'),
            ds18b20_data.get('temperature_interior'),
            ds18b20_data.get('temperature_exterior'),
            data.get('timestamp')
        ))

        connection.commit()
        logger.info("Data inserted successfully into the database.")

    except Exception as e:
        logger.error(f"An error occurred while inserting data: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def main():
    uart_port = None
    for vid, pid in VID_PID_LIST:
        uart_port = E220.find_serial_port(vid, pid)
        if uart_port:
            break

    if uart_port is None:
        logger.error("LoRa module not found. Check connections.")
        return

    logger.info(f"LoRa module found at {uart_port}, initializing.")

    try:
        lora_module = E220(m0_pin=17, m1_pin=27, aux_pin=22, uart_port=uart_port)

        while True:
            data = lora_module.receive_data()
            if data:
                data = data.strip("<<<").strip(">>>")
                sensor_data = json.loads(data)
                insert_data_to_db(sensor_data)
                logger.info(f"Received data: {sensor_data}")

    except KeyboardInterrupt:
        logger.info("Program interrupted by user, exiting.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        lora_module.close()

if __name__ == "__main__":
    main()
