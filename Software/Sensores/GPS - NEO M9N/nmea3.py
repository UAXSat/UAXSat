import serial
import pynmea2
from ublox_gps import UbloxGps

port = serial.Serial('/dev/ttyACM1', baudrate=38400, timeout=1)
gps = UbloxGps(port)

def handle_gga(msg):
    print(f"Lat: {msg.latitude:.6f}, Lon: {msg.longitude:.6f}, Alt: {msg.altitude} {msg.altitude_units}")
    print(f"Satellites: {msg.num_sats}, HDOP: {msg.horizontal_dil}, Quality: {msg.gps_qual}")

def handle_rmc(msg):
    speed_kmh = float(msg.spd_over_grnd) * 1.852  # Convert knots to km/h
    print(f"Speed: {speed_kmh:.2f} km/h, Date: {msg.datestamp}, Time: {msg.timestamp}")
    print(f"Status: {msg.status}, Lat: {msg.latitude}, Lon: {msg.longitude}")

def handle_vtg(msg):
    true_track = msg.true_track or 'None'
    mag_track = msg.mag_track or 'None'
    speed_kmh = msg.spd_over_grnd_kmph or 'None'
    print(f"True track: {true_track}, Magnetic track: {mag_track}, Speed: {speed_kmh} km/h")

def handle_gsa(msg):
    mode = msg.mode
    pdop = msg.pdop
    hdop = msg.hdop
    vdop = msg.vdop
    satellites_used = [getattr(msg, f'sv_id{i:02}', '') for i in range(1, 13)]
    satellites_used = ', '.join(filter(None, satellites_used))
    print(f"Mode: {mode}, PDOP: {pdop}, HDOP: {hdop}, VDOP: {vdop}")
    print(f"Satellites used: {satellites_used if satellites_used else 'None'}")

def run():
    sentence_handlers = {
        'GGA': handle_gga,
        'RMC': handle_rmc,
        'VTG': handle_vtg,
        'GSA': handle_gsa
    }
    
    try:
        print("Listening for UBX Messages")
        while True:
            nmea_data = gps.stream_nmea()
            if nmea_data.startswith('$'):
                msg = pynmea2.parse(nmea_data)
                handler = sentence_handlers.get(msg.sentence_type, lambda x: None)
                handler(msg)
    except (ValueError, IOError) as err:
        print(err)
    except pynmea2.ParseError as pe:
        print(f"NMEA parse error: {pe}")
    finally:
        port.close()

if __name__ == '__main__':
    run()