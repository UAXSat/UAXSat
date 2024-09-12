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
    Esta función inicializa el GPS, extrae los datos y los devuelve en forma de tupla.
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

        # Devuelve los datos como una tupla
        return (
            geo.lat,                # Latitude
            geo.lon,                # Longitude
            geo.height / 1000,      # Altitude
            geo.headMot,            # Heading of Motion
            veh.roll,               # Roll
            veh.pitch,              # Pitch
            veh.heading,            # Heading
            stream_nmea,            # NMEA Sentence
            hp_geo.latHp,           # High Precision Latitude
            hp_geo.lonHp,           # High Precision Longitude
            hp_geo.heightHp / 1000  # High Precision Altitude
        )

    except Exception as e:
        # En caso de error, devuelve una tupla con None y el mensaje de error
        return (None, None, None, None, None, None, None, None, None, None, None, f"Error: {str(e)}")
