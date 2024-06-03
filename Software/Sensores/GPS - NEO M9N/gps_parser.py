import serial
import pynmea2

class GPSData:
    def __init__(self):
        self.latitude = None
        self.longitude = None
        self.altitude = None
        self.speed_kmh = None
        self.datestamp = None
        self.timestamp = None
        self.satellites_used = []
        self.hdop = None
        self.vdop = None
        self.pdop = None
        self.quality = None

class GPSParser:
    def __init__(self, port='/dev/ttyACM1', baudrate=38400):
        self.port = serial.Serial(port, baudrate=baudrate, timeout=1)
        self.gps_data = GPSData()

    def parse_nmea_sentence(self, nmea_data):
        msg = pynmea2.parse(nmea_data)
        if isinstance(msg, pynmea2.types.talker.GGA):
            self.gps_data.latitude = msg.latitude
            self.gps_data.longitude = msg.longitude
            self.gps_data.altitude = msg.altitude
            self.gps_data.quality = msg.gps_qual
            self.gps_data.satellites_used = msg.num_sats
        elif isinstance(msg, pynmea2.types.talker.RMC):
            self.gps_data.speed_kmh = float(msg.spd_over_grnd) * 1.852 if msg.spd_over_grnd else None
            self.gps_data.datestamp = msg.datestamp
            self.gps_data.timestamp = msg.timestamp
        elif isinstance(msg, pynmea2.types.talker.GSA):
            self.gps_data.pdop = msg.pdop
            self.gps_data.hdop = msg.hdop
            self.gps_data.vdop = msg.vdop
            self.gps_data.satellites_used = [getattr(msg, f'sv_id{i:02}', '') for i in range(1, 13) if getattr(msg, f'sv_id{i:02}', '')]

    def run(self):
        try:
            while True:
                nmea_data = self.port.readline().decode('ascii', errors='replace').strip()
                if nmea_data.startswith('$'):
                    self.parse_nmea_sentence(nmea_data)
        finally:
            self.port.close()

    def get_gps_data(self):
        return self.gps_data

if __name__ == '__main__':
    gps_parser = GPSParser()
    gps_parser.run()
