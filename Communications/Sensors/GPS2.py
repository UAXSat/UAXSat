#GPS2.py
import serial
from serial.tools import list_ports
from ublox_gps import UbloxGps

class GPSHandler:
    def __init__(self, baudrate, timeout, description=None, hwid=None):
        self.baudrate = baudrate
        self.timeout = timeout
        self.description = description
        self.hwid = hwid
        self.port = self.find_gps_port(description, hwid)
        self.serial_port = None
        self.gps = None
        self.initialize_gps()

    def find_gps_port(self, description, hwid):
        ports = list_ports.comports()
        for port in ports:
            if description and description in port.description:
                return port.device
            if hwid and hwid in port.hwid:
                return port.device
        return None

    def initialize_gps(self):
        if not self.port:
            raise Exception("GPS port not found.")
        self.serial_port = serial.Serial(self.port, baudrate=self.baudrate, timeout=self.timeout)
        self.gps = UbloxGps(self.serial_port)

    def get_location(self):
        if not self.gps or not self.serial_port or not self.serial_port.is_open:
            self.initialize_gps()  # Re-initialize GPS if not properly initialized
        try:
            geo = self.gps.geo_coords()
            return {'Longitude': geo.lon, 'Latitude': geo.lat, 'Heading': geo.headMot}
        except (ValueError, IOError) as err:
            return {"Error": str(err)}
