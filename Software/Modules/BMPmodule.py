"""- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - *

                         Developed by Javier Bolanos
                    https://github.com/javierbolanosllano

                           UAXSAT IV Project - 2024
                       https://github.com/UAXSat/UAXSat

* - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - """

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

# Funcion para obtener datos de presion, temperatura y altitud
def read_sensor_data(bmp):
    try:
        pressure, temperature, altitude = bmp.pressure, bmp.temperature, bmp.altitude
        return {"pressure": pressure, "temperature": temperature, "altitude": altitude}
    except Exception as e:
        print(f"Error reading sensor data: {e}")
        return None

# Funcion principal - inicializa el sensor y lee los datos
def get_BMP_data():
    BMP = initialize_sensor()
    return read_sensor_data(BMP)

# Función principal - inicializa el sensor y lee los datos
def main():
    bmp = initialize_sensor()
    while True:
        sensor_data = read_sensor_data(bmp)
        if sensor_data:
            print(f"Pressure: {sensor_data['pressure']} Pa, Temperature: {sensor_data['temperature']} C, Altitude: {sensor_data['altitude']} m")
        else:
            print("Error initializing the sensor")
        time.sleep(1)

if __name__ == "__main__":
    main()