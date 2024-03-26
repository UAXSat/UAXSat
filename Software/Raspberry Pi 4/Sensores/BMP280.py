"""*********************************************************************************************************
*                                                                                                          *
*                                     UAXSAT IV Project - 2024                                             *
*                                 Developed by Javier Bolaños Llano                                        *
*                                https://github.com/javierbolanosllano                                     *
*                                                                                                          *
*********************************************************************************************************"""

import board
import busio
import adafruit_bmp280

# Crea el objeto I2C utilizando los pines SCL y SDA estándar del microcontrolador.
i2c = busio.I2C(board.SCL, board.SDA)

# Crea el objeto BMP280. Se puede especificar la dirección I2C del sensor si es necesario (usualmente 0x76 o 0x77).
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=0x76)

def get_temperature():
    """
    Obtiene y devuelve la temperatura del sensor BMP280.
    
    :return: Temperatura medida por el sensor BMP280 en grados Celsius, redondeada a dos decimales.
    """
    return round(bmp280.temperature, 2)

def get_pressure():
    """
    Obtiene y devuelve la presión atmosférica medida por el sensor BMP280.
    
    :return: Presión medida por el sensor BMP280 en hectopascales (hPa), redondeada a dos decimales.
    """
    return round(bmp280.pressure, 2)

def get_altitude():
    """
    Calcula y devuelve la altitud basada en la presión atmosférica medida por el BMP280.
    
    La altitud se calcula utilizando la fórmula internacional estándar de la atmósfera (ISA),
    basada en la presión actual medida y la presión estándar al nivel del mar.
    
    :return: Altitud en metros, calculada a partir de la presión medida por el sensor BMP280, redondeada a dos decimales.
    """
    P = bmp280.pressure  # Presión actual medida en hPa
    P_0 = 1013.25  # Presión estándar al nivel del mar en hPa
    h = 44330 * (1 - (P / P_0) ** (1 / 5.255))  # Fórmula para calcular la altitud
    return round(h, 2)
