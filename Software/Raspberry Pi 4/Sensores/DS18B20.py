"""*********************************************************************************************************
*                                                                                                          *
*                                     UAXSAT IV Project - 2024                                             *
*                                 Developed by Javier Bolaños Llano                                        *
*                                https://github.com/javierbolanosllano                                     *
*                                                                                                          *
*********************************************************************************************************"""

# Identificador único del sensor DS18B20
sensor_id = "28-072252732021"
# Ruta al archivo del sistema que contiene la lectura de temperatura del sensor
sensor_file = '/sys/bus/w1/devices/' + sensor_id + '/w1_slave'

def read_temp_raw():
    """
    Lee las líneas crudas desde el archivo del sensor.
    
    :return: Una lista de líneas leídas desde el archivo del sensor.
    """
    f = open(sensor_file, 'r')  # Abre el archivo en modo de lectura
    lines = f.readlines()  # Lee todas las líneas del archivo
    f.close()  # Cierra el archivo
    return lines

def read_temp():
    """
    Procesa las líneas crudas para extraer y convertir la temperatura a grados Celsius.
    
    :return: La temperatura leída desde el sensor DS18B20 en grados Celsius.
    """
    lines = read_temp_raw()  # Obtiene las líneas crudas del archivo del sensor
    # Espera hasta que la primera línea termine en 'YES', indicando una lectura exitosa
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)  # Espera 200 ms antes de intentar leer de nuevo
        lines = read_temp_raw()  # Reintenta leer las líneas crudas del archivo del sensor
    equals_pos = lines[1].find('t=')  # Busca la posición de 't=' en la segunda línea
    if equals_pos != -1:  # Si se encuentra 't='
        temp_string = lines[1][equals_pos+2:]  # Extrae la parte de la cadena que representa la temperatura
        temp_c = float(temp_string) / 1000.0  # Convierte la cadena de temperatura a flotante y la divide por 1000 para obtener grados Celsius
        return temp_c  # Devuelve la temperatura en grados Celsius
