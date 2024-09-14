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
    ports = list_ports.comports()
    for port in ports:
        if description and description in port.description:
            return port.device
        if hwid and hwid in port.hwid:
            return port.device
    raise Exception("GPS port not found")

def initialize_gps(port, baudrate, timeout):
    serial_port = serial.Serial(port, baudrate=baudrate, timeout=timeout)
    gps = UbloxGps(serial_port)
    return gps, serial_port

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

    # Fórmula de haversine
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c

    return distance

def get_GPS_data(initial_lat, initial_lon, baudrate=38400, timeout=1, hwid="1546:01A9", description=None):
    """
    Esta función inicializa el GPS, extrae los datos y calcula la distancia desde unas coordenadas iniciales.
    """
    try:
        # Encontrar el puerto del GPS
        port = find_gps_port(description, hwid)

        # Inicializar el GPS
        gps, serial_port = initialize_gps(port, baudrate, timeout)

        # Obtener datos GPS
        geo = gps.geo_coords()
        veh = gps.veh_attitude()
        stream_nmea = gps.stream_nmea()
        hp_geo = gps.hp_geo_coords()

        # Comprobar si se obtuvieron coordenadas GPS
        latitude = geo.lat if geo else None
        longitude = geo.lon if geo else None

        # Calcular la distancia desde las coordenadas iniciales
        if latitude is not None and longitude is not None:
            distance = haversine(initial_lat, initial_lon, latitude, longitude)
        else:
            distance = None

        # Crear un diccionario con los datos
        gps_data = {
            "latitude": latitude,
            "longitude": longitude,
            "altitude": geo.height / 1000 if geo else None,
            "heading_of_motion": geo.headMot if geo else None,
            "roll": veh.roll if veh else None,
            "pitch": veh.pitch if veh else None,
            "heading": veh.heading if veh else None,
            "nmea_sentence": stream_nmea if stream_nmea else None,
            "high_precision_latitude": hp_geo.latHp if hp_geo else None,
            "high_precision_longitude": hp_geo.lonHp if hp_geo else None,
            "high_precision_altitude": hp_geo.heightHp / 1000 if hp_geo else None,
            "distance": distance if latitude is not None and longitude is not None else None  
        }

        return gps_data, None

    except Exception as e:
        # En caso de error, devuelve un mensaje de error
        return None, str(e)
