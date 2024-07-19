"""* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
*                                                                            *
*                    Developed by Javier Bolaños                             *
*                 https://github.com/javierbolanosllano                      *
*                                                                            *
*                      UAXSAT IV Project - 2024                              *
*                   https://github.com/UAXSat/UAXSat                         *
*                                                                            *
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *"""

# GPSmodule.py
import serial
from ublox_gps import UbloxGps
from serial.tools import list_ports

class GPSParser:
    def __init__(self, baudrate, timeout, description=None, hwid=None):
        self.baudrate = baudrate
        self.timeout = timeout
        self.description = description
        self.hwid = hwid
        self.port = self.find_gps_port(description, hwid)
        self.gps, self.serial_port = self.initialize_gps()

    def find_gps_port(self, description, hwid):
        """
        Encuentra el puerto serial basado en la descripción o HWID.
        """
        ports = list_ports.comports()
        for port in ports:
            if description and description in port.description:
                return port.device
            if hwid and hwid in port.hwid:
                return port.device
        print("No se encontró el puerto serial con la descripción o HWID proporcionados.")
        return None

    def initialize_gps(self):
        """
        Inicializa el puerto serie y el objeto GPS.
        """
        if not self.port:
            return None, None
        try:
            serial_port = serial.Serial(self.port, baudrate=self.baudrate, timeout=self.timeout)
            gps = UbloxGps(serial_port)
            return gps, serial_port
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
            return None, None

    def valid_checksum(self, nmea_sentence):
        sentence, checksum = nmea_sentence.split('*')
        sentence = sentence[1:]  # Eliminar el símbolo de inicio $
        calc_checksum = 0
        for char in sentence:
            calc_checksum ^= ord(char)
        return f"{calc_checksum:02X}" == checksum.upper()

    def parse_nmea_sentence(self, nmea):
        if not self.valid_checksum(nmea):
            return None, "Invalid checksum"

        parts = nmea.split(',')

        parsers = {
            '$GNRMC': self.parse_rmc,
            '$GNVTG': self.parse_vtg,
            '$GNGGA': self.parse_gga,
            '$GNGSA': self.parse_gsa,
            '$GPGSV': self.parse_gsv,
            '$GLGSV': self.parse_gsv,
            '$GBGSV': self.parse_gsv,
            '$GAGSV': self.parse_gsv,
            '$GNGLL': self.parse_gll,
        }

        sentence_type = parts[0]
        parser = parsers.get(sentence_type)
        if parser:
            return parser(parts)
        else:
            return None, "Unknown sentence type"

    def parse_gga(self, parts):
        return {
            'Sentence': 'GNGGA',
            'Time (UTC)': parts[1],
            'Latitude': self.nmea_to_decimal(parts[2], parts[3]),
            'Longitude': self.nmea_to_decimal(parts[4], parts[5]),
            'Fix Quality': parts[6],
            'Number of Satellites': parts[7],
            'Horizontal Dilution': parts[8],
            'Altitude': f"{parts[9]} {parts[10]}",
            'Height of Geoid': f"{parts[11]} {parts[12].split('*')[0]}"
        }, None

    def parse_rmc(self, parts):
        return {
            'Sentence': 'GNRMC',
            'Time (UTC)': parts[1],
            'Status': parts[2],
            'Latitude': self.nmea_to_decimal(parts[3], parts[4]),
            'Longitude': self.nmea_to_decimal(parts[5], parts[6]),
            'Speed (knots)': parts[7],
            'Track Angle (degrees)': parts[8],
            'Date': parts[9],
            'Mode': parts[12].split('*')[0] if len(parts) > 12 else ""
        }, None

    def parse_vtg(self, parts):
        return {
            'Sentence': 'GNVTG',
            'Track Degrees (True)': parts[1],
            'Track Degrees (Magnetic)': parts[3],
            'Speed (knots)': parts[5],
            'Speed (km/h)': parts[7].split('*')[0]
        }, None

    def parse_gsa(self, parts):
        return {
            'Sentence': 'GNGSA',
            'Mode': parts[1],
            'Fix Type': parts[2],
            'Satellites Used': [s for s in parts[3:15] if s],
            'PDOP': parts[15],
            'HDOP': parts[16],
            'VDOP': parts[17].split('*')[0] if len(parts) > 17 else ""
        }, None

    def parse_gsv(self, parts):
        satellites_info = []
        for i in range(4, len(parts) - 4, 4):
            satellite_info = {
                'Satellite PRN': parts[i],
                'Elevation (degrees)': parts[i + 1],
                'Azimuth (degrees)': parts[i + 2],
                'SNR (dB)': parts[i + 3].split('*')[0] if '*' in parts[i + 3] else parts[i + 3]
            }
            satellites_info.append(satellite_info)
        return {
            'Sentence': 'GSV',
            'Message Type': parts[0][1:4],
            'Number of Sentences': parts[1],
            'Sentence Number': parts[2],
            'Satellites in View': parts[3],
            'Satellites Info': satellites_info
        }, None

    def parse_gll(self, parts):
        return {
            'Sentence': 'GNGLL',
            'Latitude': self.nmea_to_decimal(parts[1], parts[2]),
            'Longitude': self.nmea_to_decimal(parts[3], parts[4]),
            'Time (UTC)': parts[5],
            'Status': parts[6],
            'Mode': parts[7].split('*')[0] if len(parts) > 7 else ""
        }, None

    def nmea_to_decimal(self, coord, direction):
        if not coord or not direction:
            return None
        d, m = divmod(float(coord), 100)
        decimal = d + (m / 60)
        if direction in ['S', 'W']:
            decimal = -decimal
        return decimal

    def read_nmea_data(self):
        try:
            nmea_data = self.gps.stream_nmea().strip()
            return nmea_data
        except (ValueError, IOError) as e:
            print(f"Error reading NMEA data: {e}")
            return None

    def extract_relevant_data(self, nmea_data):
        extracted_data = {
            'Latitude': None,
            'Longitude': None,
            'Altitude': None,
            'Satellites in View': None,
            'Elevation': None,
            'Azimuth': None,
            'Time (UTC)': None
        }
        for sentence in nmea_data.splitlines():
            data, error = self.parse_nmea_sentence(sentence)
            if error:
                print(f"Error parsing sentence: {error}")
                continue
            
            if 'Latitude' in data and 'Longitude' in data:
                extracted_data['Latitude'] = data['Latitude']
                extracted_data['Longitude'] = data['Longitude']
            if 'Altitude' in data:
                extracted_data['Altitude'] = data['Altitude']
            if 'Satellites in View' in data:
                extracted_data['Satellites in View'] = data['Satellites in View']
            if 'Elevation (degrees)' in data:
                extracted_data['Elevation'] = data['Elevation (degrees)']
            if 'Azimuth (degrees)' in data:
                extracted_data['Azimuth'] = data['Azimuth (degrees)']
            if 'Time (UTC)' in data:
                extracted_data['Time (UTC)'] = data['Time (UTC)']
        
        return extracted_data

    def close(self):
        if self.serial_port:
            self.serial_port.close()
            print("Serial port closed.")

"""
# main.py
from GPSmodule import GPSParser

BAUDRATE = 38400
TIMEOUT = 1
DESCRIPTION = "u-blox GNSS receiver"
HWID = "1546:01A9"

def main():
    gps_parser = GPSParser(BAUDRATE, TIMEOUT, description=DESCRIPTION, hwid=HWID)
    if not gps_parser.gps or not gps_parser.serial_port:
        return
    
    print("Listening for UBX Messages. Press Ctrl+C to exit.")
    try:
        while True:
            nmea_data = gps_parser.read_nmea_data()
            if nmea_data:
                print(f"Raw NMEA Data: {nmea_data}")
                extracted_data = gps_parser.extract_relevant_data(nmea_data)
                print(f"Extracted Data: {extracted_data}")
    except KeyboardInterrupt:
        print("Exiting program.")
    finally:
        gps_parser.close()

if __name__ == '__main__':
    main()
"""
