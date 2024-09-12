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
import time
import psycopg2
from serial.tools import list_ports
from e220 import E220, MODE_NORMAL, AUX, M0, M1, VID_PID_LIST
import json
import logging

# Configuración del logger en nivel DEBUG
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

def find_serial_port(vendor_id, product_id):
    """Encuentra y devuelve el puerto serial para un dispositivo con el VID y PID dados"""
    logger.debug(f"Buscando puerto serial para VID: {vendor_id}, PID: {product_id}")
    ports = list_ports.comports()
    for port in ports:
        logger.debug(f"Comprobando puerto {port.device}, VID: {port.vid}, PID: {port.pid}")
        if port.vid == vendor_id and port.pid == product_id:
            logger.info(f"Puerto encontrado: {port.device}")
            return port.device
    logger.error("No se encontró el puerto serial.")
    return None

def insert_data_to_db(data):
    """Inserta los datos en la base de datos PostgreSQL"""
    try:
        logger.debug("Intentando conectarse a la base de datos...")
        connection = psycopg2.connect(
            database="sensor_data",
            user="cubesat",
            password="cubesat",
            host="localhost",
            port="5432"
        )
        cursor = connection.cursor()

        # Consulta de inserción
        insert_query = """
        INSERT INTO sensor_readings (
            acelx, acely, acelz, girox, giroy, giroz, magx, magy, magz,
            uva, uvb, uvc, uv_temp, cpu_usage, ram_usage, total_ram,
            disk_usage, disk_usage_gb, total_disk_gb, temperature,
            lat, lon, alt, headmot, roll, pitch, heading, NMEA,
            lat_hp, lon_hp, alt_hp, gps_error, pressure, bmp_temperature, bmp_altitude
        ) VALUES (
            %(acelx)s, %(acely)s, %(acelz)s, %(girox)s, %(giroy)s, %(giroz)s, %(magx)s, %(magy)s, %(magz)s,
            %(uva)s, %(uvb)s, %(uvc)s, %(uv_temp)s, %(cpu_usage)s, %(ram_usage)s, %(total_ram)s,
            %(disk_usage)s, %(disk_usage_gb)s, %(total_disk_gb)s, %(temperature)s,
            %(lat)s, %(lon)s, %(alt)s, %(headmot)s, %(roll)s, %(pitch)s, %(heading)s, %(NMEA)s,
            %(lat_hp)s, %(lon_hp)s, %(alt_hp)s, %(gps_error)s, %(pressure)s, %(bmp_temperature)s, %(bmp_altitude)s
        )
        """

        # Registro de los datos antes de la inserción
        logger.debug(f"Datos a insertar: {data}")

        # Ejecutar la consulta de inserción
        cursor.execute(insert_query, {
            'acelx': data.get('IMU', {}).get('ACELX'),
            'acely': data.get('IMU', {}).get('ACELY'),
            'acelz': data.get('IMU', {}).get('ACELZ'),
            'girox': data.get('IMU', {}).get('GIROX'),
            'giroy': data.get('IMU', {}).get('GIROY'),
            'giroz': data.get('IMU', {}).get('GIROZ'),
            'magx': data.get('IMU', {}).get('MAGX'),
            'magy': data.get('IMU', {}).get('MAGY'),
            'magz': data.get('IMU', {}).get('MAGZ'),
            'lat': data.get('GPS', {}).get('lat'),
            'lon': data.get('GPS', {}).get('lon'),
            'alt': data.get('GPS', {}).get('alt'),
            'headmot': data.get('GPS', {}).get('headmot'),
            'roll': data.get('GPS', {}).get('roll'),
            'pitch': data.get('GPS', {}).get('pitch'),
            'heading': data.get('GPS', {}).get('heading'),
            'NMEA': data.get('GPS', {}).get('NMEA'),
            'lat_hp': data.get('GPS', {}).get('lat_hp'),
            'lon_hp': data.get('GPS', {}).get('lon_hp'),
            'alt_hp': data.get('GPS', {}).get('alt_hp'),
            'gps_error': data.get('GPS', {}).get('gps_error'),
            'pressure': data.get('BMP', {}).get('pressure'),
            'bmp_temperature': data.get('BMP', {}).get('temperature'),
            'bmp_altitude': data.get('BMP', {}).get('altitude'),
            'uva': data.get('UV', {}).get('UVA'),
            'uvb': data.get('UV', {}).get('UVB'),
            'uvc': data.get('UV', {}).get('UVC'),
            'uv_temp': data.get('UV', {}).get('UV Temp'),
            'cpu_usage': data.get('System', {}).get('CPU Usage (%)'),
            'ram_usage': data.get('System', {}).get('RAM Usage (MB)'),
            'total_ram': data.get('System', {}).get('Total RAM (MB)'),
            'disk_usage': data.get('System', {}).get('Disk Usage (%)'),
            'disk_usage_gb': data.get('System', {}).get('Disk Usage (GB)'),
            'temperature': data.get('System', {}).get('Temperature (°C)')
        })

        # Confirmar los cambios en la base de datos
        connection.commit()
        logger.info("Datos insertados correctamente en la base de datos.")

    except Exception as error:
        logger.error(f"Error al insertar en la base de datos: {error}")
    finally:
        if connection:
            cursor.close()
            connection.close()

def main():
    uart_port = None
    logger.debug("Comenzando búsqueda de dispositivo LoRa...")
    for vid, pid in VID_PID_LIST:
        uart_port = find_serial_port(vid, pid)
        if uart_port:
            break

    if uart_port is None:
        logger.error("Dispositivo no encontrado. Por favor, verifica tus conexiones.")
        exit(1)

    logger.info(f"Dispositivo encontrado en {uart_port}, inicializando el módulo E220...")

    lora_module = None
    try:
        lora_module = E220(m0_pin=M0, m1_pin=M1, aux_pin=AUX, uart_port=uart_port)
        lora_module.set_mode(MODE_NORMAL)

        logger.info("Escuchando mensajes entrantes...")

        buffer = ""  # Buffer para almacenar datos recibidos

        while True:
            logger.debug("Esperando a recibir datos...")
            received_message = lora_module.receive_data()

            if received_message:
                logger.debug(f"Datos recibidos: {received_message}")
                buffer += received_message  # Añadir datos recibidos al buffer

                # Buscar el marcador de inicio y fin en el buffer
                start_marker = "<<<"
                end_marker = ">>>"
                start_index = buffer.find(start_marker)
                end_index = buffer.find(end_marker)

                # Procesar solo si se encuentra un mensaje completo
                if start_index != -1 and end_index != -1 and end_index > start_index:
                    logger.debug(f"Mensaje completo encontrado entre {start_index} y {end_index}.")
                    complete_message = buffer[start_index + len(start_marker):end_index]
                    logger.info(f"Mensaje JSON recibido: {complete_message}")

                    # Convertir el mensaje JSON a un diccionario
                    try:
                        data_dict = json.loads(complete_message)
                        logger.debug(f"Mensaje JSON decodificado: {data_dict}")
                    except json.JSONDecodeError as e:
                        logger.error(f"Error al decodificar JSON: {e}")
                        buffer = ""  # Reiniciar buffer en caso de error en el JSON
                        continue

                    # Insertar los datos en la base de datos
                    insert_data_to_db(data_dict)

                    # Limpiar el buffer hasta el fin del marcador procesado
                    buffer = buffer[end_index + len(end_marker):]
                else:
                    logger.debug("No se ha encontrado un mensaje completo aún.")

            time.sleep(0.5)  # Pequeña pausa para evitar alta carga en CPU

    except Exception as e:
        logger.error(f"Error al inicializar el módulo LoRa: {e}")

if __name__ == "__main__":
    main()
