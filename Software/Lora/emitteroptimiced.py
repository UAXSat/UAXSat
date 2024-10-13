# emitter.py

import serial
import time
import json
import logging
import RPi.GPIO as GPIO

# Importar funciones de PostgreSQL y de LoRa desde los módulos
from db_functions import connect_to_db, insert_data_to_db
from lora_functions import wait_aux_high, wait_aux_low, enter_normal_mode
from constants import M0_PIN, M1_PIN, AUX_PIN, initial_lat, initial_lon, SERIAL_PORT, BAUD_RATE

# Importar módulos de sensores
from Modules.IMUmodule import get_IMU_data
from Modules.UVmodule import get_UV_data
from Modules.BMPmodule import get_BMP_data
from Modules.DS18B20module import get_DS18B20_data
from Modules.GPSmodule import get_GPS_data
from Modules.SYSTEMmodule import get_system_data

# Configuración del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_all_sensor_data(initial_lat, initial_lon):
    sensor_data = {}
    try:
        logger.info("Recolectando datos de sensores...")

        sensor_data['IMU'] = get_IMU_data()
        logger.debug(f"Datos IMU: {sensor_data['IMU']}")

        sensor_data['UV'] = get_UV_data()
        logger.debug(f"Datos UV: {sensor_data['UV']}")

        sensor_data['BMP'] = get_BMP_data()
        logger.debug(f"Datos BMP: {sensor_data['BMP']}")

        sensor_data['Dallas'] = get_DS18B20_data()
        logger.debug(f"Datos Dallas: {sensor_data['Dallas']}")

        sensor_data['GPS'] = get_GPS_data(initial_lat, initial_lon)
        logger.debug(f"Datos GPS: {sensor_data['GPS']}")

        sensor_data['System'] = get_system_data()
        logger.debug(f"Datos del sistema: {sensor_data['System']}")

        sensor_data['timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        logger.debug(f"Timestamp: {sensor_data['timestamp']}")

        logger.info("Datos de sensores recolectados exitosamente.")
        return sensor_data
    except Exception as e:
        logger.error(f"Error obteniendo los datos de los sensores: {e}")
        return None

def serialize_sensor_data(sensor_data):
    try:
        logger.info("Serializando los datos de sensores...")
        serialized_data = json.dumps(sensor_data)
        logger.debug(f"Datos serializados: {serialized_data}")
        return serialized_data
    except Exception as e:
        logger.error(f"Error serializando los datos: {e}")
        return None

def send_message(message):
    """Envía un mensaje vía LoRa."""
    logger.info(f"Enviando mensaje: {message}")
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
            ser.write(message.encode('utf-8'))
            if not wait_aux_low():
                logger.error("Fallo al enviar el mensaje: AUX no bajó a LOW.")
                return
            if not wait_aux_high():
                logger.error("Fallo al enviar el mensaje: AUX no regresó a HIGH.")
                return
        logger.info("Mensaje enviado.")
    except serial.SerialException as e:
        logger.error(f"Error en la comunicación serial: {e}")
    except Exception as e:
        logger.error(f"Error inesperado al enviar el mensaje: {e}")

def send_sensor_data(cursor, connection, initial_lat, initial_lon):
    sensor_data = get_all_sensor_data(initial_lat, initial_lon)
    if sensor_data:
        message_content = serialize_sensor_data(sensor_data)
        if message_content:
            # Envuelve el mensaje con marcadores <<< y >>>
            full_message = f'<<<{message_content}>>>'
            send_message(full_message)
            # Guarda los datos en la base de datos
            insert_data_to_db(cursor, connection, sensor_data)
        else:
            logger.error("No se pudo serializar los datos.")
    else:
        logger.error("Datos no enviados debido a un error en la recolección.")

def main():
    connection = None
    cursor = None
    try:
        logger.info("Iniciando el programa emisor...")
        enter_normal_mode()
        connection, cursor = connect_to_db()
        if not connection or not cursor:
            logger.error("No se pudo establecer conexión con la base de datos.")
            return
        while True:
            send_sensor_data(cursor, connection, initial_lat, initial_lon)
            time.sleep(5)  # Espera 5 segundos antes de enviar nuevamente
    except KeyboardInterrupt:
        logger.info("Programa interrumpido por el usuario.")
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
    finally:
        if cursor:
            cursor.close()
            logger.debug("Cursor de la base de datos cerrado.")
        if connection:
            connection.close()
            logger.debug("Conexión a la base de datos cerrada.")
        logger.info("Terminando el programa emisor. Limpiando GPIO...")
        GPIO.cleanup()
        logger.debug("GPIO limpiado.")

if __name__ == '__main__':
    main()
