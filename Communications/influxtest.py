import time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import random

# Configuración de InfluxDB
url = "http://192.168.1.70:8086"
token = "9h_snhKkWwj_gSe5rrjxCAcEA3ucj4Y37pyQ9lGEU3PC4TU4iBjuoHvnNReRvNA04kY3mzHBfPpp_X6c0CCpmA=="
org = "UAX"
bucket = "UAXSAT IV"

# Crear un cliente de InfluxDB
client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

# Función para simular la obtención de datos de sensores
def obtener_datos():
    temperatura = random.uniform(20.0, 30.0)  # Simular una temperatura entre 20 y 30 grados
    humedad = random.uniform(30.0, 70.0)  # Simular una humedad entre 30% y 70%
    return temperatura, humedad

try:
    while True:
        # Obtener datos simulados
        temperatura, humedad = obtener_datos()

        # Crear un punto de datos para InfluxDB
        punto = Point("mediciones") \
            .tag("ubicacion", "laboratorio") \
            .field("temperatura", temperatura) \
            .field("humedad", humedad) \
            .time(time.time_ns(), WritePrecision.NS)

        # Escribir el punto en InfluxDB
        write_api.write(bucket=bucket, org=org, record=punto)

        print(f"Datos enviados: Temperatura={temperatura}°C, Humedad={humedad}%")

        # Esperar antes de enviar los próximos datos
        time.sleep(10)  # Esperar 10 segundos

except KeyboardInterrupt:
    print("Script terminado por el usuario")

finally:
    client.close()
