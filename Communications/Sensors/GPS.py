import serial
from ublox_gps import UbloxGps

port = serial.Serial('/dev/serial0', baudrate=38400, timeout=1)
gps = UbloxGps(port)

def run():
    try:
        print("Listening for UBX Messages")
        while True:
            try:
                geo = gps.geo_coords()
                if geo is not None:
                    print("Longitude: ", geo.lon) 
                    print("Latitude: ", geo.lat)
                    print("Heading of Motion: ", geo.headMot)
                    
                    altitude = gps.get_altitude()
                    print("Altitude: ", altitude)

                    roll, pitch, yaw = gps.roll_pitch_yaw()
                    print("Roll: ", roll)
                    print("Pitch: ", pitch)
                    print("Yaw: ", yaw)

                    speed = gps.get_speed()
                    print("Speed: ", speed)

                    satellites = gps.get_satellite_info()
                    print("Satellites: ", satellites)
                else:
                    print("No GPS fix acquired.")
                
            except (ValueError, IOError) as err:
                print(f"GPS error: {err}")
    
    finally:
        port.close()

if __name__ == '__main__':
    run()
