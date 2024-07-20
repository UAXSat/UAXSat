import serial
import pynmea2

from ublox_gps import UbloxGps

port = serial.Serial('/dev/ttyACM1', baudrate=38400, timeout=1)
gps = UbloxGps(port)

def knots_to_mps(knots):
    return knots * 0.514444  # Convert knots to meters per second

def run():
    try:
        print("Listening for UBX Messages")
        while True:
            try:
                nmea_data = gps.stream_nmea()
                if nmea_data.startswith('$'):
                    msg = pynmea2.parse(nmea_data)
                    if isinstance(msg, pynmea2.types.talker.RMC):
                        lat = msg.latitude
                        lon = msg.longitude
                        # Verifica si spd_over_grnd es None antes de convertirlo
                        if msg.spd_over_grnd is not None:
                            speed_mps = knots_to_mps(float(msg.spd_over_grnd))
                            print(f"Time: {msg.timestamp}, Status: {msg.status}, Lat: {lat}, Lon: {lon}, Speed: {speed_mps:.2f} m/s")
                        else:
                            print(f"Time: {msg.timestamp}, Status: {msg.status}, Lat: {lat}, Lon: {lon}, Speed: Data not available")
                    elif isinstance(msg, pynmea2.types.talker.GGA):
                        alt = msg.altitude
                        print(f"Lat: {msg.latitude}, Lon: {msg.longitude}, Alt: {alt} M")
                    # Agrega más condiciones para otros tipos de mensajes NMEA
            except (ValueError, IOError) as err:
                print(err)
            except pynmea2.ParseError as pe:
                print(f"NMEA parse error: {pe}")

    finally:
        port.close()

if __name__ == '__main__':
    run()
