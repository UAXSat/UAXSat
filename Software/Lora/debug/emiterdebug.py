# emiterdebug.py

import json
import time
import csv
import os
from datetime import datetime
from serial.tools import list_ports
from e220 import E220, MODE_NORMAL, AUX, M0, M1, VID_PID_LIST
from Modules.IMUmodule import get_IMU_data
from Modules.UVmodule import get_UV_data
from Modules.BMPmodule import get_BMP_data
from Modules.DS18B20module import get_DS18B20_data
from Modules.GPSmodule import get_GPS_data
from Modules.SYSTEMmodule import get_system_data
import logging

# Configuración del logger
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

def get_all_sensor_data():
    """Recoge datos de todos los sensores conectados."""
    sensor_data = {}

    try:
        sensor_data['IMU'] = get_IMU_data()
        sensor_data['UV'] = get_UV_data()
        sensor_data['BMP'] = get_BMP_data()
        sensor_data['Dallas'] = get_DS18B20_data()
        sensor_data['GPS'] = get_GPS_data()
        sensor_data['System'] = get_system_data()
    except Exception as e:
        logger.error(f"Error al recoger datos de los sensores: {e}")
    
    return sensor_data

def save_data_to_csv(data):
    """Guarda los datos de los sensores en un archivo CSV con fecha y hora."""
    timestamp = datetime.now().strftime('%Y-%m-%d')
    hour = datetime.now().strftime('%H-%M-%S')
    directory = f"/path/to/data/{timestamp}"

    if not os.path.exists(directory):
        os.makedirs(directory)

    file_name = os.path.join(directory, f"{hour}.csv")

    file_exists = os.path.isfile(file_name)
    headers = list(data.keys())

    try:
        with open(file_name, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=headers)

            if not file_exists:
                writer.writeheader()

            writer.writerow(data)
        logger.info(f"Datos guardados en {file_name}.")
    except Exception as e:
        logger.error(f"Error al guardar datos en CSV: {e}")

def main():
    uart_port = None
    for vid, pid in VID_PID_LIST:
        uart_port = find_serial_port(vid, pid)
        if uart_port:
            break

    if uart_port is None:
        logger.error("Dispositivo no encontrado. Por favor, verifica tus conexiones.")
        return

    logger.info(f"Dispositivo encontrado en {uart_port}, inicializando el módulo E220900T30D.")

    try:
        lora_module = E220(m0_pin=M0, m1_pin=M1, aux_pin=AUX, uart_port=uart_port)
        lora_module.set_mode(MODE_NORMAL)
        logger.info("Módulo en modo de operación normal.")

        while True:
            all_sensor_data = get_all_sensor_data()
            if all_sensor_data:
                save_data_to_csv(all_sensor_data)
                all_sensor_data_json = json.dumps(all_sensor_data, indent=4)
                logger.info(f"Datos recolectados: {all_sensor_data_json}")
                lora_module.send_data(all_sensor_data_json)
                logger.info("Datos enviados a la estación terrestre correctamente.")
            time.sleep(5)
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
