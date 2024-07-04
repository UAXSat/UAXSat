"""***************************************************************************
*                                                                            *
*                      UAXSAT IV Project - 2024                              *
*                  Developed by Javier Bolaños Llano                         *
*                 https://github.com/javierbolanosllano                      *
*                                                                            *
***************************************************************************"""

# bmp390.py
import time
import board
import busio
import adafruit_bmp3xx
import math

class BMP3XXSensor:
    def __init__(self, i2c_bus=None):
        if i2c_bus is None:
            i2c_bus = busio.I2C(board.SCL, board.SDA)
        self.i2c_bus = i2c_bus
        self.sensor = None
        self.connect_sensor()
    
    def connect_sensor(self):
        try:
            self.sensor = adafruit_bmp3xx.BMP3XX_I2C(self.i2c_bus)
            self.sensor.sea_level_pressure = 1013.25
            self.sensor.pressure_oversampling = 8
            self.sensor.temperature_oversampling = 2
            print("Sensor BMP3XX conectado exitosamente.")
        except Exception as e:
            self.sensor = None
            print(f"Error al conectar con el sensor: {e}")
    
    def read_pressure(self):
        try:
            return self.sensor.pressure if self.sensor else math.nan
        except Exception as e:
            print(f"Error al leer presión: {e}")
            self.sensor = None
            return math.nan
    
    def read_temperature(self):
        try:
            return self.sensor.temperature if self.sensor else math.nan
        except Exception as e:
            print(f"Error al leer temperatura: {e}")
            self.sensor = None
            return math.nan
    
    def read_altitude(self):
        try:
            return self.sensor.altitude if self.sensor else math.nan
        except Exception as e:
            print(f"Error al leer altitud: {e}")
            self.sensor = None
            return math.nan
    
    def read_all(self):
        return {
            'pressure': self.read_pressure(),
            'temperature': self.read_temperature(),
            'altitude': self.read_altitude()
        }

def main():
    bmp3xx = BMP3XXSensor()
    while True:
        try:
            data = bmp3xx.read_all()
            print("Presión: {:6.4f} hPa  Temperatura: {:5.2f} °C".format(data['pressure'], data['temperature']))
            print("Altitud: {} metros".format(data['altitude']))
            print("")
        except Exception as e:
            print(f"Error al leer datos del sensor: {e}")
        
        # Si el sensor es None, intenta reconectarse
        if bmp3xx.sensor is None:
            print("Intentando reconectar con el sensor...")
            bmp3xx.connect_sensor()
        
        time.sleep(1)

if __name__ == '__main__':
    main()
