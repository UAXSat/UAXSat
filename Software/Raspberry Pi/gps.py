import serial
from ublox_gps import UbloxGps

port = serial.Serial('/dev/ttyACM0', baudrate=38400, timeout=1)
gps = UbloxGps(port)

def parse_nmea_sentence(sentence):
    parts = sentence.split(',')
    data = {}

    if parts[0] == '$GPGGA':
        data['type'] = 'GPGGA'
        data['fix_time'] = parts[1]
        data['latitude'] = convert_to_degrees(parts[2], parts[3])
        data['longitude'] = convert_to_degrees(parts[4], parts[5])
        data['fix_quality'] = parts[6]
        data['num_sats'] = parts[7]
        data['hdop'] = parts[8]
        data['altitude'] = parts[9]
        data['altitude_units'] = parts[10]
        data['geoid_separation'] = parts[11]
        data['geoid_units'] = parts[12]
    elif parts[0] == '$GPRMC':
        data['type'] = 'GPRMC'
        data['time'] = parts[1]
        data['status'] = parts[2]
        data['latitude'] = convert_to_degrees(parts[3], parts[4])
        data['longitude'] = convert_to_degrees(parts[5], parts[6])
        data['speed'] = parts[7]
        data['track_angle'] = parts[8]
        data['date'] = parts[9]
    elif parts[0] == '$GPGSV':
        data['type'] = 'GPGSV'
        data['num_messages'] = parts[1]
        data['message_num'] = parts[2]
        data['num_sats_in_view'] = parts[3]
        sats = []
        for i in range(4, len(parts) - 4, 4):
            sat = {
                'sat_id': parts[i],
                'elevation': parts[i + 1],
                'azimuth': parts[i + 2],
                'snr': parts[i + 3]
            }
            sats.append(sat)
        data['sats'] = sats
    return data

def convert_to_degrees(raw_data, direction):
    if not raw_data:
        return None
    degrees = float(raw_data[:2])
    minutes = float(raw_data[2:])
    result = degrees + minutes / 60
    if direction in ['S', 'W']:
        result = -result
    return result

def run():
    try:
        print("Listening for UBX Messages")
        while True:
            try:
                nmea_sentences = gps.stream_nmea().split('\n')
                for sentence in nmea_sentences:
                    data = parse_nmea_sentence(sentence)
                    if data:
                        print_nmea_data(data)

                geo = gps.geo_coords()
                print("Longitude: {:.7f}".format(geo.lon))
                print("Latitude: {:.7f}".format(geo.lat))
                print("Heading of Motion: {:.4f}".format(geo.headMot))

                gps_time = gps.date_time()
                print("{}/{}/{}".format(gps_time.day, gps_time.month, gps_time.year))
                print("UTC Time {}:{}:{}".format(gps_time.hour, gps_time.min, gps_time.sec))
                print("Valid date: {}\nValid Time: {}".format(gps_time.valid.validDate, gps_time.v>
                
            except (ValueError, IOError) as err:
                print(f"Error: {err}")

    finally:
        port.close()

def print_nmea_data(data):
    if data['type'] == 'GPGGA':
        print(f"Type: GPGGA")
        print(f"Fix Time: {data.get('fix_time', 'N/A')}")
        print(f"Latitude: {data.get('latitude', 'N/A')}")
        print(f"Longitude: {data.get('longitude', 'N/A')}")
        print(f"Fix Quality: {data.get('fix_quality', 'N/A')}")
        print(f"Number of Satellites: {data.get('num_sats', 'N/A')}")
        print(f"HDOP: {data.get('hdop', 'N/A')}")
        print(f"Altitude: {data.get('altitude', 'N/A')} {data.get('altitude_units', '')}")
        print(f"Geoid Separation: {data.get('geoid_separation', 'N/A')} {data.get('geoid_units', '>
    elif data['type'] == 'GPRMC':
        print(f"Type: GPRMC")
        print(f"Time: {data.get('time', 'N/A')}")
        print(f"Status: {data.get('status', 'N/A')}")
        print(f"Latitude: {data.get('latitude', 'N/A')}")
        print(f"Longitude: {data.get('longitude', 'N/A')}")
        print(f"Speed: {data.get('speed', 'N/A')}")
        print(f"Track Angle: {data.get('track_angle', 'N/A')}")
        print(f"Date: {data.get('date', 'N/A')}\n")
    elif data['type'] == 'GPGSV':
        print(f"Type: GPGSV")
        print(f"Number of Messages: {data.get('num_messages', 'N/A')}")
        print(f"Message Number: {data.get('message_num', 'N/A')}")
        print(f"Number of Satellites in View: {data.get('num_sats_in_view', 'N/A')}")
        print("Satellites Info:")
        for sat in data.get('sats', []):
            print(f"  Sat ID: {sat.get('sat_id', 'N/A')}")
            print(f"    Elevation: {sat.get('elevation', 'N/A')}")
            print(f"    Azimuth: {sat.get('azimuth', 'N/A')}")
            print(f"    SNR: {sat.get('snr', 'N/A')}\n")

if __name__ == '__main__':
    run()