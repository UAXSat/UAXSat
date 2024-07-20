"""* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
*                                                                            *
*               Developed by Javier Bolañs & Javier Lendinez                *
*                  https://github.com/javierbolanosllano                     *
*                        https://github.com/JaviLendi                        *
*                                                                            *
*                      UAXSAT IV Project - 2024                              *
*                   https://github.com/UAXSat/UAXSat                         *
*                                                                            *
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *"""

# IMUmodule.py
import time
import board
import adafruit_icm20x

# Función para inicializar el sensor ICM
def initialize_sensor():
    i2c = board.I2C()  # Utiliza board.SCL y board.SDA por defecto
    icm = adafruit_icm20x.ICM20948(i2c)
    return icm

# Función para obtener datos de aceleración
def read_acceleration(icm):
    return icm.acceleration

# Función para obtener datos de giroscopio
def read_gyro(icm):
    return icm.gyro

# Función para obtener datos del magnetómetro
def read_magnetic(icm):
    return icm.magnetic

def read_sensor_data(icm):
    try:
        acceleration, gyro, magnetic = read_acceleration(icm), read_gyro(icm), read_magnetic(icm)
        return {"ACELX": acceleration[0], "ACELY": acceleration[1], "ACELZ": acceleration[2], "GIROX": gyro[0], "GIROY": gyro[1], "GIROZ": gyro[2], "MAGX": magnetic[0], "MAGY": magnetic[1], "MAGZ": magnetic[2]}
    except Exception as e:
        print(f"Error reading the IMU: {e}")
        return None

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
