"""* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
*                                                                            *
*                         Developed by Javier Bolanos                        *
*                  https://github.com/javierbolanosllano                     *
*                                                                            *
*                      UAXSAT IV Project - 2024                              *
*                   https://github.com/UAXSat/UAXSat                         *
*                                                                            *
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *"""

# SYSTEMmodule
import psutil

def get_system_data():
    """Recoge estadísticas del sistema de la Raspberry Pi."""

    # Uso de CPU
    cpu_usage = psutil.cpu_percent(interval=1)

    # Uso de RAM
    virtual_mem = psutil.virtual_memory()
    ram_usage_percent = virtual_mem.percent

    # Sensores (temperatura y ventiladores)
    temp_sensors = psutil.sensors_temperatures()
    fan_sensors = psutil.sensors_fans()

    # Construcción del diccionario con las estadísticas solicitadas
    system_stats = {
        "CPU Usage (%)": cpu_usage,
        "RAM Usage (%)": ram_usage_percent,
        "Sensors": {
            "Temperatures": {
                sensor: [{
                    "Current": temp.current
                } for temp in temps]
                for sensor, temps in temp_sensors.items()
            },
            "Fans": {
                fan: [{
                    "Current RPM": f.current
                } for f in fans]
                for fan, fans in fan_sensors.items()
            }
        }
    }

    return system_stats