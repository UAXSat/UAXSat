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
    # Obtener las estadísticas del sistema
    system_stats = {
        "CPU Usage (%)": psutil.cpu_percent(interval=1),
        "RAM Usage (MB)": psutil.virtual_memory().used / (1024 ** 2),
        "Total RAM (MB)": psutil.virtual_memory().total / (1024 ** 2),
        "Disk Usage (%)": psutil.disk_usage('/').percent,
        "Disk Usage (GB)": psutil.disk_usage('/').used / (1024 ** 3),
        "Total Disk (GB)": psutil.disk_usage('/').total / (1024 ** 3),
    }
    
    # Obtener información de la temperatura del sistema
    temp_sensors = psutil.sensors_temperatures()
    if 'cpu_thermal' in temp_sensors:
        # Acceder a la primera temperatura en la lista de sensores
        cpu_temp = temp_sensors['cpu_thermal'][0].current
        system_stats["Temperature (°C)"] = cpu_temp
    else:
        system_stats["Temperature (°C)"] = "N/A"  # No disponible si no hay datos

    return system_stats
