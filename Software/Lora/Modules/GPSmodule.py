"""* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
*                                                                            *
*                         Developed by Javier Bolanos                        *
*                  https://github.com/javierbolanosllano                     *
*                                                                            *
*                      UAXSAT IV Project - 2024                              *
*                   https://github.com/UAXSat/UAXSat                         *
*                                                                            *
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *"""

# GPSmodule.py
import serial
from serial.tools import list_ports
from ublox_gps import UbloxGps
from math import radians, sin, cos, sqrt, atan2

def find_gps_port(description=None, hwid=None):
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

def initialize_gps(port, baudrate, timeout):
    """
    Inicializa la conexi  n con el GPS usando el puerto proporcionado.
    """
    try:
        serial_port = serial.Serial(port, baudrate=baudrate, timeout=timeout)
        gps = UbloxGps(serial_port)
        return gps, serial_port
    except serial.SerialException as e:
        raise Exception(f"Error al conectar con el puerto {port}: {e}")

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

def get_GPS_data(initial_lat=None, initial_lon=None, baudrate=38400, timeout=1, hwid="1546:01A9", description=None):
    """
    Esta funci  n inicializa el GPS, extrae los datos y calcula la distancia desde unas coordenadas iniciales.
    """
    serial_port = None
    try:
        # Encontrar el puerto del GPS
        port = find_gps_port(description, hwid)

        # Inicializar el GPS
        gps, serial_port = initialize_gps(port, baudrate, timeout)

        # Obtener datos GPS
        geo = gps.geo_coords()

        # Comprobar si se obtuvieron coordenadas GPS
        latitude = geo.lat if geo else None
        longitude = geo.lon if geo else None

        # Calcular la distancia desde las coordenadas iniciales
        if latitude is not None and longitude is not None and initial_lat is not None and initial_lon is not None:
            distance = haversine(initial_lat, initial_lon, latitude, longitude)
        else:
            distance = None

        # Crear un diccionario con los datos
        gps_data = {
            "latitude": latitude,
            "longitude": longitude,
            "heading_of_motion": geo.headMot if geo else None,
            "distance": distance
        }

        return gps_data

    except Exception as e:
        raise Exception(f"Error al obtener datos del GPS: {e}")

    finally:
        # Asegurarse de cerrar el puerto serial si fue abierto
        if serial_port and serial_port.is_open:
            serial_port.close()

