# lora_module.py
import serial
import serial.tools.list_ports
import RPi.GPIO as GPIO
import time

class LoRaModule:
    def __init__(self, port=None, baud_rate=9600, timeout=1, m0_pin=17, m1_pin=27):
        if port is None:
            port = self.find_lora_port()
        if port is None:
            raise Exception("No se encontró un puerto serie para el módulo LoRa.")
        self.ser = serial.Serial(port, baud_rate, timeout=timeout)
        self.m0_pin = m0_pin
        self.m1_pin = m1_pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.m0_pin, GPIO.OUT)
        GPIO.setup(self.m1_pin, GPIO.OUT)
        self.set_transparent_mode()
        
    def set_transparent_mode(self):
        GPIO.output(self.m0_pin, GPIO.LOW)
        GPIO.output(self.m1_pin, GPIO.LOW)
        time.sleep(1)

    def send_data(self, data):
        try:
            self.ser.write(data.encode('utf-8'))
            print(f"Mensaje enviado: {data}")
        except Exception as e:
            print(f"Error enviando datos: {e}")

    def receive_data(self):
        try:
            data = self.ser.read(100)
            if data:
                return data.decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"Error recibiendo datos: {e}")
        return None

    def send_at_command(self, command):
        try:
            self.ser.write(command.encode('utf-8'))
            time.sleep(0.1)
            response = self.ser.read(100)
            return response.decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"Error enviando comando AT: {e}")
            return None

    def close(self):
        self.ser.close()
        GPIO.cleanup()

    def find_lora_port(self):
        """Detecta automáticamente el puerto en el que está conectado el módulo LoRa."""
        ports = serial.tools.list_ports.comports()
        for port in ports:
            # Se puede ajustar este filtro según el módulo específico o la configuración del sistema
            if "USB" in port.description or "UART" in port.description:
                print(f"Puerto LoRa encontrado: {port.device}")
                return port.device
        return None

# Configuración inicial del módulo para verificar
if __name__ == "__main__":
    lora = LoRaModule()
    print("Configuración del módulo LoRa:")
    response = lora.send_at_command("AT+PARAM\r\n")
    print(response)
    lora.close()
