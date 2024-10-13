import serial
import time
import json
import logging
import RPi.GPIO as GPIO

# Importar funciones de PostgreSQL y de LoRa desde los módulos
from db_functions import *
from lora_functions import *
from constants import *

# Configuración del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_message(message):
    """Limpia caracteres no válidos de un mensaje JSON."""
    return message.replace('\n', '').replace('\r', '').replace('\t', '').replace('\x00', '')

def receive_message(cursor, connection):
    """Recibe mensajes vía LoRa y procesa los datos entre marcadores."""
    buffer = ""
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
            logger.info("Puerto serial abierto para recepción.")
            while True:
                if ser.in_waiting > 0:
                    chunk = ser.read(ser.in_waiting).decode('utf-8', errors='ignore').strip()
                    buffer += chunk
                    logger.debug(f"Buffer actualizado: {buffer}")

                    # Procesar mensajes completos
                    while '<<<' in buffer and '>>>' in buffer:
                        start = buffer.find('<<<') + 3
                        end = buffer.find('>>>', start)
                        if end != -1:
                            message_content = buffer[start:end]
                            buffer = buffer[end+3:]  # Actualizar el buffer
                            logger.debug(f"Mensaje completo extraído: {message_content}")
                            try:
                                # Limpiar y deserializar mensaje
                                cleaned_message = clean_message(message_content)
                                logger.info(f"Mensaje limpio extraído: {cleaned_message}")
                                data = json.loads(cleaned_message)
                                logger.info("Datos del sensor recibidos y deserializados.")
                                logger.debug(f"Datos deserializados: {data}")
                                insert_data_to_db(cursor, connection, data)  # Usar función del módulo
                            except json.JSONDecodeError as e:
                                logger.error(f"Error al deserializar el mensaje: {e}")
                                logger.error(f"Mensaje problemático: {message_content}")
                        else:
                            break  # Esperar el resto del mensaje
                else:
                    time.sleep(0.1)
    except serial.SerialException as e:
        logger.error(f"Error en la comunicación serial: {e}")
    except Exception as e:
        logger.error(f"Error inesperado en receive_message: {e}")

def main():
    try:
        logger.info("Iniciando el programa receptor...")
        enter_normal_mode()
        connection, cursor = connect_to_db()  # Usar función del módulo
        receive_message(cursor, connection)
    except KeyboardInterrupt:
        logger.info("Programa interrumpido por el usuario.")
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
            logger.debug("Cursor de la base de datos cerrado.")
        if 'connection' in locals() and connection:
            connection.close()
            logger.debug("Conexión a la base de datos cerrada.")
        logger.info("Terminando el programa receptor. Limpiando GPIO...")
        GPIO.cleanup()
        logger.debug("GPIO limpiado.")

if __name__ == '__main__':
    main()
