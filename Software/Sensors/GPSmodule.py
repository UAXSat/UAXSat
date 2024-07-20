"""* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
*                                                                            *
*                    Developed by Javier Lendínez                            *
*                    https://github.com/javilendi                            *
*                                                                            *
*                      UAXSAT IV Project - 2024                              *
*                   https://github.com/UAXSat/UAXSat                         *
*                                                                            *
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *"""


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

    def GPSprogram(self):
        if not self.gps or not self.serial_port or not self.serial_port.is_open:
            self.initialize_gps()  # Re-initialize GPS if not properly initialized
        try:
            while True:
                data = {
                    'Latitude': None,
                    'Longitude': None,
                    'Altitude': None,
                    'Heading of Motion': None,
                    'Roll': None,
                    'Pitch': None,
                    'Heading': None,
                    'NMEA Sentence': None,
                }

                geo = self.gps.geo_coords()
                veh = self.gps.veh_attitude()
                stream_nmea = self.gps.stream_nmea()
                hp_geo = self.gps.hp_geo_coords()

                if geo is not None:
                    data['Latitude'] = geo.lat
                    data['Longitude'] = geo.lon
                    data['Altitude'] = geo.height/1000
                    data['Heading of Motion'] = geo.headMot

                if veh is not None:
                    data['Roll'] = veh.roll
                    data['Pitch'] = veh.pitch
                    data['Heading'] = veh.heading

                if stream_nmea is not None:
                    data['NMEA Sentence'] = stream_nmea

                if hp_geo is not None:
                    data['Latitude'] = hp_geo.latHp
                    data['Longitude'] = hp_geo.lonHp
                    data['Altitude'] = hp_geo.heightHp/1000
                
                return data
                    
        except (ValueError, IOError) as err:
            return {"Error": str(err)}
        
if __name__ == '__main__':
    import sys
    gps_handler = GPSHandler(baudrate=38400, timeout=1, description=None, hwid="1546:01A9")
    try:
        while True:
            gps_handler.GPSprogram()  # Add a small delay to prevent CPU overuse
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
    
    