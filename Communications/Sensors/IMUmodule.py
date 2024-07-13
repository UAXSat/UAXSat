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
def initialize_sensor():
    try: 
        i2c = board.I2C()  # Utiliza board.SCL y board.SDA por defecto
        icm = adafruit_icm20x.ICM20948(i2c)
        return icm
    except Exception as e:
        return Exception  # Devuelve None si ocurre un error durante la inicialización

# Función para obtener datos de aceleración
def read_acceleration(icm):
    try:
        return icm.acceleration
    except Exception as e:
        #print(f"Error reading acceleration: {e}")
        return None

# Función para obtener datos de giroscopio
def read_gyro(icm):
    try:
        return icm.gyro
    except Exception as e:
        #print(f"Error reading gyro: {e}")
        return None

# Función para obtener datos del magnetómetro
def read_magnetic(icm):
    try: 
        return icm.magnetic
    except Exception as e:
        #print(f"Error reading magnetic: {e}")
        return None

def read_sensor_data(icm):
    try:
        acceleration, gyro, magnetic = read_acceleration(icm), read_gyro(icm), read_magnetic(icm)
        return {"acceleration": acceleration, "gyro": gyro, "magnetic": magnetic}
    except Exception as e:
        print(f"Error reading sensor data: {e}")

# Función principal para ejecución continua
def main():
    icm = initialize_sensor()
    while True:
        sensor_data = read_sensor_data(icm)
        if sensor_data:
            print(f"Acceleration: {sensor_data['acceleration']}, Gyro: {sensor_data['gyro']}, Magnetic: {sensor_data['magnetic']}")
        else:
            print("Error initializing the sensor")
        time.sleep(1)

# Ejecutar el sensor si se ejecuta como script principal
if __name__ == "__main__":
    main()

