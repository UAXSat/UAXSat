"""*********************************************************************************************************
*                                                                                                          *
*                                     UAXSAT IV Project - 2024                                             *
*                       Developed by Javier Bolaños Llano and Javier Lendinez                              *
*                                https://github.com/UAXSat                                                 *
*                                                                                                          *
*********************************************************************************************************"""

import os
import time
import json
import logging

# Importar los módulos de los sensores
import bmp390
import icm20948
import neo_m9n as neom9n
import ds18b20
#from dallassensor import get_temp_ds18b20_interior, get_temp_ds18b20_exterior
from gpiozero import CPUTemperature

import paho.mqtt.publish as publish  # Importa el módulo para publicar mensajes MQTT

logging.basicConfig(filename='errores_sensores.log', level=logging.DEBUG,
                    format='%(asctime)s: %(levelname)s: %(message)s')

def clear_screen():
    """Limpia la pantalla de la consola."""
    os.system('cls' if os.name == 'nt' else 'clear')

def log_status(sensor_name, status):
    """
    Imprime el estado del sensor y registra en el log.

    Parámetros:
    - sensor_name: Nombre del sensor (string).
    - status: Estado del sensor ('OK' o 'Disconnected') (string).

    Verde: 'OK'
    Rojo:  'Disconnected'
    """

    RED     = "\033[91m"
    GREEN   = "\033[92m"
    RESET   = "\033[0m"
    status_message = f"{sensor_name}: {status}"
    if status == "OK":
        print(f"{GREEN}{status_message}{RESET}", end=" | ")
        logging.info(status_message)
    else:
        print(f"{RED}{status_message}{RESET}", end=" | ")
        logging.warning(status_message)

## Funciones para leer los datos de los sensores
def read_icm20948():
    """
    Intenta leer los datos del sensor ICM20948, incluyendo temperatura, aceleración y giroscopio.
    """
    try:
        imu = icm20948.create_imu_instance(0x68)
        log_status("ICM20948", "OK")
        imu_mag = imu.read_magnetic()
        imu_accel = imu.read_acceleration(g=False)
        imu_gyro = imu.read_gyro()
        return {"magnetic": imu_mag, "acceleration": imu_accel, "gyro": imu_gyro}
    except Exception as e:
        log_status("ICM20948", "Disconnected")
        return None

def read_bmp390():
    """
    Intenta leer los datos del sensor BMP390, incluyendo temperatura, la presión y altura.
    Registra el estado del sensor (conectado o desconectado).
    """
    try:
        bmp_temp = bmp390.read_temperature()
        bmp_press = bmp390.read_pressure()
        bmp_alt = bmp390.read_altitude()
        log_status("BMP390", "OK")
        return {"temperature": bmp_temp, "presion": bmp_press, "altitude": bmp_alt}
    except Exception as e:
        log_status("BMP390", "Disconnected")
        return None

def read_neom9n():
    try:
        geo_coords = neom9n.get_geo_coords()
        log_status("NEOM9N", "OK")
        return {geo_coords}
    except Exception as e:
        log_status("NEOM9N", "Disconnected")
        return None

def read_ds18b20():
    try:
        ds18b20_temp = ds18b20.read_temp()
        log_status("DS18B20", "OK")
        return {ds18b20_temp}
    except Exception as e:
        log_status("DS18B20", "Disconnected")
        return None

def read_CPU():
    """Lee las temperaturas de varios sensores."""
    try:
        cpu = CPUTemperature().temperature
        log_status("CPUTemperature", "OK")
        return {cpu}
    except Exception as e:
        log_status("CPUTemperature", "Err")
        logging.error(f"Error al leer CPUTemperature: {e}")
        return None

## Prepara los datos de los sensores para ser enviados
def prepare_sensor_data(readings):
    sensors_data = {"fecha": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}
    for sensor, data in readings.items():
        sensors_data[sensor] = data if data else "Error"
    return sensors_data

def read_sensors():
    readings = {
        "ICM20948": read_icm20948(),
        "BMP390": read_bmp390(),
        "NEOM9N": read_neom9n(),
        "DS18B20": read_ds18b20(),
        "CPUTemp": read_CPU(),
    }
    return prepare_sensor_data(readings)

## Configuración de MQTT y el intervalo entre lecturas de sensores
hostname_mqtt = "localhost"
intervalo = 2

if __name__ == "__main__":
    try:
        while True:
            clear_screen()
            mensaje_json = json.dumps(read_sensors())
            if mensaje_json:
                publish.single("sensores/data", mensaje_json, hostname=hostname_mqtt)
                print("Datos publicados con éxito.")
            else:
                print("No se pudo obtener datos de los sensores.")
            time.sleep(intervalo)
    except KeyboardInterrupt:
        print("Programa detenido manualmente.")
    except Exception as e:
        print(f"Error inesperado al publicar datos: {e}")