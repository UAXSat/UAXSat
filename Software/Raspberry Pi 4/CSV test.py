import time
import os
import board
import busio
import adafruit_bmp280
import csv

# Identificador del sensor DS18B20
sensor_id = "28-072252732021"
sensor_file = '/sys/bus/w1/devices/' + sensor_id + '/w1_slave'

def read_temp_raw():
    f = open(sensor_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

# Crea el objeto I2C utilizando los pines de board.SCL y board.SDA
i2c = busio.I2C(board.SCL, board.SDA)

# Crea el objeto BMP280, especificando la dirección I2C si es necesario (0x76 o 0x77)
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=0x76)

# Carpeta donde se guardará el archivo CSV
folder_path = '/home/javi/Documents/'

# Genera el nombre del archivo CSV basado en la fecha y hora actual
current_time = time.strftime("%d-%m_%H-%M-%S", time.localtime())
file_name = "data_" + current_time + ".csv"
file_path = os.path.join(folder_path, file_name)

# Abre el archivo CSV en modo de añadir ('a') o crea uno nuevo si no existe
with open(file_path, mode='a', newline='') as file:
    writer = csv.writer(file, delimiter=';')  # Use ';' as the delimiter
    # Escribe el encabezado solo si el archivo está vacío
    if os.stat(file_path).st_size == 0:
        writer.writerow(['Hour', 'Min', 'Second', 'DS18B20 [°C]', 'BMP280 [°C]', 'Pressure [hPa]'])
        print("Hour, Min, Second, DS18B20 [°C], BMP280 [°C], Pressure [hPa]")

    # Inicio del temporizador
    start_time = time.time()
    # Duración deseada del script en segundos
    duration = 1 * 60 * 60 # Hours * Minutes * Seconds

    while time.time() - start_time < duration:
        now = time.localtime() # Obtiene la hora actual
        temperature_ds18b20 = read_temp()
        temperature_bmp280 = bmp280.temperature
        pressure = bmp280.pressure
        # Escribe los datos en el archivo CSV
        writer.writerow([now.tm_hour, now.tm_min, now.tm_sec, temperature_ds18b20, temperature_bmp280, pressure])
        file.flush()  # Flush the buffer to ensure immediate writing to disk
        os.fsync(file.fileno())  # Force write to disk
        print("{},{},{},{:.1f},{:.1f},{:.1f}".format(now.tm_hour, now.tm_min, now.tm_sec, temperature_ds18b20, temperature_bmp280, pressure))
        time.sleep(5)  # Espera antes de la próxima lectura