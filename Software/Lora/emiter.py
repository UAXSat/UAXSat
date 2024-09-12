"""* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
*                                                                            *
*                         Developed by Javier Bolanos                        *
*                  https://github.com/javierbolanosllano                     *
*                                                                            *
*                      UAXSAT IV Project - 2024                              *
*                   https://github.com/UAXSat/UAXSat                         *
*                                                                            *
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *"""

# emiter.py
import json
import time
from serial.tools import list_ports
from e220 import E220, MODE_NORMAL, AUX, M0, M1, VID_PID_LIST

from Modules.IMUmodule import get_IMU_data
from Modules.UVmodule import get_UV_data
from Modules.BMPmodule import get_BMP_data
from Modules.DS18B20module import get_DS18B20_data
from Modules.GPSmodule import get_GPS_data
from Modules.SYSTEMmodule import get_system_data

def find_serial_port(vendor_id, product_id):
    """Encuentra y devuelve el puerto serial para un dispositivo con el VID y PID dados."""
    ports = list_ports.comports()
    for port in ports:
        if port.vid == vendor_id and port.pid == product_id:
            return port.device
    return None

def get_all_sensor_data():
    """Recoge datos de todos los sensores conectados."""
    sensor_data = {}

    # Obtener datos de los diferentes sensores
    sensor_data['IMU'] = get_IMU_data()         # ICM20948
    sensor_data['UV'] = get_UV_data()           # AS7331
    sensor_data['BMP'] = get_BMP_data()         # BMP390
    sensor_data['Dallas'] = get_DS18B20_data()  # DS18B20
    sensor_data['GPS'] = get_GPS_data()         # GPS NEO M9N
    sensor_data['System'] = get_system_data()   # Sistema (CPU, RAM...)

    return sensor_data

def main():
    # Encontrar el puerto serial del módulo E220
    uart_port = None
    for vid, pid in VID_PID_LIST:
        uart_port = find_serial_port(vid, pid)
        if uart_port:
            break

    if uart_port is None:
        print("Dispositivo no encontrado. Por favor, verifica tus conexiones.")
        exit(1)

    print(f"Dispositivo encontrado en {uart_port}, inicializando el módulo E220900T30D")

    try:
        lora_module = E220(m0_pin=M0, m1_pin=M1, aux_pin=AUX, uart_port=uart_port)

        # Configurar el módulo en modo de operación normal
        lora_module.set_mode(MODE_NORMAL)
        print("Módulo en modo de operación normal.")

        while True:  # Bucle infinito para enviar mensajes
            # Obtener todos los datos de los sensores
            all_sensor_data = get_all_sensor_data()

            # Convertir los datos en formato JSON
            all_sensor_data_json = json.dumps(all_sensor_data)

            # Imprimir los datos en formato JSON
            print(f"{all_sensor_data_json}")

            # Enviar los datos por LoRa
            lora_module.send_data(all_sensor_data_json)
            print("Datos enviados a tierra correctamente.")

            # Pausa entre lecturas para evitar saturar la CPU
            time.sleep(5)

    except KeyboardInterrupt:
        print("KeyboardInterrupt: Saliendo del programa.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Asegurarse de que el puerto serial se cierre correctamente
        if 'lora_module' in locals():
            lora_module.close()

if __name__ == "__main__":
    main()
