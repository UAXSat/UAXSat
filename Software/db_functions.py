"""- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - *

                         Developed by Javier Bolanos
                    https://github.com/javierbolanosllano

                           UAXSAT IV Project - 2024
                       https://github.com/UAXSat/UAXSat

* - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - """

# db_functions.py
import psycopg2
import logging

# Configuración del logger
logger = logging.getLogger(__name__)

def connect_to_db():

    """Conecta a la base de datos y retorna la conexión y el cursor."""
    
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
        logger.error(f"Error al conectar con la base de datos: {error}")
        return None, None

def insert_data_to_db(cursor, connection, data):

    """Inserta los datos recibidos en la base de datos.
    - data: Diccionario con los datos a insertar.
    - cursor: Cursor de la base de datos.
    - connection: Conexión a la base de datos.
    - Si hay un error, se hace rollback de la transacción."""

    try:
        logger.info("Insertando datos en la base de datos...")
        insert_query = """
        INSERT INTO sensor_readings (
            acelx, acely, acelz, girox, giroy, giroz,
            magx, magy, magz, uva, uvb, uvc, uv_temp,
            bmp_pressure, bmp_temperature, bmp_altitude, bmp_vertical_speed,
            dallas_intern, dallas_extern,
            gps_speed_mps, gps_gga_latitude, gps_gga_longitude, gps_distance,
            gps_altitude, gps_height_geoid, gps_satellites,
            gps_pdop, gps_hdop, gps_vdop,
            system_cpu_usage_percent, system_ram_usage_percent,
            system_temp_cpu_thermal, timestamp
        ) VALUES (
            %(acelx)s, %(acely)s, %(acelz)s, %(girox)s, %(giroy)s, %(giroz)s,
            %(magx)s, %(magy)s, %(magz)s, %(uva)s, %(uvb)s, %(uvc)s, %(uv_temp)s,
            %(bmp_pressure)s, %(bmp_temperature)s, %(bmp_altitude)s, %(bmp_vertical_speed)s,
            %(dallas_intern)s, %(dallas_extern)s,
            %(gps_speed_mps)s, %(gps_gga_latitude)s, %(gps_gga_longitude)s, %(gps_distance)s,
            %(gps_altitude)s, %(gps_height_geoid)s, %(gps_satellites)s,
            %(gps_pdop)s, %(gps_hdop)s, %(gps_vdop)s,
            %(system_cpu_usage_percent)s, %(system_ram_usage_percent)s,
            %(system_temp_cpu_thermal)s, %(timestamp)s
        );
        """

        # Función auxiliar para convertir valores a float
        def to_float(value):
            try:
                return float(value)
            except (TypeError, ValueError):
                return None

        # Mapeo de datos para la consulta
        data_map = {
            'acelx': data.get('IMU', {}).get('ACELX'),
            'acely': data.get('IMU', {}).get('ACELY'),
            'acelz': data.get('IMU', {}).get('ACELZ'),
            'girox': data.get('IMU', {}).get('GIROX'),
            'giroy': data.get('IMU', {}).get('GIROY'),
            'giroz': data.get('IMU', {}).get('GIROZ'),
            'magx': data.get('IMU', {}).get('MAGX'),
            'magy': data.get('IMU', {}).get('MAGY'),
            'magz': data.get('IMU', {}).get('MAGZ'),
            'uva': data.get('UV', {}).get('UVA'),
            'uvb': data.get('UV', {}).get('UVB'),
            'uvc': data.get('UV', {}).get('UVC'),
            'uv_temp': data.get('UV', {}).get('UV Temp'),
            'bmp_pressure': data.get('BMP', {}).get('pressure'),
            'bmp_temperature': data.get('BMP', {}).get('temperature'),
            'bmp_altitude': data.get('BMP', {}).get('altitude'),
            'bmp_vertical_speed': to_float(data.get('BMP', {}).get('vertical_speed')),
            'dallas_intern': data.get('Dallas', {}).get('28-03a0d446ef0a'),
            'dallas_extern': data.get('Dallas', {}).get('28-6fc2d44578f0'),
            'gps_speed_mps': to_float(data.get('GPS', {}).get('RMC', {}).get('speed_mps')),
            'gps_gga_latitude': to_float(data.get('GPS', {}).get('GGA', {}).get('latitude')),
            'gps_gga_longitude': to_float(data.get('GPS', {}).get('GGA', {}).get('longitude')),
            'gps_distance': to_float(data.get('GPS', {}).get('distance')),
            'gps_altitude': to_float(data.get('GPS', {}).get('GGA', {}).get('altitude')),
            'gps_height_geoid': to_float(data.get('GPS', {}).get('GGA', {}).get('height_geoid')),
            'gps_satellites': data.get('GPS', {}).get('GGA', {}).get('num_satellites'),
            'gps_pdop': to_float(data.get('GPS', {}).get('GSA', {}).get('pdop')),
            'gps_hdop': to_float(data.get('GPS', {}).get('GSA', {}).get('hdop')),
            'gps_vdop': to_float(data.get('GPS', {}).get('GSA', {}).get('vdop')),
            'system_cpu_usage_percent': data.get('System', {}).get('CPU_Usage'),
            'system_ram_usage_percent': data.get('System', {}).get('RAM_Usage'),
            'system_temp_cpu_thermal': data.get('System', {}).get('CPU_Temperature'),
            'timestamp': data.get('timestamp')
        }

        # Ejecutar la consulta de inserción
        cursor.execute(insert_query, data_map)
        connection.commit()
        logger.info("Datos insertados exitosamente en la base de datos.")

    except Exception as e:
        logger.error(f"Error al insertar datos en la base de datos: {e}")
        connection.rollback()