"""***************************************************************************
*                                                                            *
*                      UAXSAT IV Project - 2024                              *
*                  Developed by Javier Bolaños Llano                         *
*                 https://github.com/javierbolanosllano                      *
*                                                                            *
***************************************************************************"""

# neo_m9n.py
import serial
import time
from serial.tools import list_ports
from ublox_gps import UbloxGps

def find_serial_port():
    # Enumerar todos los puertos seriales disponibles
    ports = list_ports.comports()
    for port in ports:
        if 'ACM' in port.device or 'USB' in port.device:
            return port.device
    return None

def connect_gps():
    while True:
        port_name = find_serial_port()
        if port_name:
            try:
                port = serial.Serial(port_name, baudrate=38400, timeout=1)
                gps = UbloxGps(port)
                print(f"Connected to GPS on {port_name}")
                return port, gps
            except serial.SerialException:
                print(f"Failed to connect to {port_name}. Retrying in 5 seconds...")
                time.sleep(5)
        else:
            print("GPS device not found. Retrying in 5 seconds...")
            time.sleep(5)

def parse_nmea_sentence(nmea):
    try:
        data = {}
        if not valid_checksum(nmea):
            return None, "Invalid checksum"

        parts = nmea.split(',')

        if nmea.startswith('$GNGGA'):
            data = {
                'latitude': nmea_to_decimal(parts[2], parts[3]),
                'longitude': nmea_to_decimal(parts[4], parts[5])
            }
        elif nmea.startswith('$GNRMC'):
            data = {
                'latitude': nmea_to_decimal(parts[3], parts[4]),
                'longitude': nmea_to_decimal(parts[5], parts[6])
            }

        return data, None

    except Exception as e:
        return None, f"Error parsing sentence: {e}"

def valid_checksum(nmea_sentence):
    try:
        sentence, checksum = nmea_sentence.split('*')
        sentence = sentence[1:]  # Eliminar el símbolo de inicio $
        calc_checksum = 0
        for char in sentence:
            calc_checksum ^= ord(char)
        return f"{calc_checksum:01X}" == checksum.upper()
    
    except Exception as e:
        print(f"Error calculating checksum: {e}", nmea_sentence)
        time.sleep(5)
        return False

def nmea_to_decimal(coord, direction):
    try:
        if not coord or not direction:
            return None
        d, m = divmod(float(coord), 100)
        decimal = d + (m / 60)
        if direction in ['S', 'W']:
            decimal = -decimal
        return decimal
    except Exception as e:
        print(f"Error converting NMEA to decimal: {e}")
        return None

def run():
    try:
        port, gps = connect_gps()
        print("Listening for UBX Messages")
        while True:
            try:
                nmea_data = gps.stream_nmea().strip()
                print(f"Raw NMEA Data: {nmea_data}")  # Mostrar la cadena NMEA original

                for sentence in nmea_data.splitlines():
                    try:
                        data, error = parse_nmea_sentence(sentence)
                        if error:
                            print(f"Error parsing sentence: {error}")
                        else:
                            if 'latitude' in data and 'longitude' in data:
                                print(f"latitude: {data['latitude']}")
                                print(f"longitude: {data['longitude']}")
                                print()  # Línea en blanco para separar las sentencias
                    except Exception as e:
                        print(f"Error processing sentence: {e}")

            except (ValueError, IOError) as nmea_err:
                print("Error streaming NMEA data:", nmea_err)
                port, gps = connect_gps()

            except serial.SerialException as serial_err:
                print("Serial port error:", serial_err)
                port, gps = connect_gps()

    except KeyboardInterrupt:
        print("Exiting program.")
    
    finally:
        try:
            gps.close()
            port.close()
            print("Serial port closed.")
        except Exception as e:
            print(f"Error closing serial port: {e}")

def main():
    run()

if __name__ == '__main__':
    main()
