import serial
from ublox_gps import UbloxGps
from serial.tools import list_ports

class GPSManager:
    def __init__(self, baudrate=38400, timeout=1, description=None, hwid=1546:01A9):
        self.baudrate = baudrate
        self.timeout = timeout
        self.description = description
        self.hwid = hwid
        self.port = self.find_gps_port(description, hwid)
        self.gps, self.serial_port = self.initialize_gps()

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
            return None, None
        try:
            serial_port = serial.Serial(self.port, baudrate=self.baudrate, timeout=self.timeout)
            gps = UbloxGps(serial_port)
            return gps, serial_port
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
            return None, None

    def coordinates(self):
        try:
            geo = self.geo_coords()
            return geo.lon, geo.lat
        except Exception as e:
            print(f"Error reading coordinates: {e}")
            return None, None
    
    def heading(self):
        try:
            veh = self.veh_attitude()
            heading = veh.heading
            return heading
        except Exception as e:
            print(f"Error reading heading: {e}")
            return None
    
    def altitude(self):
        try:
            altitude = self.gps.altitude()
            return altitude
        except Exception as e:
            print(f"Error reading altitude: {e}")
            return None
    
    def roll_pitch_yaw(self):
        try:
            veh = self.veh_attitude()
            roll, pitch, yaw = veh.accRoll, veh.accPitch, veh.accheading
            return roll, pitch, yaw
        except Exception as e:
            print(f"Error reading roll, pitch and yaw: {e}")
            return None, None, None
    
    def main(self):
        while True:
            lat, lon = self.coordinates()
            if lat is not None and lon is not None:
                print(f"Coordinates: {lat}, {lon}")
            else:
                print("Error reading coordinates")
            
            heading = self.heading()
            if heading is not None:
                print(f"Heading: {heading}")
            else:
                print("Error reading heading")
            
            altitude = self.altitude()
            if altitude is not None:
                print(f"Altitude: {altitude}")
            else:
                print("Error reading altitude")
            
            roll, pitch, yaw = self.roll_pitch_yaw()
            if roll is not None and pitch is not None and yaw is not None:
                print(f"Roll: {roll}, Pitch: {pitch}, Yaw: {yaw}")
            else:
                print("Error reading roll, pitch and yaw")
            
            print("\n")

if __name__ == "__main__":
    gps_manager = GPSManager(description="u-blox")
    gps_manager.main()
