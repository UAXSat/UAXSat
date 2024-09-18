import serial
import time
from serial.tools import list_ports
from math import radians, sin, cos, sqrt, atan2

def haversine(lat1, lon1, lat2, lon2):
    """
    Calcula la distancia entre dos puntos dados por sus coordenadas (lat1, lon1) y (lat2, lon2).
    La distancia se devuelve en metros.
    """
    R = 6371000  # Radio de la Tierra en metros

    # Convertir grados a radianes
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Diferencias
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # F  rmula de haversine
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c

    return distance

def find_gps_port(description=None, hwid="1546:01A9"):
    """
    Encuentra el puerto del GPS basado en la descripci  n o el HWID proporcionado.
    """
    ports = list_ports.comports()
    for port in ports:
        if description and description in port.description:
            return port.device
        if hwid and hwid in port.hwid:
            return port.device
    raise Exception("GPS port not found")

def initialize_gps(port, baudrate=9600, timeout=1):
    """
    Inicializa la conexi  n con el GPS usando el puerto proporcionado.
    """
    try:
        serial_port = serial.Serial(port, baudrate=baudrate, timeout=timeout)
        return serial_port
    except serial.SerialException as e:
        raise Exception(f"Error al conectar con el puerto {port}: {e}")

def read_gps_data(gps_serial):
    """
    Lee datos del GPS desde el puerto serie.
    """
    try:
        gps_data = gps_serial.readline().decode('utf-8', errors='replace').strip()
        if gps_data.startswith('$'):
            return process_nmea(gps_data)
    except Exception as e:
        print(f"Error al leer datos del GPS: {e}")
    return None

def process_nmea(nmea_data):
    """
    Procesa datos NMEA y devuelve un diccionario con la informaci  n relevante.
    """
    parts = nmea_data.split(',')
    message_type = parts[0][3:]

    if message_type == 'GGA':
        return process_gga(parts)
    elif message_type == 'RMC':
        return process_rmc(parts)
    elif message_type == 'VTG':
        return process_vtg(parts)
    elif message_type == 'GSV':
        return process_gsv(parts)
    else:
        return {'type': message_type}  # A  ade el tipo de mensaje aunque no sea relevante

def nmea_to_decimal(coord, direction):
    """
    Convierte las coordenadas NMEA a formato decimal.
    """
    if not coord or not direction:
        return None

    if direction in ['N', 'S']:  # Latitud tiene 2 grados
        degrees = float(coord[:2])
        minutes = float(coord[2:])
    elif direction in ['E', 'W']:  # Longitud tiene 3 grados
        degrees = float(coord[:3])
        minutes = float(coord[3:])
    else:
        return None

    decimal = degrees + (minutes / 60)

    if direction in ['S', 'W']:
        decimal *= -1

    return decimal

def process_gga(parts):
    """
    Procesa el mensaje GGA y devuelve un diccionario con la informaci  n.
    """
    latitude = nmea_to_decimal(parts[2], parts[3])
    longitude = nmea_to_decimal(parts[4], parts[5])
    # Elimina el sufijo 'M' y convierte a float
    altitude = float(parts[9]) if parts[9] else None
    height_geoid = float(parts[11]) if parts[11] else None
    return {
        'type': 'GGA',
        'utc_time': parts[1],
        'latitude': latitude,
        'longitude': longitude,
        'altitude': altitude,
        'height_geoid': height_geoid
    }

def process_rmc(parts):
    """
    Procesa el mensaje RMC y devuelve un diccionario con la informaci  n.
    """
    latitude = nmea_to_decimal(parts[3], parts[4])
    longitude = nmea_to_decimal(parts[5], parts[6])
    speed_knots = float(parts[7]) if parts[7] else 0.0
    speed_mps = speed_knots * 0.514444  # Conversi  n de nudos a m/s
    return {
        'type': 'RMC',
        'utc_time': parts[1],
        #'latitude': latitude,
        #'longitude': longitude,
        'speed_mps': speed_mps
    }

def process_vtg(parts):
    """
    Procesa el mensaje VTG y devuelve un diccionario con la informaci  n.
    """
    return {
        'type': 'VTG',
        'speed_kmh': parts[7] if len(parts) > 7 else None
    }

def process_gsv(parts):
    """
    Procesa el mensaje GSV y devuelve un diccionario con la informaci  n.
    """
    return {
        'type': 'GSV',
        'total_satellites': int(parts[3]) if len(parts) > 3 else None
    }

def get_GPS_data(ref_lat=None, ref_lon=None, baudrate=9600, timeout=1, hwid="1546:01A9", description="None"):
    """
    Obtiene datos del GPS, busca el puerto, inicializa la conexi  n y lee los datos.
    """
    gps_data = {}
    serial_port = None

    try:
        # Encontrar el puerto del GPS
        port = find_gps_port(description, hwid)
        # Inicializar el GPS
        serial_port = initialize_gps(port, baudrate, timeout)

        while True:
            nmea_data = read_gps_data(serial_port)
            if nmea_data:
                message_type = nmea_data.get('type')
                if message_type in ['GGA', 'RMC', 'VTG', 'GSV']:
                    gps_data[message_type] = nmea_data
            if len(gps_data) == 4:  # Aseguramos que tenemos todos los tipos de mensajes necesarios
                break
        
        # Calcular la distancia a las coordenadas de referencia si est  n disponibles
        if ref_lat is not None and ref_lon is not None:
            current_lat = gps_data.get('GGA', {}).get('latitude')
            current_lon = gps_data.get('GGA', {}).get('longitude')
            if current_lat is not None and current_lon is not None:
                distance = haversine(current_lat, current_lon, ref_lat, ref_lon)
                gps_data['distance'] = distance

        return gps_data

    except KeyboardInterrupt:
        print("Lectura interrumpida.")
    finally:
        if serial_port and serial_port.is_open:
            serial_port.close()

if __name__ == "__main__":
    try:
        ref_lat = 40.7128  # Ejemplo de latitud de referencia
        ref_lon = -74.0060 # Ejemplo de longitud de referencia
        while True:
            gps_data = get_GPS_data(ref_lat=ref_lat, ref_lon=ref_lon)
            if gps_data:
                print("Datos GPS recopilados:")
                print(f"UTC Time: {gps_data.get('RMC', {}).get('utc_time')}")
                print(f"Latitude: {gps_data.get('GGA', {}).get('latitude')}")
                print(f"Longitude: {gps_data.get('GGA', {}).get('longitude')}")
                print(f"Altitude: {gps_data.get('GGA', {}).get('altitude')}")
                print(f"Height Geoid: {gps_data.get('GGA', {}).get('height_geoid')}")
                print(f"Speed (m/s): {gps_data.get('RMC', {}).get('speed_mps')}")
                print(f"Total Satellites: {gps_data.get('GSV', {}).get('total_satellites')}")
                print(f"Distance to Reference: {gps_data.get('distance')} meters")
            time.sleep(1)  # Espera un segundo antes de la siguiente lectura
    except KeyboardInterrupt:
        print("Lectura interrumpida por el usuario.")
    finally:
        print("Conexi  n con el GPS cerrada.")
