import serial
import pynmea2
import time
from ublox_gps import UbloxGps

def open_serial_port():
    ports = ['/dev/ttyACM1', '/dev/ttyACM0']
    for port in ports:
        try:
            return serial.Serial(port, baudrate=38400, timeout=1), port
        except serial.SerialException as e:
            print(f"No se pudo abrir {port}: {e}")
    raise ConnectionError("No se pudo abrir ningún puerto serial.")

def handle_message(msg):
    if isinstance(msg, pynmea2.types.talker.RMC):
        print(f"RMC: Time {msg.timestamp}, Status {msg.status}, Lat {msg.latitude}, Lon {msg.longitude}, Speed {msg.spd_over_grnd} knots")
    elif isinstance(msg, pynmea2.types.talker.VTG):
        print(f"VTG: True Track {msg.true_track}, Magnetic Track {msg.mag_track}, Speed {msg.spd_over_grnd_kmph} km/h")
    elif isinstance(msg, pynmea2.types.talker.GGA):
        print(f"GGA: Time {msg.timestamp}, Lat {msg.latitude}, Lon {msg.longitude}, Altitude {msg.altitude} {msg.altitude_units}, Satellites {msg.num_sats}, HDOP {msg.horizontal_dil}")
    elif isinstance(msg, pynmea2.types.talker.GSA):
        print(f"GSA: Mode {msg.mode}, PDOP {msg.pdop}, HDOP {msg.hdop}, VDOP {msg.vdop}")
    elif isinstance(msg, pynmea2.types.talker.GSV):
        print(f"GSV: Satellites in View {msg.num_sv_in_view}")
    elif isinstance(msg, pynmea2.types.talker.GLL):
        print(f"GLL: Lat {msg.latitude}, Lon {msg.longitude}, Time {msg.timestamp}, Status {msg.status}")

def run():
    port, port_name = open_serial_port()
    print(f"Listening for UBX Messages on {port_name}")
    try:
        while True:
            nmea_data = port.readline().decode().strip()
            if nmea_data.startswith('$'):
                try:
                    msg = pynmea2.parse(nmea_data)
                    handle_message(msg)
                except pynmea2.ParseError as pe:
                    print(f"NMEA parse error: {pe}")
            time.sleep(2)  # Espera 2 segundos
    except KeyboardInterrupt:
        print("Program interrupted by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if port.is_open:
            port.close()
            print("Serial port closed properly.")

if __name__ == '__main__':
    run()