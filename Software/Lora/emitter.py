"""* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
*                                                                            *
*                         Developed by Javier Bolanos                        *
*                  https://github.com/javierbolanosllano                     *
*                                                                            *
*                      UAXSAT IV Project - 2024                              *
*                   https://github.com/UAXSat/UAXSat                         *
*                                                                            *
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *"""

# emitter.py
import serial
import time
import json
import logging
from gpiozero import DigitalOutputDevice, DigitalInputDevice

# Configuración del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar módulos de sensores
from Modules.IMUmodule import get_IMU_data
from Modules.UVmodule import get_UV_data
from Modules.BMPmodule import get_BMP_data
from Modules.DS18B20module import get_DS18B20_data
from Modules.GPSmodule import get_GPS_data
from Modules.SYSTEMmodule import get_system_data

# Definición de pines GPIO
M0_PIN = 17
M1_PIN = 27
AUX_PIN = 22

# Configuración del puerto serial
SERIAL_PORT = '/dev/ttyUSB0'  # Ajusta según tu sistema
BAUD_RATE = 9600  # Debe coincidir con la configuración del módulo LoRa

# Inicialización de los pines GPIO
m0 = DigitalOutputDevice(M0_PIN)
m1 = DigitalOutputDevice(M1_PIN)
aux = DigitalInputDevice(AUX_PIN, pull_up=True)

def wait_aux_high():
    """Espera hasta que el pin AUX esté en HIGH."""
    logger.debug("Esperando a que AUX esté en HIGH...")
    timeout = time.time() + 10  # Timeout de 10 segundos
    while not aux.value:
        logger.debug(f"Valor actual de AUX: {aux.value}")
        time.sleep(0.5)
        if time.time() > timeout:
            logger.error("Timeout esperando a que AUX esté en HIGH.")
            break
    if aux.value:
        logger.debug("AUX está en HIGH.")
    else:
        logger.error("No se pudo establecer comunicación con el módulo LoRa.")

def wait_aux_low():
    """Espera hasta que el pin AUX esté en LOW."""
    logger.debug("Esperando a que AUX esté en LOW...")
    while aux.value:
        time.sleep(0.01)
    logger.debug("AUX esta en LOW.")

def enter_normal_mode():
    """Configura el modulo LoRa en modo normal (transparente)."""
    logger.info("Configurando el modulo en modo NORMAL...")
    m0.off()
    m1.off()
    wait_aux_high()
    time.sleep(0.1)
    logger.info("Modulo configurado en modo NORMAL.")

def get_all_sensor_data():
    sensor_data = {}
    try:
        logger.info("Recolectando datos de sensores...")
        initial_lat = None  # Define tu latitud inicial si es necesario
        initial_lon = None  # Define tu longitud inicial si es necesario

        sensor_data['IMU'] = get_IMU_data()
        logger.debug(f"Datos de IMU: {sensor_data['IMU']}")

        sensor_data['UV'] = get_UV_data()
        logger.debug(f"Datos de UV: {sensor_data['UV']}")

        sensor_data['BMP'] = get_BMP_data()
        logger.debug(f"Datos de BMP: {sensor_data['BMP']}")

        sensor_data['Dallas'] = get_DS18B20_data()
        logger.debug(f"Datos de Dallas: {sensor_data['Dallas']}")

        sensor_data['GPS'] = get_GPS_data(initial_lat, initial_lon)
        logger.debug(f"Datos de GPS: {sensor_data['GPS']}")

        sensor_data['System'] = get_system_data()
        logger.debug(f"Datos del sistema: {sensor_data['System']}")

        sensor_data['timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S")
        logger.debug(f"Timestamp: {sensor_data['timestamp']}")

        logger.info("Datos de sensores recolectados exitosamente.")
        return sensor_data
    except Exception as e:
        logger.error(f"Error al obtener datos de sensores: {e}")
        return None

def serialize_sensor_data(sensor_data):
    try:
        logger.info("Serializando datos de sensores...")
        serialized_data = json.dumps(sensor_data)
        logger.debug(f"Datos serializados: {serialized_data}")
        return serialized_data
    except Exception as e:
        logger.error(f"Error al serializar datos: {e}")
        return None

def send_message(message):
    """Envía un mensaje a través de LoRa."""
    logger.info(f"Enviando mensaje: {message}")
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
        ser.write(message.encode('utf-8'))
        wait_aux_low()
        wait_aux_high()
    logger.info("Mensaje enviado.")

def send_sensor_data():
    sensor_data = get_all_sensor_data()
    if sensor_data:
        message_content = serialize_sensor_data(sensor_data)
        if message_content:
            # Envolver el mensaje con los marcadores <<< y >>>
            full_message = f'<<<{message_content}>>>'
            send_message(full_message)
        else:
            logger.error("No se pudieron serializar los datos.")
    else:
        logger.error("No se enviaron datos debido a un error en la recolección.")

def main():
    # Inicializar variables para evitar NameError en caso de interrupción
    global m0, m1, aux
    m0 = None
    m1 = None
    aux = None
    try:
        logger.info("Iniciando programa del emisor...")
        # Inicialización de los pines GPIO
        m0 = DigitalOutputDevice(M0_PIN)
        m1 = DigitalOutputDevice(M1_PIN)
        aux = DigitalInputDevice(AUX_PIN, pull_up=True)

        enter_normal_mode()
        while True:
            send_sensor_data()
            time.sleep(5)  # Espera 5 segundos antes de enviar nuevamente
    except KeyboardInterrupt:
        logger.info("Programa interrumpido por el usuario.")
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
    finally:
        logger.info("Finalizando programa del emisor. Limpiando GPIO...")
        if m0:
            m0.close()
        if m1:
            m1.close()
        if aux:
            aux.close()
        logger.debug("GPIO limpiado.")

if __name__ == '__main__':
    main()

