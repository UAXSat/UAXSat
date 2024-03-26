"""*********************************************************************************************************
*                                                                                                          *
*                                     UAXSAT IV Project - 2024                                             *
*                                 Developed by Javier Bolaños Llano                                        *
*                                https://github.com/javierbolanosllano                                     *
*                                                                                                          *
*********************************************************************************************************"""

import smbus

class mpu6050:
    """
    Clase para interactuar con el sensor MPU-6050, permitiendo leer los datos
    de aceleración, giroscopio y temperatura.
    """

    # Constantes globales
    GRAVITIY_MS2 = 9.80665  # Aceleración de la gravedad en metros sobre segundo al cuadrado
    address = None  # Dirección I2C del sensor
    bus = None  # Objeto SMBus para la comunicación I2C

    # Modificadores de escala para la aceleración
    ACCEL_SCALE_MODIFIER_2G = 16384.0
    ACCEL_SCALE_MODIFIER_4G = 8192.0
    ACCEL_SCALE_MODIFIER_8G = 4096.0
    ACCEL_SCALE_MODIFIER_16G = 2048.0

    # Modificadores de escala para el giroscopio
    GYRO_SCALE_MODIFIER_250DEG = 131.0
    GYRO_SCALE_MODIFIER_500DEG = 65.5
    GYRO_SCALE_MODIFIER_1000DEG = 32.8
    GYRO_SCALE_MODIFIER_2000DEG = 16.4

    # Rangos predefinidos para la aceleración
    ACCEL_RANGE_2G = 0x00
    ACCEL_RANGE_4G = 0x08
    ACCEL_RANGE_8G = 0x10
    ACCEL_RANGE_16G = 0x18

    # Rangos predefinidos para el giroscopio
    GYRO_RANGE_250DEG = 0x00
    GYRO_RANGE_500DEG = 0x08
    GYRO_RANGE_1000DEG = 0x10
    GYRO_RANGE_2000DEG = 0x18

    # Configuraciones para el filtro de paso bajo
    FILTER_BW_256=0x00
    FILTER_BW_188=0x01
    FILTER_BW_98=0x02
    FILTER_BW_42=0x03
    FILTER_BW_20=0x04
    FILTER_BW_10=0x05
    FILTER_BW_5=0x06

    # Registros del MPU-6050
    PWR_MGMT_1 = 0x6B
    PWR_MGMT_2 = 0x6C

    ACCEL_XOUT0 = 0x3B
    ACCEL_YOUT0 = 0x3D
    ACCEL_ZOUT0 = 0x3F

    TEMP_OUT0 = 0x41

    GYRO_XOUT0 = 0x43
    GYRO_YOUT0 = 0x45
    GYRO_ZOUT0 = 0x47

    ACCEL_CONFIG = 0x1C
    GYRO_CONFIG = 0x1B
    MPU_CONFIG = 0x1A

    def __init__(self, address, bus=1):
        """
        Inicializa la clase con la dirección I2C del sensor y el número del bus I2C.
        Activa el sensor sacándolo del modo de reposo.
        """
        self.address = address
        self.bus = smbus.SMBus(bus)
        # Despertar el MPU-6050 ya que comienza en modo de reposo
        self.bus.write_byte_data(self.address, self.PWR_MGMT_1, 0x00)

    def read_i2c_word(self, register):
        """
        Lee dos registros I2C y los combina en un valor.

        :param register: el primer registro de donde leer.
        :return: el resultado combinado de la lectura.
        """
        # Leer los datos de los registros
        high = self.bus.read_byte_data(self.address, register)
        low = self.bus.read_byte_data(self.address, register + 1)

        value = (high << 8) + low

        if (value >= 0x8000):
            return -((65535 - value) + 1)
        else:
            return value

    def get_temp(self):
        """
        Lee la temperatura del sensor de temperatura integrado en el MPU-6050.

        :return: la temperatura en grados Celsius.
        """
        raw_temp = self.read_i2c_word(self.TEMP_OUT0)
        # Calcular la temperatura real usando la fórmula del datasheet
        actual_temp = (raw_temp / 340.0) + 36.53

        return actual_temp
    def set_accel_range(self, accel_range):
        """
        Establece el rango del acelerómetro.

        :param accel_range: el rango a establecer para el acelerómetro, usando uno de los rangos predefinidos.
        """
        # Primero lo cambiamos a 0x00 para asegurarnos de escribir el valor correcto después
        self.bus.write_byte_data(self.address, self.ACCEL_CONFIG, 0x00)

        # Escribir el nuevo rango en el registro ACCEL_CONFIG
        self.bus.write_byte_data(self.address, self.ACCEL_CONFIG, accel_range)

    def read_accel_range(self, raw=False):
        """
        Lee el rango al que está configurado el acelerómetro.

        :param raw: Si es True, devuelve el valor crudo del registro ACCEL_CONFIG.
                    Si es False, devuelve un entero: -1, 2, 4, 8 o 16. Si devuelve -1, algo salió mal.
        :return: El rango del acelerómetro.
        """
        raw_data = self.bus.read_byte_data(self.address, self.ACCEL_CONFIG)

        if raw:
            return raw_data
        else:
            if raw_data == self.ACCEL_RANGE_2G:
                return 2
            elif raw_data == self.ACCEL_RANGE_4G:
                return 4
            elif raw_data == self.ACCEL_RANGE_8G:
                return 8
            elif raw_data == self.ACCEL_RANGE_16G:
                return 16
            else:
                return -1

    def get_accel_data(self, g=False):
        """
        Obtiene y devuelve los valores X, Y y Z del acelerómetro.

        :param g: Si es True, devuelve los datos en unidades de g (gravedad).
                  Si es False, devuelve los datos en m/s^2.
        :return: Un diccionario con los resultados de las mediciones.
        """
        x = self.read_i2c_word(self.ACCEL_XOUT0)
        y = self.read_i2c_word(self.ACCEL_YOUT0)
        z = self.read_i2c_word(self.ACCEL_ZOUT0)

        accel_range = self.read_accel_range(True)
        accel_scale_modifier = self._get_scale_modifier(accel_range)

        x = x / accel_scale_modifier
        y = y / accel_scale_modifier
        z = z / accel_scale_modifier

        if g:
            return {'x': x, 'y': y, 'z': z}
        else:
            x = x * self.GRAVITIY_MS2
            y = y * self.GRAVITIY_MS2
            z = z * self.GRAVITIY_MS2
            return {'x': x, 'y': y, 'z': z}

    def set_gyro_range(self, gyro_range):
        """
        Establece el rango del giroscopio.

        :param gyro_range: el rango a establecer para el giroscopio, utilizando uno de los rangos predefinidos.
        """
        self.bus.write_byte_data(self.address, self.GYRO_CONFIG, 0x00)  # Restablecer primero a 0x00
        self.bus.write_byte_data(self.address, self.GYRO_CONFIG, gyro_range)  # Escribir el nuevo rango

    def set_filter_range(self, filter_range=FILTER_BW_256):
        """
        Establece la frecuencia del filtro de paso bajo.

        :param filter_range: la frecuencia del filtro a establecer, usando uno de los valores predefinidos.
        """
        EXT_SYNC_SET = self.bus.read_byte_data(self.address, self.MPU_CONFIG) & 0b00111000
        self.bus.write_byte_data(self.address, self.MPU_CONFIG, EXT_SYNC_SET | filter_range)

    def read_gyro_range(self, raw=False):
        """
        Lee el rango al que está configurado el giroscopio.

        :param raw: Si es True, devuelve el valor crudo del registro GYRO_CONFIG.
                    Si es False, devuelve 250, 500, 1000, 2000 o -1. Si devuelve -1, algo salió mal.
        :return: El rango del giroscopio.
        """
        raw_data = self.bus.read_byte_data(self.address, self.GYRO_CONFIG)

        if raw:
            return raw_data
        else:
            if raw_data == self.GYRO_RANGE_250DEG:
                return 250
            elif raw_data == self.GYRO_RANGE_500DEG:
                return 500
            elif raw_data == self.GYRO_RANGE_1000DEG:
                return 1000
            elif raw_data == self.GYRO_RANGE_2000DEG:
                return 2000
            else:
                return -1

    def get_gyro_data(self):
        """
        Obtiene y devuelve los valores X, Y y Z del giroscopio.

        :return: Un diccionario con los valores leídos.
        """
        x = self.read_i2c_word(self.GYRO_XOUT0)
        y = self.read_i2c_word(self.GYRO_YOUT0)
        z = self.read_i2c_word(self.GYRO_ZOUT0)

        gyro_range = self.read_gyro_range(True)
        gyro_scale_modifier = self._get_scale_modifier(gyro_range, gyro=True)

        x = x / gyro_scale_modifier
        y = y / gyro_scale_modifier
        z = z / gyro_scale_modifier

        return {'x': x, 'y': y, 'z': z}

    def _get_scale_modifier(self, range_value, gyro=False):
        """
        Obtiene el modificador de escala basado en el rango seleccionado para
        el acelerómetro o el giroscopio.

        :param range_value: El valor del rango seleccionado.
        :param gyro: Booleano que indica si el cálculo es para el giroscopio (True) o el acelerómetro (False).
        :return: El modificador de escala correspondiente al rango.
        """
        if gyro:
            return {
                self.GYRO_RANGE_250DEG: self.GYRO_SCALE_MODIFIER_250DEG,
                self.GYRO_RANGE_500DEG: self.GYRO_SCALE_MODIFIER_500DEG,
                self.GYRO_RANGE_1000DEG: self.GYRO_SCALE_MODIFIER_1000DEG,
                self.GYRO_RANGE_2000DEG: self.GYRO_SCALE_MODIFIER_2000DEG,
            }.get(range_value, self.GYRO_SCALE_MODIFIER_250DEG)  # Default a 250 grados por segundo
        else:
            return {
                self.ACCEL_RANGE_2G: self.ACCEL_SCALE_MODIFIER_2G,
                self.ACCEL_RANGE_4G: self.ACCEL_SCALE_MODIFIER_4G,
                self.ACCEL_RANGE_8G: self.ACCEL_SCALE_MODIFIER_8G,
                self.ACCEL_RANGE_16G: self.ACCEL_SCALE_MODIFIER_16G,
            }.get(range_value, self.ACCEL_SCALE_MODIFIER_2G)  # Default a 2g

    def get_all_data(self):
        """
        Lee y devuelve todos los datos disponibles: aceleración, giroscopio y temperatura.

        :return: Una lista que contiene los datos del acelerómetro, giroscopio y la temperatura.
        """
        temp = self.get_temp()
        accel = self.get_accel_data()
        gyro = self.get_gyro_data()

        return [accel, gyro, temp]

# Función para crear y devolver una instancia de la clase mpu6050
def create_mpu_instance(address=0x68, bus=1):
    """
    Crea y devuelve una instancia de la clase mpu6050 con la dirección y bus I2C especificados.

    :param address: Dirección I2C del sensor MPU-6050.
    :param bus: Número del bus I2C a utilizar.
    :return: Una instancia de la clase mpu6050.
    """
    return mpu6050(address, bus)