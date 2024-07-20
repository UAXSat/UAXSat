import serial
import pynmea2

# Abre el puerto serial
try:
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
except serial.SerialException as e:
    print(f"Error al abrir el puerto serial: {e}")
    exit()

# Función para formatear y estructurar los datos
def format_gps_data(data):
    print("GPS Data")
    print("=" * 40)
    print(f"Time: {data.timestamp}")
    print(f"Latitude: {data.latitude} {data.lat_dir}")
    print(f"Longitude: {data.longitude} {data.lon_dir}")
    print(f"Fix Quality: {data.gps_qual}")
    print(f"Number of Satellites: {data.num_sats}")
    print(f"Horizontal Dilution: {data.horizontal_dil}")
    print(f"Altitude: {data.altitude} {data.altitude_units}")
    print(f"Height of Geoid: {data.geo_sep} {data.geo_sep_units}")
    print("=" * 40)

# Leer del puerto serial
while True:
    try:
        line = ser.readline().decode('ascii', errors='replace')
        if line.startswith('$GNGGA'):
            msg = pynmea2.parse(line)
            format_gps_data(msg)
    except serial.SerialException as e:
        print(f"Error de lectura del puerto serial: {e}")
        break
    except pynmea2.ParseError as e:
        print(f"Error de parseo de NMEA: {e}")
        continue
    except KeyboardInterrupt:
        print("\nInterrupción por teclado detectada. Cerrando el puerto serial.")
        ser.close()
        break
