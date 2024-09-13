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

def get_GPS_data(baudrate=38400, timeout=1, hwid="1546:01A9", description=None):
    """
    Esta funci  n inicializa el GPS, extrae los datos y los devuelve en forma de diccionario.
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

        # Crear un diccionario con los datos
        gps_data = {
            "latitude": geo.lat if geo else None,
            "longitude": geo.lon if geo else None,
            "altitude": geo.height / 1000 if geo else None,
            "heading_of_motion": geo.headMot if geo else None,
            "roll": veh.roll if veh else None,
            "pitch": veh.pitch if veh else None,
            "heading": veh.heading if veh else None,
            "nmea_sentence": stream_nmea if stream_nmea else None,
            "high_precision_latitude": hp_geo.latHp if hp_geo else None,
            "high_precision_longitude": hp_geo.lonHp if hp_geo else None,
            "high_precision_altitude": hp_geo.heightHp / 1000 if hp_geo else None
        }

        return gps_data, None

    except Exception as e:
        # En caso de error, devuelve un mensaje de error
        return None