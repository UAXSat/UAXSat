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

        if nmea.startswith('$GNRMC'):
            return parse_rmc(parts)
        elif nmea.startswith('$GNVTG'):
            return parse_vtg(parts)
        elif nmea.startswith('$GNGGA'):
            return parse_gga(parts)
        elif nmea.startswith('$GNGSA'):
            return parse_gsa(parts)
        elif nmea.startswith('$GPGSV') or nmea.startswith('$GLGSV') or nmea.startswith('$GBGSV') or nmea.startswith('$GAGSV'):
            return parse_gsv(parts)
        elif nmea.startswith('$GNGLL'):
            return parse_gll(parts)
        else:
            return None, "Unknown sentence type"
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
        print(f"Error calculating checksum: {e}")
        time.sleep(5)
        return False

def parse_gga(parts):
    try:
        data = {
            'Sentence': 'GNGGA',
            'Time (UTC)': parts[1],
            'Latitude': nmea_to_decimal(parts[2], parts[3]),
            'Longitude': nmea_to_decimal(parts[4], parts[5]),
            'Fix Quality': parts[6],
            'Number of Satellites': parts[7],
            'Horizontal Dilution': parts[8],
            'Altitude': f"{parts[9]} {parts[10]}",
            'Height of Geoid': f"{parts[11]} {parts[12].split('*')[0]}"
        }
        return data, None
    except Exception as e:
        return None, f"Error parsing GGA: {e}"

def parse_rmc(parts):
    try:
        data = {
            'Sentence': 'GNRMC',
            'Time (UTC)': parts[1],
            'Status': parts[2],
            'Latitude': nmea_to_decimal(parts[3], parts[4]),
            'Longitude': nmea_to_decimal(parts[5], parts[6]),
            'Speed (knots)': parts[7],
            'Track Angle (degrees)': parts[8],
            'Date': parts[9],
            'Mode': parts[12].split('*')[0] if len(parts) > 12 else ""
        }
        return data, None
    except Exception as e:
        return None, f"Error parsing RMC: {e}"

def parse_vtg(parts):
    try:
        data = {
            'Sentence': 'GNVTG',
            'Track Degrees (True)': parts[1],
            'Track Degrees (Magnetic)': parts[3],
            'Speed (knots)': parts[5],
            'Speed (km/h)': parts[7].split('*')[0]
        }
        return data, None
    except Exception as e:
        return None, f"Error parsing VTG: {e}"

def parse_gsa(parts):
    try:
        data = {
            'Sentence': 'GNGSA',
            'Mode': parts[1],
            'Fix Type': parts[2],
            'Satellites Used': [s for s in parts[3:15] if s],
            'PDOP': parts[15],
            'HDOP': parts[16],
            'VDOP': parts[17].split('*')[0] if len(parts) > 17 else ""
        }
        return data, None
    except Exception as e:
        return None, f"Error parsing GSA: {e}"

def parse_gsv(parts):
    try:
        satellites_info = []
        for i in range(4, len(parts) - 4, 4):
            satellite_info = {
                'Satellite PRN': parts[i],
                'Elevation (degrees)': parts[i + 1],
                'Azimuth (degrees)': parts[i + 2],
                'SNR (dB)': parts[i + 3].split('*')[0] if '*' in parts[i + 3] else parts[i + 3]
            }
            satellites_info.append(satellite_info)
        data = {
            'Sentence': 'GSV',
            'Message Type': parts[0][1:4],
            'Number of Sentences': parts[1],
            'Sentence Number': parts[2],
            'Satellites in View': parts[3],
            'Satellites Info': satellites_info
        }
        return data, None
    except Exception as e:
        return None, f"Error parsing GSV: {e}"

def parse_gll(parts):
    try:
        data = {
            'Sentence': 'GNGLL',
            'Latitude': nmea_to_decimal(parts[1], parts[2]),
            'Longitude': nmea_to_decimal(parts[3], parts[4]),
            'Time (UTC)': parts[5],
            'Status': parts[6],
            'Mode': parts[7].split('*')[0] if len(parts) > 7 else ""
        }
        return data, None
    except Exception as e:
        return None, f"Error parsing GLL: {e}"

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
                            for key, value in data.items():
                                if key == 'Satellites Info':
                                    print(f"{key}:")
                                    for sat in value:
                                        for sat_key, sat_value in sat.items():
                                            print(f"    {sat_key}: {sat_value}")
                                else:
                                    print(f"{key}: {value}")
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
