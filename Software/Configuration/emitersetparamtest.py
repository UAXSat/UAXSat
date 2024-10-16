"""- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - *

                         Developed by Javier Bolanos
                    https://github.com/javierbolanosllano

                           UAXSAT IV Project - 2024
                       https://github.com/UAXSat/UAXSat

* - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - """

#!/usr/bin/env python3

# emitersetparamtest.py
import E220900T30D as e220
import time
import RPi.GPIO as GPIO
GPIO.setwarnings(False)

def main():
    try:
        # Configurar el módulo LoRa usando setparam
        e220.setparam(baudrate=9600, parity='8N1', air_rate=2400, power=21, packet_size=200, channel=18)
        print("Módulo LoRa configurado correctamente.")

        while True:
            # Ejemplo de mensaje que envías
            message = "Mensaje de prueba"
            e220.send_message(message)
            time.sleep(5)  # Envía un mensaje cada 5 segundos
    except KeyboardInterrupt:
        print("Interrupción por teclado. Limpiando y saliendo...")
    except Exception as e:
        print(f"Error inesperado: {e}")
    finally:
        e220.clean_gpio()  # Asegura liberar los pines GPIO

if __name__ == "__main__":
    main()
