"""- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - *

                         Developed by Javier Bolanos
                    https://github.com/javierbolanosllano

                           UAXSAT IV Project - 2024
                       https://github.com/UAXSat/UAXSat

* - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - """

# SYSTEMmodule
import psutil
import time

def get_system_data():
    """Recoge estadísticas del sistema de la Raspberry Pi."""

    # Uso de CPU
    cpu_usage = psutil.cpu_percent(interval=1)

    # Uso de RAM
    virtual_mem = psutil.virtual_memory()
    ram_usage_percent = virtual_mem.percent

    # Sensores de temperatura (CPU)
    temp_sensors = psutil.sensors_temperatures()
    cpu_temp = None

    # Verifica si hay sensores de temperatura disponibles y si el sensor "cpu_thermal" está presente
    if 'cpu_thermal' in temp_sensors:
        cpu_temp = temp_sensors['cpu_thermal'][0].current

    # Construcción del diccionario con las estadísticas solicitadas
    system_stats = {
        "CPU_Usage": cpu_usage,
        "RAM_Usage": ram_usage_percent,
        "CPU_Temperature": cpu_temp
    }

    return system_stats

# Función principal para ejecución continua
def main():

    while True:
        sysdata = get_system_data()
        if sysdata:
            print(sysdata)
        else:
            print("Error initializing the IMU")
        time.sleep(1)

# Ejecutar el sensor si se ejecuta como script principal
if __name__ == "__main__":
    main()
