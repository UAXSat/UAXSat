import os
import time
import json
import csv
import logging
import paho.mqtt.client as mqtt

import sys
sys.path.append('../')  # Permite importar modulos de la carpeta vecinos

from Sensors.UVmodule import initialize_sensor as init_uv_sensor, read_sensor_data as read_uv_data
from Sensors.GPSmodule import GPSParser
from Sensors.IMUmodule import initialize_sensor as init_icm_sensor, read_sensor_data as read_imu_data
from Sensors.DS18B20module import DallasSensor
from Sensors.BMPmodule import initialize_sensor as init_bmp_sensor, read_sensor_data as read_bmp_data
from gpiozero import CPUTemperature
from psutil import cpu_percent, virtual_memory

# Configuración de MQTT
MQTT_BROKER = "192.168.1.70"  # Reemplaza con la dirección IP de tu broker MQTT
MQTT_PORT = 1883  # Puerto estándar para MQTT sin TLS
MQTT_TOPIC = "data"
MQTT_CLIENT_ID = "CubesatSensorClient"
MQTT_USERNAME = "your_username"
MQTT_PASSWORD = "your_password"

# Configuración de GPS
BAUDRATE = 38400
TIMEOUT = 1
DESCRIPTION = "u-blox GNSS receiver"
HWID = "1546:01A9"

# Función de conexión
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Conectado al broker MQTT")
        logging.info("Conectado al broker MQTT")
    else:
        print(f"Fallo en la conexión, código de error: {rc}")
        logging.error(f"Fallo en la conexión, código de error: {rc}")

# Función de desconexión
def on_disconnect(client, userdata, rc):
    print("Desconectado del broker MQTT")
    logging.info("Desconectado del broker MQTT")

# Configuración del cliente MQTT
client = mqtt.Client(client_id=MQTT_CLIENT_ID, protocol=mqtt.MQTTv311, userdata=None, transport="tcp", clean_session=True)
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.on_connect = on_connect
client.on_disconnect = on_disconnect

# Conexión al broker
client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
client.loop_start()

# Función para publicar datos
def publish_data(topic, payload):
    try:
        client.publish(topic, payload, qos=1)  # QoS 1 garantiza al menos una entrega
        print("Datos enviados exitosamente")
        logging.info("Datos enviados exitosamente")
    except Exception as e:
        print(f"Error al enviar datos: {e}")
        logging.error(f"Error al enviar datos: {e}")

# Configuración de intervalos de lectura y ruta del CSV
sensorReadingInterval = 2

def initialize_csv_folder():
    """Crea la carpeta 'csv' si no existe."""
    if not os.path.exists(csv_folder):
        os.makedirs(csv_folder)
        print(f"Carpeta '{csv_folder}' creada.")

def read_sensors(gps_parser):
    # Aquí debes definir cómo leer los datos de los sensores y devolverlos como un diccionario
    # Ejemplo ficticio:
    data = {
        "temperature": 25.0,
        "humidity": 50.0,
        "gps": gps_parser.read_gps_data()  # Supongamos que esta función existe
    }
    return data

def save_json_to_csv(json_data, csv_file_path):
    try:
        data = json.loads(json_data)

        # Check if the CSV file already exists
        file_exists = os.path.isfile(csv_file_path)

        with open(csv_file_path, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=data.keys())

            # If the file doesn't exist, write the header
            if not file_exists:
                writer.writeheader()

            # Write the data
            writer.writerow(data)
        
        logging.info(f"Data appended to {csv_file_path} successfully.")

    except Exception as e:
        logging.error(f"Error saving data to CSV: {e}")

# Función principal
if __name__ == "__main__":
    try:
        current_time = time.strftime("%H%M%S", time.localtime())
        current_date = time.strftime("%d%m%Y", time.localtime())

        csv_folder = f"CSV/{current_date}"
        initialize_csv_folder()
        csv_filename = f"data_{current_time}.csv"
        csv_file_path = os.path.join(csv_folder, csv_filename)

        gps_parser = GPSParser(BAUDRATE, TIMEOUT, description=DESCRIPTION, hwid=HWID)

        while True:
            logging.debug("Reading sensor data...")
            sensor_data = read_sensors(gps_parser)
            sensorDataJSON = json.dumps(sensor_data)

            if sensorDataJSON:
                # Publish the data via MQTT
                logging.debug(f"Publishing data via MQTT: {sensorDataJSON}")
                publish_data(MQTT_TOPIC, sensorDataJSON)

                # Save the JSON data to CSV
                logging.debug(f"Saving data to CSV: {sensorDataJSON}")
                save_json_to_csv(sensorDataJSON, csv_file_path)
                print(f"Data saved to {csv_filename} successfully.")
            else:
                print("Error sending data.")

            time.sleep(sensorReadingInterval)

    except KeyboardInterrupt:
        print("\n Program stopped by the user.")
    except Exception as e:
        logging.error(f"Unexpected error while publishing data: {e}")
        print(f"Unexpected error while publishing data: {e}")
    finally:
        client.loop_stop()
        client.disconnect()
