"""- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - *

                         Developed by Javier Bolanos
                    https://github.com/javierbolanosllano

                           UAXSAT IV Project - 2024
                       https://github.com/UAXSat/UAXSat

* - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - """

#!/usr/bin/env python3

# receiversetparamtest.py
import E220900T30D as e220
import RPi.GPIO as GPIO

# Desactiva las advertencias de GPIO si los pines ya están en uso
GPIO.setwarnings(False)

def configure_lora():
    """Configura el módulo LoRa con los parámetros adecuados."""
    e220.setparam(baudrate=9600, parity='8N1', air_rate=2400, power=21, packet_size=200, channel=18)

def main():
    """Función principal para recibir mensajes a través de LoRa."""
    configure_lora()
    try:
        while True:
            message = e220.receive_message()
            if message:
                print(f"Mensaje recibido: {message}")
    except KeyboardInterrupt:
        print("Interrupción por teclado. Limpiando y saliendo...")
    except Exception as e:
        print(f"Error inesperado: {e}")
    finally:
        e220.clean_gpio()  # Asegura liberar los pines GPIO

if __name__ == "__main__":
    main()