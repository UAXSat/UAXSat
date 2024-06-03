import serial
import pynmea2

from ublox_gps import UbloxGps

port = serial.Serial('/dev/ttyACM1', baudrate=38400, timeout=1)
gps = UbloxGps(port)

def run():
    try:
        print("Listening for UBX Messages")
        while True:
            try:
                nmea_data = gps.stream_nmea()
                if nmea_data.startswith('$'):
                    msg = pynmea2.parse(nmea_data)
                    if isinstance(msg, pynmea2.types.talker.GGA):
                        print(f"Lat: {msg.latitude}, Lon: {msg.longitude}, Alt: {msg.altitude} {msg.altitude_units}")
                        print(f"Satellites: {msg.num_sats}, HDOP: {msg.horizontal_dil}, Quality: {msg.gps_qual}")
                    elif isinstance(msg, pynmea2.types.talker.RMC):
                        print(f"Speed: {msg.spd_over_grnd} knots, Date: {msg.datestamp}, Time: {msg.timestamp}")
                        print(f"Status: {msg.status}, Lat: {msg.latitude}, Lon: {msg.longitude}")
                    elif isinstance(msg, pynmea2.types.talker.VTG):
                        print(f"True track: {msg.true_track}, Magnetic track: {msg.mag_track}, Speed: {msg.spd_over_grnd_kmph} km/h")
                    elif isinstance(msg, pynmea2.types.talker.GSA):
                        pdop = getattr(msg, 'pdop', 'N/A')
                        hdop = getattr(msg, 'hdop', 'N/A')
                        vdop = getattr(msg, 'vdop', 'N/A')
                        mode = getattr(msg, 'mode', 'N/A')
                        print(f"Mode: {mode}, PDOP: {pdop}, HDOP: {hdop}, VDOP: {vdop}")
                        satellites_used = [msg.data[i] for i in range(3, 15) if msg.data[i].isdigit()]  # GSA has up to 12 satellite slots from index 3 to 14
                        print(f"Satellites used: {','.join(satellites_used) if satellites_used else 'None'}")
            except (ValueError, IOError) as err:
                print(err)
            except pynmea2.ParseError as pe:
                print(f"NMEA parse error: {pe}")

    finally:
        port.close()

if __name__ == '__main__':
    run()