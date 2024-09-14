"""* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
*                                                                            *
*                         Developed by Javier Bolanos                        *
*                  https://github.com/javierbolanosllano                     *
*                                                                            *
*                      UAXSAT IV Project - 2024                              *
*                   https://github.com/UAXSat/UAXSat                         *
*                                                                            *
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *"""

#!/usr/bin/env python3

# emitter.py
import json
import time
from datetime import datetime
import logging
from serial.tools import list_ports
from e220 import E220
from constants import M0, M1, AUX, VID_PID_LIST, MODE_NORMAL, initial_lat, initial_lon

from Modules.IMUmodule import get_IMU_data
from Modules.UVmodule import get_UV_data
from Modules.BMPmodule import get_BMP_data
from Modules.DS18B20module import get_DS18B20_data
from Modules.GPSmodule import get_GPS_data
from Modules.SYSTEMmodule import get_system_data

# Configuración del logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

def find_serial_port(vendor_id, product_id):
    """Encuentra y devuelve el puerto serial para un dispositivo con el VID y PID dados."""
    ports = list_ports.comports()
    for port in ports:
        if port.vid == vendor_id and port.pid == product_id:
            return port.device
    return None

def get_all_sensor_data():
    """Recoge datos de todos los sensores conectados."""
    sensor_data = {}

    # Obtener datos de los diferentes sensores
    try:
        sensor_data['IMU'] = get_IMU_data()         # ICM20948
        sensor_data['UV'] = get_UV_data()           # AS7331
        sensor_data['BMP'] = get_BMP_data()         # BMP390
        sensor_data['Dallas'] = get_DS18B20_data()  # DS18B20
        sensor_data['GPS'] = get_GPS_data(initial_lat, initial_lon), # GPS NEO M9N
        sensor_data['System'] = get_system_data()   # Sistema (CPU, RAM...)
    except Exception as e:
        logger.error(f"Error al obtener datos de sensores: {e}")
        raise e

    return sensor_data

def initialize_lora_module():
    """Inicializa el módulo LoRa y lo pone en modo normal."""
    uart_port = None
    for vid, pid in VID_PID_LIST:
        uart_port = find_serial_port(vid, pid)
        if uart_port:
            break

    if uart_port is None:
        logger.error("Dispositivo no encontrado. Verifique las conexiones.")
        raise Exception("Dispositivo LoRa no encontrado")

    logger.info(f"Dispositivo LoRa encontrado en {uart_port}, inicializando el módulo E220...")

    try:
        lora_module = E220(m0_pin=M0, m1_pin=M1, aux_pin=AUX, uart_port=uart_port)
        lora_module.set_mode(MODE_NORMAL)
        logger.info("Módulo E220 en modo de operación normal.")
        return lora_module
    except Exception as e:
        logger.error(f"Error al inicializar el módulo LoRa: {e}")
        raise e

def send_data_loop(lora_module, interval=5):
    """Bucle principal para recopilar y enviar datos de sensores a través de LoRa."""
    while True:
        try:
            # Obtener todos los datos de los sensores
            all_sensor_data = get_all_sensor_data()

            # Añadir timestamp a los datos
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            all_sensor_data['timestamp'] = timestamp

            # Convertir los datos a formato JSON
            all_sensor_data_json = json.dumps(all_sensor_data)

            # Preparar el mensaje con los markers
            message = f"<<<{all_sensor_data_json}>>>"

            # Imprimir los datos en formato JSON con timestamp y markers
            logger.info(f"Datos a enviar: {message}")

            # Enviar los datos por LoRa
            lora_module.send_data(message)
            logger.info("Datos enviados correctamente.")

            # Pausa entre lecturas para evitar saturar la CPU
            time.sleep(interval)

        except Exception as e:
            logger.error(f"Error en el envío de datos: {e}")
            time.sleep(interval)  # Pausar antes de intentar de nuevo

def main():
    try:
        # Inicializar el módulo LoRa
        lora_module = initialize_lora_module()

        # Iniciar el bucle de envío de datos
        logger.info("Iniciando el envío de datos a tierra...")
        send_data_loop(lora_module, interval=5)

    except KeyboardInterrupt:
        logger.info("Programa interrumpido por el usuario.")
    except Exception as e:
        logger.error(f"Error fatal en la ejecución: {e}")
    finally:
        # Asegurarse de que el puerto serial se cierre correctamente
        if 'lora_module' in locals():
            lora_module.close()
        logger.info("Puerto serial cerrado correctamente.")

if __name__ == "__main__":
    main()
