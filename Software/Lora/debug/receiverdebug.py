# receiverdebug.py

import time
import json
import logging
import psycopg2
from serial.tools import list_ports
from e220 import E220, MODE_NORMAL, AUX, M0, M1, VID_PID_LIST

# Configuración del logger
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

def find_serial_port(vendor_id, product_id):
    """Encuentra y devuelve el puerto serial para un dispositivo con el VID y PID dados."""
    ports = list_ports.comports()
    for port in ports:
        if port.vid == vendor_id and port.pid == product_id:
            return port.device
    return None

def insert_data_to_db(data):
    """Inserta los datos en la base de datos PostgreSQL."""
    connection = None
    cursor = None
    try:
        connection = psycopg2.connect(
            database="cubesat",
            user="cubesat",
            password="cubesat",
            host="localhost",
            port="5432"
        )
        cursor = connection.cursor()
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
        cursor.execute(insert_query, data)
        connection.commit()
        logger.info("Datos insertados en la base de datos.")
    except psycopg2.Error as e:
        logger.error(f"Error al insertar en la base de datos: {e}")
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def main():
    uart_port = None
    for vid, pid in VID_PID_LIST:
        uart_port = find_serial_port(vid, pid)
        if uart_port:
            break

    if uart_port is None:
        logger.error("Dispositivo no encontrado. Por favor, verifica tus conexiones.")
        return

    logger.info(f"Dispositivo encontrado en {uart_port}, inicializando el módulo E220.")

    try:
        lora_module = E220(m0_pin=M0, m1_pin=M1, aux_pin=AUX, uart_port=uart_port)
        lora_module.set_mode(MODE_NORMAL)
        logger.info("Módulo en modo de operación normal.")
        buffer = ""

        while True:
            received_message = lora_module.receive_data()
            if received_message:
                buffer += received_message
                start_marker = "<<<"
                end_marker = ">>>"
                start_index = buffer.find(start_marker)
                end_index = buffer.find(end_marker)

                if start_index != -1 and end_index != -1 and end_index > start_index:
                    complete_message = buffer[start_index + len(start_marker):end_index]
                    try:
                        data_dict = json.loads(complete_message)
                        insert_data_to_db(data_dict)
                    except json.JSONDecodeError as e:
                        logger.error(f"Error al decodificar JSON: {e}")
                    except Exception as e:
                        logger.error(f"Error inesperado al procesar el mensaje JSON: {e}")
                    buffer = buffer[end_index + len(end_marker):]

            time.sleep(0.25)
    except KeyboardInterrupt:
        logger.info("Interrupción por teclado, saliendo del programa.")
    except Exception as e:
        logger.error(f"Se produjo un error inesperado: {e}")
    finally:
        if 'lora_module' in locals():
            lora_module.close()
            logger.info("Comunicación UART cerrada.")
        time.sleep(1)

if __name__ == "__main__":
    main()
