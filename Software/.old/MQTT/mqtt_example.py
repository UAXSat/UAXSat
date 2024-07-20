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
import mpu6050  # Importa el módulo para interactuar con el sensor MPU6050
import bmp280   # Importa el módulo para interactuar con el sensor BMP280
import neom9n   # Importa el módulo para interactuar con el sensor NEO-M9N GPS
import ds18b20  # Importa el módulo para interactuar con el sensor DS18B20
import paho.mqtt.publish as publish  # Importa el módulo para publicar mensajes MQTT

logging.basicConfig(filename='errores_sensores.log', level=logging.DEBUG,
                    format='%(asctime)s: %(levelname)s: %(message)s')

def clear_screen():
    """Limpia la pantalla de la consola."""
    os.system('cls' if os.name == 'nt' else 'clear')

def log_status(sensor_name, status):
    """
    Imprime el estado del sensor con colores en la consola y registra en el log.

    Parámetros:
    - sensor_name: Nombre del sensor (string).
    - status: Estado del sensor ('OK' o 'Disconnected') (string).

    Usa colores para la salida en consola: verde para 'OK', rojo para 'Disconnected'.
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

def read_mpu6050():
    """
    Intenta leer los datos del sensor MPU6050, incluyendo temperatura, aceleración y giroscopio.
    """
    try:
        mpu = mpu6050.create_mpu_instance(0x68)
        log_status("MPU6050", "OK")
        mpu_temp = mpu.get_temp()
        mpu_accel = mpu.get_accel_data(g=False)
        mpu_gyro = mpu.get_gyro_data()
        return {"temperatura": mpu_temp, "aceleracion": mpu_accel, "giro": mpu_gyro}
    except Exception as e:
        log_status("MPU6050", "Disconnected")
        return None

def read_bmp280():
    """
    Intenta leer los datos del sensor BMP280, incluyendo temperatura, la presión y altura.
    Registra el estado del sensor (conectado o desconectado).
    """
    try:
        bmp_temp = bmp280.get_temperature()
        bmp_press = bmp280.get_pressure()
        bmp_alt = bmp280.get_altitude()
        log_status("BMP280", "OK")
        return {"temperatura": bmp_temp, "presion": bmp_press, "altura": bmp_alt}
    except Exception as e:
        log_status("BMP280", "Disconnected")
        return None

def read_neom9n():
    try:
        geo_coords = neom9n.get_geo_coords()
        log_status("NEOM9N", "OK")
        return {"Coordenadas": geo_coords}
    except Exception as e:
        log_status("NEOM9N", "Disconnected")
        return None

def read_ds18b20():
    try:
        ds18b20_temp = ds18b20.read_temp()
        log_status("DS18B20", "OK")
        return {"temperatura": ds18b20_temp}
    except Exception as e:
        log_status("DS18B20", "Disconnected")
        return None

def prepare_sensor_data(readings):
    sensors_data = {"fecha": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}
    for sensor, data in readings.items():
        sensors_data[sensor] = data if data else "Error"
    return sensors_data

def read_sensors():
    readings = {
        "MPU6050": read_mpu6050(),
        "BMP280": read_bmp280(),
        "NEOM9N": read_neom9n(),
        "DS18B20": read_ds18b20(),
    }
    return prepare_sensor_data(readings)

# Configuración de MQTT y el intervalo entre lecturas de sensores
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