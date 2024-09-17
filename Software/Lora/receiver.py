#!/usr/bin/env python3

import json
import logging
import psycopg2
import time
from serial.tools import list_ports
from e220 import E220
from constants import M0, M1, AUX, VID_PID_LIST, MODE_NORMAL

# Configuración del logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def find_serial_port(vendor_id, product_id):
    """Encuentra el puerto serial para el módulo LoRa basado en VID y PID."""
    for port in list_ports.comports():
        if port.vid == vendor_id and port.pid == product_id:
            return port.device
    return None

def connect_to_db():
    """Conecta a la base de datos y retorna la conexión y cursor."""
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
        raise

def insert_data_to_db(cursor, connection, data):
    """Inserta los datos recibidos a la base de datos."""
    try:
        insert_query = """
        INSERT INTO sensor_readings (
            imu_acelx, imu_acely, imu_acelz, imu_girox, imu_giroy, imu_giroz,
            imu_magx, imu_magy, imu_magz, uv_uva, uv_uvb, uv_uvc, uv_uv_temp,
            bmp_pressure, bmp_temperature, bmp_altitude,
            dallas_28_3c01f0950010, dallas_28_072252732021,
            gps_rmc_latitude, gps_rmc_longitude, gps_rmc_speed_mps, gps_vtg_speed_kmh,
            gps_gga_latitude, gps_gga_longitude, gps_gga_altitude, gps_gga_height_geoid,
            gps_gsv_total_satellites, distance_to_ref,
            system_cpu_usage_percent, system_ram_usage_mb, system_total_ram_mb,
            system_disk_usage_percent, system_disk_usage_gb, system_total_disk_gb,
            system_temperature_celsius, timestamp
        ) VALUES (
            %(imu_acelx)s, %(imu_acely)s, %(imu_acelz)s, %(imu_girox)s, %(imu_giroy)s, %(imu_giroz)s,
            %(imu_magx)s, %(imu_magy)s, %(imu_magz)s, %(uv_uva)s, %(uv_uvb)s, %(uv_uvc)s, %(uv_uv_temp)s,
            %(bmp_pressure)s, %(bmp_temperature)s, %(bmp_altitude)s,
            %(dallas_28_3c01f0950010)s, %(dallas_28_072252732021)s,
            %(gps_rmc_latitude)s, %(gps_rmc_longitude)s, %(gps_rmc_speed_mps)s, %(gps_vtg_speed_kmh)s,
            %(gps_gga_latitude)s, %(gps_gga_longitude)s, %(gps_gga_altitude)s, %(gps_gga_height_geoid)s,
            %(gps_gsv_total_satellites)s, %(distance_to_ref)s,
            %(system_cpu_usage_percent)s, %(system_ram_usage_mb)s, %(system_total_ram_mb)s,
            %(system_disk_usage_percent)s, %(system_disk_usage_gb)s, %(system_total_disk_gb)s,
            %(system_temperature_celsius)s, %(timestamp)s
        );
        """
        # Mapa de datos para la consulta
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
            'uv_uva': data.get('UV', {}).get('UVA'),
            'uv_uvb': data.get('UV', {}).get('UVB'),
            'uv_uvc': data.get('UV', {}).get('UVC'),
            'uv_uv_temp': data.get('UV', {}).get('UV Temp'),
            'bmp_pressure': data.get('BMP', {}).get('pressure'),
            'bmp_temperature': data.get('BMP', {}).get('temperature'),
            'bmp_altitude': data.get('BMP', {}).get('altitude'),
            'dallas_28_3c01f0950010': data.get('Dallas', {}).get('28-3c01f0950010'),
            'dallas_28_072252732021': data.get('Dallas', {}).get('28-072252732021'),
            'gps_rmc_latitude': data.get('GPS', {}).get('RMC', {}).get('latitude'),
            'gps_rmc_longitude': data.get('GPS', {}).get('RMC', {}).get('longitude'),
            'gps_rmc_speed_mps': data.get('GPS', {}).get('RMC', {}).get('speed_mps'),
            'gps_vtg_speed_kmh': data.get('GPS', {}).get('VTG', {}).get('speed_kmh'),
            'gps_gga_latitude': data.get('GPS', {}).get('GGA', {}).get('latitude'),
            'gps_gga_longitude': data.get('GPS', {}).get('GGA', {}).get('longitude'),
            'gps_gga_altitude': data.get('GPS', {}).get('GGA', {}).get('altitude'),
            'gps_gga_height_geoid': data.get('GPS', {}).get('GGA', {}).get('height_geoid'),
            'gps_gsv_total_satellites': data.get('GPS', {}).get('GSV', {}).get('total_satellites'),
            'distance_to_ref': data.get('GPS', {}).get('distance'),
            'system_cpu_usage_percent': data.get('System', {}).get('CPU Usage (%)'),
            'system_ram_usage_mb': data.get('System', {}).get('RAM Usage (MB)'),
            'system_total_ram_mb': data.get('System', {}).get('Total RAM (MB)'),
            'system_disk_usage_percent': data.get('System', {}).get('Disk Usage (%)'),
            'system_disk_usage_gb': data.get('System', {}).get('Disk Usage (GB)'),
            'system_total_disk_gb': data.get('System', {}).get('Total Disk (GB)'),
            'system_temperature_celsius': data.get('System', {}).get('Temperature (\u00b0C)'),
            'timestamp': data.get('timestamp')
        })

        # Confirmar cambios
        connection.commit()
        logger.info("Datos insertados correctamente.")

    except Exception as e:
        logger.error(f"Error al insertar en la base de datos: {e}")
        connection.rollback()

def receive_data_from_lora(lora_module, cursor, connection):
    """Recibe datos del módulo LoRa y procesa los mensajes JSON."""
    buffer = ""
    start_marker, end_marker = "<<<", ">>>"

    while True:
        received_message = lora_module.receive_data()
        if received_message:
            buffer += received_message

            while True:
                start_index = buffer.find(start_marker)
                end_index = buffer.find(end_marker)

                if start_index != -1 and end_index != -1:
                    complete_message = buffer[start_index + len(start_marker):end_index].strip()
                    logger.info(f"Mensaje JSON recibido: {complete_message}")

                    try:
                        data_dict = json.loads(complete_message)
                        insert_data_to_db(cursor, connection, data_dict)
                    except json.JSONDecodeError as e:
                        logger.error(f"Error al decodificar JSON: {e}")
                    except Exception as e:
                        logger.error(f"Error inesperado al procesar el mensaje: {e}")

                    buffer = buffer[end_index + len(end_marker):]
                else:
                    break
        time.sleep(0.25)

def initialize_lora_module():
    """Inicializa el módulo LoRa y retorna su instancia."""
    for vid, pid in VID_PID_LIST:
        uart_port = find_serial_port(vid, pid)
        if uart_port:
            break
    else:
        logger.error("Módulo LoRa no encontrado. Verifique las conexiones.")
        sys.exit(1)

    logger.info(f"Módulo LoRa encontrado en {uart_port}, inicializando...")
    try:
        lora_module = E220(m0_pin=M0, m1_pin=M1, aux_pin=AUX, uart_port=uart_port)
        lora_module.set_mode(MODE_NORMAL)
        logger.info("Módulo LoRa inicializado en modo normal.")
        return lora_module
    except Exception as e:
        logger.error(f"Error al inicializar el módulo LoRa: {e}")
        raise

def main():
    try:
        # Inicializar el módulo LoRa
        lora_module = initialize_lora_module()

        # Conectar a la base de datos
        connection, cursor = connect_to_db()

        # Iniciar la recepción de datos
        logger.info("Esperando mensajes de datos...")
        receive_data_from_lora(lora_module, cursor, connection)

    except KeyboardInterrupt:
        logger.info("Recepción interrumpida por el usuario.")
    except Exception as e:
        logger.error(f"Error en la ejecución: {e}")
    finally:
        # Cerrar conexiones
        if cursor: cursor.close()
        if connection: connection.close()
        if lora_module: lora_module.close()
        logger.info("Conexiones cerradas correctamente.")
        time.sleep(1)

if __name__ == "__main__":
    main()
