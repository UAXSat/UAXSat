"""- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - *

                         Developed by Javier Bolanos
                    https://github.com/javierbolanosllano

                           UAXSAT IV Project - 2024
                       https://github.com/UAXSat/UAXSat

* - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - """

# IMUmodule.py
import time
import board
import adafruit_icm20x

# Funci  n para inicializar el sensor ICM
def initialize_sensor():
    i2c = board.I2C()  # Utiliza board.SCL y board.SDA por defecto
    icm = adafruit_icm20x.ICM20948(i2c)
    return icm

# Funci  n para obtener datos de aceleraci  n
def read_acceleration(icm):
    return icm.acceleration

# Funci  n para obtener datos de giroscopio
def read_gyro(icm):
    return icm.gyro

# Funci  n para obtener datos del magnet  metro
def read_magnetic(icm):
    return icm.magnetic

def read_sensor_data(icm):
    try:
        acceleration, gyro, magnetic = read_acceleration(icm), read_gyro(icm), read_magnetic(icm)
        data = {
            "ACELX": acceleration[0], "ACELY": acceleration[1], "ACELZ": acceleration[2],
            "GIROX": gyro[0], "GIROY": gyro[1], "GIROZ": gyro[2],
            "MAGX": magnetic[0], "MAGY": magnetic[1], "MAGZ": magnetic[2]
        }
        return data
    except Exception as e:
        print(f"Error reading the IMU: {e}")
        return None

def get_IMU_data():
    imu = initialize_sensor()
    return read_sensor_data(imu)

# Función principal para ejecución continua
def main():
    imu = initialize_sensor()
    while True:
        imudata = read_sensor_data(imu)
        if imudata:
            print(imudata)
        else:
            print("Error initializing the IMU")
        time.sleep(1)

# Ejecutar el sensor si se ejecuta como script principal
if __name__ == "__main__":
    main()
