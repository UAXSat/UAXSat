# receiverauxtest.py
import json
import logging
import psycopg2
import time
import os
import sys
import threading  # Para manejar hilos
from serial.tools import list_ports  # Importar list_ports

from e220 import E220
from constants import M0, M1, AUX, VID_PID_LIST

# Configuración del logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

def find_serial_port(vendor_id, product_id):
    ports = list_ports.comports()
    for port in ports:
        if port.vid == vendor_id and port.pid == product_id:
            return port.device
    return None

def connect_to_db():
    try:
        connection = psycopg2.connect(
            database="cubesat",
            user="cubesat",
            password="cubesat",
            host="localhost",
            port="5432"
        )
        cursor = connection.cursor()
        return connection, cursor
    except psycopg2.Error as error:
        logger.error(f"Error al conectar a la base de datos: {error}")
        raise error

def insert_data_to_db(cursor, connection, data):
    try:
        insert_query = """
        INSERT INTO sensor_readings (
            imu_acelx, imu_acely, imu_acelz, imu_girox, imu_giroy, imu_giroz, imu_magx, imu_magy, imu_magz,
            uv_uva, uv_uvb, uv_uvc, uv_temperature, cpu_usage, ram_usage, total_ram,
            disk_usage, disk_usage_gb, total_disk_gb, sys_temperature,
            lat, lon, alt, headmot, roll, pitch, heading, nmea,
            lat_hp, lon_hp, alt_hp, gps_error, bmp_pressure, bmp_temperature, bmp_altitude,
            ds18b20_temperature_interior, ds18b20_temperature_exterior, timestamp
        ) VALUES (
            %(imu_acelx)s, %(imu_acely)s, %(imu_acelz)s, %(imu_girox)s, %(imu_giroy)s, %(imu_giroz)s, %(imu_magx)s, %(imu_magy)s, %(imu_magz)s,
            %(uv_uva)s, %(uv_uvb)s, %(uv_uvc)s, %(uv_temperature)s, %(cpu_usage)s, %(ram_usage)s, %(total_ram)s,
            %(disk_usage)s, %(disk_usage_gb)s, %(total_disk_gb)s, %(sys_temperature)s,
            %(lat)s, %(lon)s, %(alt)s, %(headmot)s, %(roll)s, %(pitch)s, %(heading)s, %(nmea)s,
            %(lat_hp)s, %(lon_hp)s, %(alt_hp)s, %(gps_error)s, %(bmp_pressure)s, %(bmp_temperature)s, %(bmp_altitude)s,
            %(ds18b20_temperature_interior)s, %(ds18b20_temperature_exterior)s, %(timestamp)s
        )
        """

        gps_data = data.get('GPS', [{}])[0] if data.get('GPS') else {}
        dallas_data = data.get('Dallas', {})
        ds18b20_temp_interior = dallas_data.get('28-03a0d446ef0a')
        ds18b20_temp_exterior = dallas_data.get('28-6fc2d44578f0')

        cursor.execute(insert_query, {
            'imu_acelx': data.get('IMU', {}).get('ACELX'),
            'imu_acely': data.get('IMU', {}).get('ACELY'),
            'imu_acelz': data.get('IMU', {}).get('ACELZ'),
            'imu_girox': data.get('IMU', {}).get('GIROX'),
            'imu_giroy': data.get('IMU', {}).get('GIROY'),
            'imu_giroz': data.get('IMU', {}).get('GIROZ'),
            'imu_magx': data.get('IMU', {}).get('MAGX'),
            'imu_magy': data.get('IMU', {}).get('MAGY'),
            'imu_magz': data.get('IMU', {}).get('MAGZ'),
            'lat': gps_data.get('latitude'),
            'lon': gps_data.get('longitude'),
            'alt': gps_data.get('altitude'),
            'headmot': gps_data.get('heading_of_motion'),
            'roll': gps_data.get('roll'),
            'pitch': gps_data.get('pitch'),
            'heading': gps_data.get('heading'),
            'nmea': gps_data.get('nmea_sentence'),
            'lat_hp': gps_data.get('high_precision_latitude'),
            'lon_hp': gps_data.get('high_precision_longitude'),
            'alt_hp': gps_data.get('high_precision_altitude'),
            'bmp_pressure': data.get('BMP', {}).get('pressure'),
            'bmp_temperature': data.get('BMP', {}).get('temperature'),
            'bmp_altitude': data.get('BMP', {}).get('altitude'),
            'uv_uva': data.get('UV', {}).get('UVA'),
            'uv_uvb': data.get('UV', {}).get('UVB'),
            'uv_uvc': data.get('UV', {}).get('UVC'),
            'uv_temperature': data.get('UV', {}).get('UV Temp'),
            'cpu_usage': data.get('System', {}).get('CPU Usage (%)'),
            'ram_usage': data.get('System', {}).get('RAM Usage (MB)'),
            'total_ram': data.get('System', {}).get('Total RAM (MB)'),
            'disk_usage': data.get('System', {}).get('Disk Usage (%)'),
            'disk_usage_gb': data.get('System', {}).get('Disk Usage (GB)'),
            'total_disk_gb': data.get('System', {}).get('Total Disk (GB)'),
            'sys_temperature': data.get('System', {}).get('Temperature (°C)'),
            'ds18b20_temperature_interior': ds18b20_temp_interior,
            'ds18b20_temperature_exterior': ds18b20_temp_exterior,
            'timestamp': data.get('timestamp')
        })

        connection.commit()
        logger.info("Datos insertados en la base de datos.")

    except (psycopg2.Error, Exception) as error:
        logger.error(f"Error al insertar en la base de datos: {error}")
        connection.rollback()

def receive_data_from_lora(lora_module, cursor, connection):
    buffer = ""
    start_marker = "<<<"
    end_marker = ">>>"

    while True:
        received_message = lora_module.receive_data()
        if received_message:
            buffer += received_message

            start_index = buffer.find(start_marker)
            end_index = buffer.find(end_marker)

            if start_index != -1 and end_index != -1 and end_index > start_index:
                complete_message = buffer[start_index + len(start_marker):end_index]
                logger.info(f"Mensaje JSON recibido: {complete_message}")

                try:
                    data_dict = json.loads(complete_message)
                    insert_data_to_db(cursor, connection, data_dict)
                except json.JSONDecodeError as e:
                    logger.error(f"Error al decodificar JSON: {e}")
                except Exception as e:
                    logger.error(f"Error inesperado al procesar el mensaje JSON: {e}")

                buffer = buffer[end_index + len(end_marker):]

        time.sleep(0.25)

def monitor_aux_pin(lora_module):
    low_time = None
    while True:
        if lora_module.aux.is_active:
            low_time = None
        else:
            if low_time is None:
                low_time = time.time()
            elif time.time() - low_time > 30:
                logger.error("El pin AUX ha estado en bajo por más de 30 segundos. Reiniciando el programa...")
                os.execl(sys.executable, sys.executable, *sys.argv)

        time.sleep(1)

def main():
    uart_port = None
    for vid, pid in VID_PID_LIST:
        uart_port = find_serial_port(vid, pid)
        if uart_port:
            break

    if uart_port is None:
        logger.error("Dispositivo no encontrado. Verifique las conexiones.")
        exit(1)

    logger.info(f"Dispositivo encontrado en {uart_port}, inicializando el módulo E220...")

    try:
        lora_module = E220(m0_pin=M0, m1_pin=M1, aux_pin=AUX, uart_port=uart_port)
        lora_module.set_mode(MODE_NORMAL)

        connection, cursor = connect_to_db()

        # Iniciar el hilo para monitorear el pin AUX
        aux_monitor_thread = threading.Thread(target=monitor_aux_pin, args=(lora_module,))
        aux_monitor_thread.daemon = True
        aux_monitor_thread.start()

        logger.info("Escuchando mensajes entrantes...")
        receive_data_from_lora(lora_module, cursor, connection)

    except KeyboardInterrupt:
        logger.info("Recepción interrumpida por el usuario.")
    except Exception as e:
        logger.error(f"Se produjo un error: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
        if lora_module:
            lora_module.close()
        logger.info("Puerto serial cerrado.")
        time.sleep(1)

if __name__ == "__main__":
    main()
