"""* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
*                                                                            *
*                    Developed by Javier Bolaños                             *
*                 https://github.com/javierbolanosllano                      *
*                                                                            *
*                      UAXSAT IV Project - 2024                              *
*                   https://github.com/UAXSat/UAXSat                         *
*                                                                            *
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *"""
# bmp390module.py

import time
import board
import adafruit_bmp3xx

# Función para inicializar el sensor BMP
def initialize_bmp_sensor():
    i2c = board.I2C()
    bmp = adafruit_bmp3xx.BMP3XX_I2C(i2c)
    
    bmp.pressure_oversampling = 8
    bmp.temperature_oversampling = 2
    bmp.sea_level_pressure = 1013.25
    
    return bmp

# Función para obtener datos de presión, temperatura y altitud
def read_sensor_data(bmp):
    pressure = bmp.pressure
    temperature = bmp.temperature
    altitude = bmp.altitude
    
    return pressure, temperature, altitude

# Función para imprimir los datos
def print_sensor_data(pressure, temperature, altitude):
    print("Pressure: {:6.4f}  Temperature: {:5.2f}".format(pressure, temperature))
    print("Altitude: {} meters".format(altitude))

# Función principal - inicializa el sensor y lee los datos
def main():
    bmp = initialize_bmp_sensor()
    
    try:
        while True:
            pressure, temperature, altitude = read_sensor_data(bmp)
            print_sensor_data(pressure, temperature, altitude)
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("Program interrupted. Exiting...")

if __name__ == "__main__":
    main()


"""
# main.py

from bmp390module import initialize_bmp_sensor, read_sensor_data as read_bmp
import time

def main():
    bmp = initialize_bmp_sensor()
    
    while True:
        pressure, temperature, altitude = read_bmp(bmp)
        if pressure is not None and temperature is not None and altitude is not None:
            print("Pressure: {:6.4f}  Temperature: {:5.2f} Altitude: {} meters".format(pressure, temperature, altitude))
        time.sleep(1)

if __name__ == "__main__":
    main()

"""