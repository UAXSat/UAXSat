import json
import time
import csv
import os
from datetime import datetime
from serial.tools import list_ports

from Modules.IMUmodule import get_IMU_data
from Modules.UVmodule import get_UV_data
from Modules.BMPmodule import get_BMP_data
from Modules.DS18B20module import get_DS18B20_data
from Modules.GPSmodule import get_GPS_data
from Modules.SYSTEMmodule import get_system_data

# Ruta base donde se guardarán las carpetas y archivos CSV
BASE_DIR = '/ruta/deseada/desde/root/sensores_data'

def get_all_sensor_data():
    """Recoge datos de todos los sensores conectados."""
    sensor_data = {}

    # Obtener datos de los diferentes sensores
    sensor_data['IMU'] = get_IMU_data()         # ICM20948
    sensor_data['UV'] = get_UV_data()           # AS7331
    sensor_data['BMP'] = get_BMP_data()         # BMP390
    sensor_data['Dallas'] = get_DS18B20_data()  # DS18B20
    sensor_data['GPS'] = get_GPS_data()         # GPS NEO M9N
    sensor_data['System'] = get_system_data()   # Sistema (CPU, RAM...)

    return sensor_data

def save_data_to_csv(data):
    """
    Guarda los datos de los sensores en un archivo CSV dentro de una carpeta con la fecha actual.
    
    Cada archivo se nombra con la hora de ejecución.
    """
    # Obtener la fecha y hora actual
    current_date = datetime.now().strftime('%Y-%m-%d')  # Formato: YYYY-MM-DD
    current_time = datetime.now().strftime('%H-%M-%S')  # Formato: HH-MM-SS
    
    # Crear el directorio basado en la fecha actual
    directory = os.path.join(BASE_DIR, current_date)
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Definir el nombre del archivo basado en la hora actual
    file_name = f"{current_time}.csv"
    file_path = os.path.join(directory, file_name)

    # Verificar si el archivo ya existe
    file_exists = os.path.isfile(file_path)

    # Definir el encabezado del CSV según las claves del diccionario de datos
    headers = list(data.keys())

    # Abrir el archivo en modo escritura o añadir si ya existe
    with open(file_path, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)

        # Si el archivo no existe, escribir la cabecera
        if not file_exists:
            writer.writeheader()

        # Escribir los datos de los sensores
        writer.writerow(data)

def main():
    """
    Función principal que recoge los datos de los sensores y los guarda en un CSV de forma continua.
    """
    try:
        while True:  # Bucle infinito para recoger y guardar datos
            # Obtener todos los datos de los sensores
            all_sensor_data = get_all_sensor_data()

            # Añadir un timestamp a los datos
            all_sensor_data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Guardar los datos de los sensores en un archivo CSV
            save_data_to_csv(all_sensor_data)

            # Imprimir los datos en formato JSON para verificar
            all_sensor_data_json = json.dumps(all_sensor_data, indent=4)
            print(f"{all_sensor_data_json}")

            # Pausa entre lecturas para evitar saturar la CPU (por ejemplo, cada 5 segundos)
            time.sleep(5)

    except KeyboardInterrupt:
        print("KeyboardInterrupt: Saliendo del programa.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
