import os
import time
import json
import logging
import paho.mqtt.publish as publish  # Importa el módulo para publicar mensajes MQTT

from UVmodule import initialize_sensor as init_uv_sensor, read_sensor_data as read_uv_data
from neo_m9n import connect_gps, parse_nmea_sentence
from icm20948 import ICM20948Sensor
from ds18b20 import DallasSensor
from bmp390 import BMP3XXSensor

logging.basicConfig(filename='errores_sensores.log', level=logging.DEBUG,
                    format='%(asctime)s: %(levelname)s: %(message)s')

csv_folder = 'csv'  # Nombre de la carpeta donde se guardar   el CSV

def initialize_csv_folder():
    """Crea la carpeta 'csv' si no existe."""
    if not os.path.exists(csv_folder):
        os.makedirs(csv_folder)
        print(f"Carpeta '{csv_folder}' creada.")

def write_to_csv(data, filename):
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())
        writer.writeheader()
        writer.writerow(data)

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
    RED = "\033[91m"
    GREEN = "\033[92m"
    RESET = "\033[0m"
    status_message = f"{sensor_name}: {status}"
    if status == "OK":
        print(f"{GREEN}{status_message}{RESET}", end=" | ")
        logging.info(status_message)
    else:
        print(f"{RED}{status_message}{RESET}", end=" | ")
        logging.warning(status_message)

def read_uv_sensor():
    try:
        sensor = init_uv_sensor()
        uv_data = read_uv_data(sensor)
        log_status("UV Sensor", "OK")
        return uv_data
    except Exception as e:
        log_status("UV Sensor", "Disconnected")
        return None

def read_gps_sensor():
    try:
        port, gps = connect_gps()
        data = None
        while not data:
            nmea_data = gps.stream_nmea().strip()
            for sentence in nmea_data.splitlines():
                data, error = parse_nmea_sentence(sentence)
                if data:
                    log_status("GPS Sensor", "OK")
                    return data
        log_status("GPS Sensor", "Disconnected")
    except Exception as e:
        log_status("GPS Sensor", "Disconnected")
        return None

def read_icm20948_sensor():
    try:
        icm20948 = ICM20948Sensor()
        sensor_data = icm20948.read_all()
        log_status("ICM20948", "OK")
        return sensor_data
    except Exception as e:
        log_status("ICM20948", "Disconnected")
        return None

def read_dallas_sensor():
    try:
        dallas_sensor = DallasSensor()
        sensor_info = dallas_sensor.get_sensor_info()
        if sensor_info:
            log_status("DallasSensor", "OK")
            return sensor_info
        else:
            log_status("DallasSensor", "Disconnected")
            return None
    except Exception as e:
        log_status("DallasSensor", "Disconnected")
        return None

def read_bmp3xx_sensor():
    try:
        bmp3xx_sensor = BMP3XXSensor()
        sensor_data = bmp3xx_sensor.read_all()
        log_status("BMP3XX", "OK")
        return sensor_data
    except Exception as e:
        log_status("BMP3XX", "Disconnected")
        return None

def prepare_sensor_data(readings):
    sensors_data = {"fecha": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}
    for sensor, data in readings.items():
        sensors_data[sensor] = data if data else "Error"
    return sensors_data

def read_sensors():
    readings = {
        "UV Sensor": read_uv_sensor(),
        "GPS Sensor": read_gps_sensor(),
        "ICM20948": read_icm20948_sensor(),
        "DallasSensor": read_dallas_sensor(),
        "BMP3XX": read_bmp3xx_sensor(),
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

            # Generar el nombre del archivo CSV con la fecha y hora actual
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            filename = os.path.join(csv_folder, f'sensor_data_{timestamp}.csv')

            if mensaje_json:
                publish.single("sensores/data", mensaje_json, hostname=hostname_mqtt)
                print("Datos publicados con exito.")
            else:
                print("No se pudo obtener datos de los sensores.")
            time.sleep(intervalo)
    except KeyboardInterrupt:
        print("Programa detenido manualmente.")
    except Exception as e:
        print(f"Error inesperado al publicar datos: {e}")
