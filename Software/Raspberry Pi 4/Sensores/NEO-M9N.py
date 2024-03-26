"""*********************************************************************************************************
*                                                                                                          *
*                                     UAXSAT IV Project - 2024                                             *
*                                 Developed by Javier Bolaños Llano                                        *
*                                https://github.com/javierbolanosllano                                     *
*                                                                                                          *
*********************************************************************************************************"""

import serial
from ublox_gps import UbloxGps

# Inicializa la comunicación serial con el dispositivo GPS
# Especifica el dispositivo serial (por ejemplo, '/dev/ttyACM0') y configura la tasa de baudios y el tiempo de espera
port = serial.Serial('/dev/ttyACM0', baudrate=38400, timeout=0.5)

# Crea un objeto UbloxGps que permitirá acceder a los datos del GPS
gps = UbloxGps(port)

def get_geo_coords():
    """
    Obtiene las coordenadas geográficas del GPS NEO-M9N.
    
    Utiliza el método geo_coords() para obtener la ubicación actual y devuelve un diccionario
    con la longitud, la latitud y el rumbo del movimiento.
    
    :return: Un diccionario con las claves 'longitude', 'latitude', y 'heading_of_motion',
             que representan la longitud, latitud y el rumbo del movimiento, respectivamente.
    """
    try:
        geo = gps.geo_coords()  # Intenta leer las coordenadas geográficas
        return {
            "longitude": geo.lon,  # Longitud en grados
            "latitude": geo.lat,   # Latitud en grados
            "heading_of_motion": geo.headMot  # Rumbo del movimiento en grados
        }
    except Exception as e:
        print(f"Error al obtener las coordenadas geográficas: {e}")
        return None  # En caso de error, devuelve None

def close_port():
    """
    Cierra el puerto serial utilizado para la comunicación con el GPS.
    
    Es una buena práctica cerrar el puerto serial al finalizar la comunicación
    para liberar el recurso.
    """
    port.close()
