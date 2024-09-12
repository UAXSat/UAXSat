"""* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
*                                                                            *
*                         Developed by Javier Bolanos                        *
*                  https://github.com/javierbolanosllano                     *
*                                                                            *
*                      UAXSAT IV Project - 2024                              *
*                   https://github.com/UAXSat/UAXSat                         *
*                                                                            *
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *"""

# BMPmodule.py
import time
import board
import adafruit_bmp3xx

# Funci  n para inicializar el sensor BMP
def initialize_sensor():
    i2c = board.I2C()
    bmp = adafruit_bmp3xx.BMP3XX_I2C(i2c)
    
    bmp.pressure_oversampling = 8
    bmp.temperature_oversampling = 2
    bmp.sea_level_pressure = 1013.25
    
    return bmp

# Funci  n para obtener datos de presi  n, temperatura y altitud
def read_sensor_data(bmp):
    try:
        pressure, temperature, altitude = bmp.pressure, bmp.temperature, bmp.altitude
        return {"pressure": pressure, "temperature": temperature, "altitude": altitude}
    except Exception as e:
        print(f"Error reading sensor data: {e}")
        return None

# Funci  n principal - inicializa el sensor y lee los datos
def get_BMP_data():
    BMP = initialize_sensor()
    return read_sensor_data(BMP)
