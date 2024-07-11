"""***************************************************************************
*                                                                            *
*                      UAXSAT IV Project - 2024                              *
*                  Developed by Javier Bolaños Llano                         *
*                 https://github.com/javierbolanosllano                      *
*                                                                            *
***************************************************************************"""

# icm20948module.py
import time
import board
import adafruit_icm20x

# Función para inicializar el sensor ICM
def initialize_icm_sensor():
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

# Función principal para ejecución continua
def main():
    icm = initialize_icm_sensor()
    
    try:
        while True:
            acceleration = read_acceleration(icm)
            gyro = read_gyro(icm)
            magnetic = read_magnetic(icm)
            
            print("Acceleration: X:%.2f, Y:%.2f, Z:%.2f m/s^2" % acceleration)
            print("Gyro X:%.2f, Y:%.2f, Z:%.2f rads/s" % gyro)
            print("Magnetometer X:%.2f, Y:%.2f, Z:%.2f uT" % magnetic)
            print("")
            
            time.sleep(0.5)
    
    except KeyboardInterrupt:
        print("Program interrupted. Exiting...")

# Ejecutar el sensor si se ejecuta como script principal
if __name__ == "__main__":
    main()

"""
from icm20948module import initialize_icm_sensor, read_acceleration, read_gyro, read_magnetic
import time

def main():
    icm = initialize_icm_sensor()
    
    while True:
        acceleration = read_acceleration(icm)
        gyro = read_gyro(icm)
        magnetic = read_magnetic(icm)
        
        print("Acceleration: X:%.2f, Y:%.2f, Z:%.2f m/s^2" % acceleration)
        print("Gyro X:%.2f, Y:%.2f, Z:%.2f rads/s" % gyro)
        print("Magnetometer X:%.2f, Y:%.2f, Z:%.2f uT" % magnetic)
        print("")
        
        time.sleep(1)

if __name__ == "__main__":
    main()
    """
