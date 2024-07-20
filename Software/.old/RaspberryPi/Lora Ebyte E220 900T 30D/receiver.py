# receiver.py
from lora_module import LoRaModule
import time

class LoRaReceiver(LoRaModule):
    def __init__(self, port=None, baud_rate=9600, timeout=1, m0_pin=17, m1_pin=27):
        super().__init__(port, baud_rate, timeout, m0_pin, m1_pin)

    def receive_message(self):
        return self.receive_data()

if __name__ == "__main__":
    receiver = LoRaReceiver()
    try:
        while True:
            message = receiver.receive_message()
            if message:
                print(f"Mensaje recibido: {message}")
            time.sleep(1)  # Espera 1 segundo antes de intentar recibir de nuevo
    except KeyboardInterrupt:
        print("Interrumpido por el usuario")
    finally:
        receiver.close()
