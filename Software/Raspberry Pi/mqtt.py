import time
from bmp280 import get_temp_bmp280, get_press_bmp280, press_fixed_bmp280
from dallas_sensors import get_temp_ds18b20_interior, get_temp_ds18b20_exterior
from gpiozero import CPUTemperature
import json
import logging
import paho.mqtt.publish as publish

# Configuraci  n b  sica de logging
logging.basicConfig(filename='errores_sensores.log', level=logging.DEBUG,
                    format='%(asctime)s: %(levelname)s: %(message)s')

def log_status(sensor_name, status):
    """Imprime el estado del sensor y registra en el log."""
    status_message = f"{sensor_name}: {status}"
    print(status_message, end=" | ")
    if status == "OK":
        logging.info(status_message)
    else:
        logging.warning(status_message)

def prepare_sensor_data(readings):
    """Prepara los datos de los sensores para ser enviados."""
    sensors_data = {"fecha": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}
    for sensor, data in readings.items():
        sensors_data[sensor] = data if data else "Error"
    return sensors_data

def read_press_bmp(altitud=700):
    """Lee la presi  n y temperatura del sensor BMP280."""
    try:
        presion = get_press_bmp280()
        presion_nivel_mar = press_fixed_bmp280(altitud)
        log_status("Presion BMP280", "OK")
        return {"Presion Barom  trica": presion, "Presion Nivel Mar": presion_nivel_mar}
    except Exception as e:
        log_status("Presion BMP280", "Err")
        logging.error(f"Error al leer BMP280: {e}")
        return None

def read_temp():
    """Lee las temperaturas de varios sensores."""
    try:
        temp_ext = get_temp_ds18b20_exterior()
        temp_int = get_temp_ds18b20_interior()
        temp_bmp = get_temp_bmp280()
        log_status("Temperaturas", "OK")
        return {"Temp. Ext": temp_ext, "Temp. Int": temp_int, "Temp. BMP": temp_bmp}
    except Exception as e:
        log_status("Temperaturas", "Disconnected")
        logging.error(f"Error al leer Temperaturas: {e}")
        return None

def read_CPU():
    """Lee las temperaturas de varios sensores."""
    try:
        cpu = CPUTemperature().temperature
        log_status("CPUTemperature", "OK")
        return {"CPUTemperature": cpu}
    except Exception as e:
        log_status("CPUTemperature", "Err")
        logging.error(f"Error al leer CPUTemperature: {e}")
        return None

def read_sensors():
    """Consolida la lectura de todos los sensores."""
    readings = {
        "Presi  n BMP280": read_press_bmp(),
        "Temperaturas": read_temp(),
        "Temperatura CPU": read_CPU(),
    }
    return prepare_sensor_data(readings)

# Configuraci  n de MQTT y el intervalo entre lecturas de sensores
hostname_mqtt = "localhost"
intervalo = 2

if __name__ == "__main__":
    try:
        while True:
            mensaje_json = json.dumps(read_sensors())
            if mensaje_json:
                publish.single("sensores/data", mensaje_json, hostname=hostname_mqtt)
                print("Datos publicados con   xito.")
            else:
                print("No se pudo obtener datos de los sensores.")
            time.sleep(intervalo)
    except KeyboardInterrupt:
        print("Programa detenido manualmente.")
    except Exception as e:
        print(f"Error inesperado al publicar datos: {e}")
        logging.error(f"Error inesperado al publicar datos: {e}")
