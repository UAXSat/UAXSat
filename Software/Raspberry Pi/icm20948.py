"""***************************************************************************
*                                                                            *
*                      UAXSAT IV Project - 2024                              *
*                  Developed by Javier Bolaños Llano                         *
*                 https://github.com/javierbolanosllano                      *
*                                                                            *
***************************************************************************"""

# icm20948.py
import time
import board
import busio
import adafruit_icm20x
import math

class ICM20948Sensor:
    def __init__(self, i2c_bus=None):
        if i2c_bus is None:
            i2c_bus = busio.I2C(board.SCL, board.SDA)
        self.i2c_bus = i2c_bus
        self.sensor = None
        self.connect_sensor()
    
    def connect_sensor(self):
        try:
            self.sensor = adafruit_icm20x.ICM20948(self.i2c_bus)
            print("Sensor ICM20948 conectado exitosamente.")
        except Exception as e:
            self.sensor = None
            print(f"Error al conectar con el sensor: {e}")
    
    def read_acceleration(self):
        try:
            return self.sensor.acceleration if self.sensor else (math.nan, math.nan, math.nan)
        except Exception as e:
            print(f"Error al leer aceleración: {e}")
            self.sensor = None
            return (math.nan, math.nan, math.nan)
    
    def read_gyro(self):
        try:
            return self.sensor.gyro if self.sensor else (math.nan, math.nan, math.nan)
        except Exception as e:
            print(f"Error al leer giroscopio: {e}")
            self.sensor = None
            return (math.nan, math.nan, math.nan)
    
    def read_magnetic(self):
        try:
            return self.sensor.magnetic if self.sensor else (math.nan, math.nan, math.nan)
        except Exception as e:
            print(f"Error al leer magnetómetro: {e}")
            self.sensor = None
            return (math.nan, math.nan, math.nan)
    
    def read_all(self):
        return {
            'acceleration': self.read_acceleration(),
            'gyro': self.read_gyro(),
            'magnetic': self.read_magnetic()
        }

def main():
    icm20948 = ICM20948Sensor()
    while True:
        try:
            data = icm20948.read_all()
            print("Aceleración: X={0:.2f}m/s^2, Y={1:.2f}m/s^2, Z={2:.2f}m/s^2".format(*data['acceleration']))
            print("Giroscopio: X={0:.2f}rads/s, Y={1:.2f}rads/s, Z={2:.2f}rads/s".format(*data['gyro']))
            print("Magnetómetro: X={0:.2f}uT, Y={1:.2f}uT, Z={2:.2f}uT".format(*data['magnetic']))
            print("")
        except Exception as e:
            print(f"Error al leer datos del sensor: {e}")
        
        # Si el sensor es None, intenta reconectarse
        if icm20948.sensor is None:
            print("Intentando reconectar con el sensor...")
            icm20948.connect_sensor()
        
        time.sleep(1)

if __name__ == '__main__':
    main()
