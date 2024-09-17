#!/usr/bin/env python3

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
logger = logging.getLogger(__name__)

def find_serial_port(vendor_id, product_id):
    """Encuentra el puerto serial para el módulo LoRa basado en VID y PID."""
    ports = list_ports.comports()
    for port in ports:
        if port.vid == vendor_id and port.pid == product_id:
            return port.device
    return None

def initialize_lora_module():
    """Inicializa el módulo LoRa E220 y retorna la instancia."""
    for vid, pid in VID_PID_LIST:
        uart_port = find_serial_port(vid, pid)
        if uart_port:
            break
    else:
        logger.error("Dispositivo LoRa no encontrado. Verifique las conexiones.")
        raise Exception("Dispositivo LoRa no encontrado")

    logger.info(f"Dispositivo LoRa encontrado en {uart_port}, inicializando...")

    try:
        lora_module = E220(m0_pin=M0, m1_pin=M1, aux_pin=AUX, uart_port=uart_port)
        lora_module.set_mode(MODE_NORMAL)
        logger.info("Módulo E220 inicializado y configurado en modo normal.")
        return lora_module
    except Exception as e:
        logger.error(f"Error al inicializar el módulo LoRa: {e}")
        raise e

def get_all_sensor_data():
    """Obtiene datos de todos los sensores conectados."""
    logger.debug("Reuniendo datos de todos los sensores.")
    try:
        sensor_data = {
            'IMU': get_IMU_data(),
            'UV': get_UV_data(),
            'BMP': get_BMP_data(),
            'Dallas': get_DS18B20_data(),
            'GPS': get_GPS_data(initial_lat, initial_lon),
            'System': get_system_data()
        }
        logger.debug(f"Datos de sensores recolectados: {sensor_data}")
        return sensor_data
    except Exception as e:
        logger.error(f"Error al obtener datos de sensores: {e}")
        raise e

def main():
    try:
        # Inicializar el módulo LoRa
        lora_module = initialize_lora_module()

        while True:
            try:
                # Obtener datos de sensores y agregar timestamp
                sensor_data = get_all_sensor_data()
                sensor_data['timestamp'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

                # Convertir a JSON y enviar datos
                message = f"<<<{json.dumps(sensor_data)}>>>"
                logger.debug(f"Mensaje a enviar: {message}")
                lora_module.send_data(message)
                logger.info("Datos enviados correctamente.")

                # Esperar antes de la siguiente transmisión
                time.sleep(5)

            except Exception as e:
                logger.error(f"Error durante el envío de datos: {e}")
                time.sleep(5)  # Esperar antes de intentar nuevamente

    except KeyboardInterrupt:
        logger.info("Programa interrumpido por el usuario, saliendo.")
    except Exception as e:
        logger.error(f"Error fatal en la ejecución: {e}")
    finally:
        if 'lora_module' in locals():
            lora_module.close()
            logger.info("Puerto serial cerrado correctamente.")

if __name__ == "__main__":
    main()
