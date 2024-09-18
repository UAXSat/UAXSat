#!/usr/bin/env python3

import serial
import time
import json
import psycopg2
import logging
from gpiozero import DigitalOutputDevice, DigitalInputDevice

# Configuración del logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Definición de pines GPIO
M0_PIN = 17
M1_PIN = 27
AUX_PIN = 22

# Configuración del puerto serial
SERIAL_PORT = '/dev/ttyUSB0'  # Ajusta según tu sistema
BAUD_RATE = 9600

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
    logger.debug("AUX está en LOW.")

def enter_normal_mode():
    """Configura el módulo LoRa en modo normal (transparente)."""
    logger.info("Configurando el módulo en modo NORMAL...")
    m0.off()
    m1.off()
    wait_aux_high()
    time.sleep(0.1)
    logger.info("Módulo configurado en modo NORMAL.")

def connect_to_db():
    """Conecta a la base de datos y retorna la conexión y cursor."""
    try:
        logger.info("Conectando a la base de datos...")
        connection = psycopg2.connect(
            database="cubesat",
            user="cubesat",
            password="cubesat",
            host="localhost",
            port="5432"
        )
        cursor = connection.cursor()
        logger.info("Conexión a la base de datos establecida.")
        return connection, cursor
    except psycopg2.Error as error:
        logger.error(f"Error al conectar a la base de datos: {error}")
        raise

def insert_data_to_db(cursor, connection, data):
    """Inserta los datos recibidos a la nueva tabla."""
    try:
        logger.info("Insertando datos en la base de datos...")
        insert_query = """
        INSERT INTO sensor_readings (
            imu_acelx, imu_acely, imu_acelz, imu_girox, imu_giroy, imu_giroz,
            imu_magx, imu_magy, imu_magz, uv_uva, uv_uvb, uv_uvc, uv_uv_temp,
            bmp_pressure, bmp_temperature, bmp_altitude,
            dallas_28_03a0d446ef0a, dallas_28_6fc2d44578f0,
            gps_rmc_utc_time, gps_rmc_speed_mps, gps_vtg_speed_kmh,
            gps_gga_utc_time, gps_gga_latitude, gps_gga_longitude,
            gps_gga_altitude, gps_gga_height_geoid, gps_gsv_total_satellites,
            system_cpu_usage_percent, system_ram_usage_percent,
            system_temp_cpu_thermal, system_temp_rp1_adc,
            system_temp_w1_slave_temp_1, system_temp_w1_slave_temp_2,
            system_fan_pwmfan_rpm, timestamp
        ) VALUES (
            %(imu_acelx)s, %(imu_acely)s, %(imu_acelz)s, %(imu_girox)s, %(imu_giroy)s, %(imu_giroz)s,
            %(imu_magx)s, %(imu_magy)s, %(imu_magz)s, %(uv_uva)s, %(uv_uvb)s, %(uv_uvc)s, %(uv_uv_temp)s,
            %(bmp_pressure)s, %(bmp_temperature)s, %(bmp_altitude)s,
            %(dallas_28_03a0d446ef0a)s, %(dallas_28_6fc2d44578f0)s,
            %(gps_rmc_utc_time)s, %(gps_rmc_speed_mps)s, %(gps_vtg_speed_kmh)s,
            %(gps_gga_utc_time)s, %(gps_gga_latitude)s, %(gps_gga_longitude)s,
            %(gps_gga_altitude)s, %(gps_gga_height_geoid)s, %(gps_gsv_total_satellites)s,
            %(system_cpu_usage_percent)s, %(system_ram_usage_percent)s,
            %(system_temp_cpu_thermal)s, %(system_temp_rp1_adc)s,
            %(system_temp_w1_slave_temp_1)s, %(system_temp_w1_slave_temp_2)s,
            %(system_fan_pwmfan_rpm)s, %(timestamp)s
        );
        """

        # Función auxiliar para convertir valores a float
        def to_float(value):
            try:
                return float(value)
            except (TypeError, ValueError):
                return None

        # Mapa de datos para la consulta
        data_map = {
            'imu_acelx': data.get('IMU', {}).get('ACELX'),
            'imu_acely': data.get('IMU', {}).get('ACELY'),
            'imu_acelz': data.get('IMU', {}).get('ACELZ'),
            'imu_girox': data.get('IMU', {}).get('GIROX'),
            'imu_giroy': data.get('IMU', {}).get('GIROY'),
            'imu_giroz': data.get('IMU', {}).get('GIROZ'),
            'imu_magx': data.get('IMU', {}).get('MAGX'),
            'imu_magy': data.get('IMU', {}).get('MAGY'),
            'imu_magz': data.get('IMU', {}).get('MAGZ'),
            'uv_uva': data.get('UV', {}).get('UVA'),
            'uv_uva': data.get('UV', {}).get('UVA'),
            'uv_uvb': data.get('UV', {}).get('UVB'),
            'uv_uvc': data.get('UV', {}).get('UVC'),
            'uv_uv_temp': data.get('UV', {}).get('UV Temp'),
            'bmp_pressure': data.get('BMP', {}).get('pressure'),
            'bmp_temperature': data.get('BMP', {}).get('temperature'),
            'bmp_altitude': data.get('BMP', {}).get('altitude'),
            'dallas_28_03a0d446ef0a': data.get('Dallas', {}).get('28-03a0d446ef0a'),
            'dallas_28_6fc2d44578f0': data.get('Dallas', {}).get('28-6fc2d44578f0'),
            'gps_rmc_utc_time': data.get('GPS', {}).get('RMC', {}).get('utc_time'),
            'gps_rmc_speed_mps': to_float(data.get('GPS', {}).get('RMC', {}).get('speed_mps')),
            'gps_vtg_speed_kmh': to_float(data.get('GPS', {}).get('VTG', {}).get('speed_kmh')),
            'gps_gga_utc_time': data.get('GPS', {}).get('GGA', {}).get('utc_time'),
            'gps_gga_latitude': to_float(data.get('GPS', {}).get('GGA', {}).get('latitude')),
            'gps_gga_longitude': to_float(data.get('GPS', {}).get('GGA', {}).get('longitude')),
            'gps_gga_altitude': to_float(data.get('GPS', {}).get('GGA', {}).get('altitude')),
            'gps_gga_height_geoid': to_float(data.get('GPS', {}).get('GGA', {}).get('height_geoid')),
            'gps_gsv_total_satellites': data.get('GPS', {}).get('GSV', {}).get('total_satellites'),
            'system_cpu_usage_percent': data.get('System', {}).get('CPU Usage (%)'),
            'system_ram_usage_percent': data.get('System', {}).get('RAM Usage (%)'),
            'system_temp_cpu_thermal': data.get('System', {}).get('Sensors', {}).get('Temperatures', {}).get('cpu_thermal', [{}])[0].get('Current'),
            'system_temp_rp1_adc': data.get('System', {}).get('Sensors', {}).get('Temperatures', {}).get('rp1_adc', [{}])[0].get('Current'),
            'system_temp_w1_slave_temp_1': data.get('System', {}).get('Sensors', {}).get('Temperatures', {}).get('w1_slave_temp', [{}])[0].get('Current'),
            'system_temp_w1_slave_temp_2': data.get('System', {}).get('Sensors', {}).get('Temperatures', {}).get('w1_slave_temp', [{}])[1].get('Current') if len(data.get('System', {}).get('Sensors', {}).get('Temperatures', {}).get('w1_slave_temp', [])) > 1 else None,
            'system_fan_pwmfan_rpm': data.get('System', {}).get('Sensors', {}).get('Fans', {}).get('pwmfan', [{}])[0].get('Current RPM'),
            'timestamp': data.get('timestamp')
        }

        logger.debug(f"Datos a insertar: {data_map}")

        cursor.execute(insert_query, data_map)
        connection.commit()
        logger.info("Datos insertados correctamente en la base de datos.")

    except Exception as e:
        logger.error(f"Error al insertar en la base de datos: {e}")
        connection.rollback()

def receive_message():
    """Recibe mensajes a través de LoRa y procesa los datos entre marcadores."""
    buffer = ""
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
        logger.info("Puerto serial abierto para recepción.")
        while True:
            if ser.in_waiting > 0:
                chunk = ser.read(ser.in_waiting).decode('utf-8', errors='replace')
                buffer += chunk
                logger.debug(f"Buffer actualizado: {buffer}")

                # Procesar los mensajes completos
                while '<<<' in buffer and '>>>' in buffer:
                    start = buffer.find('<<<') + 3
                    end = buffer.find('>>>', start)
                    if end != -1:
                        message_content = buffer[start:end]
                        buffer = buffer[end+3:]  # Actualizar el buffer
                        logger.debug(f"Mensaje completo extraído: {message_content}")
                        try:
                            data = json.loads(message_content)
                            logger.info("Datos de sensores recibidos y deserializados.")
                            logger.debug(f"Datos deserializados: {data}")
                            insert_data_to_db(cursor, connection, data)
                        except json.JSONDecodeError as e:
                            logger.error(f"Error al deserializar el mensaje: {e}")
                    else:
                        break  # Esperar a que llegue el resto del mensaje
            else:
                time.sleep(0.1)

def main():
    global connection, cursor
    connection = None
    cursor = None
    try:
        logger.info("Iniciando programa del receptor...")
        enter_normal_mode()
        connection, cursor = connect_to_db()
        receive_message()
    except KeyboardInterrupt:
        logger.info("Programa interrumpido por el usuario.")
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
    finally:
        if cursor:
            cursor.close()
            logger.debug("Cursor de base de datos cerrado.")
        if connection:
            connection.close()
            logger.debug("Conexión a la base de datos cerrada.")
        logger.info("Finalizando programa del receptor. Limpiando GPIO...")
        m0.close()
        m1.close()
        aux.close()
        logger.debug("GPIO limpiado.")

if __name__ == '__main__':
    main()

