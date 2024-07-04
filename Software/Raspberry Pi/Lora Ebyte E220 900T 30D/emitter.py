# emitter.py
from lora_module import LoRaModule
import time

class LoRaEmitter(LoRaModule):
    def __init__(self, port=None, baud_rate=9600, timeout=1, m0_pin=17, m1_pin=27):
        super().__init__(port, baud_rate, timeout, m0_pin, m1_pin)

    def send_message(self, message):
        self.send_data(message)

if __name__ == "__main__":
    emitter = LoRaEmitter()
    try:
        while True:
            emitter.send_message("Hola, mundo!")
            time.sleep(2)  # Espera 2 segundos entre mensajes
    except KeyboardInterrupt:
        print("Interrumpido por el usuario")
    finally:
        emitter.close()
