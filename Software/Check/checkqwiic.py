"""* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
*                                                                            *
*                         Developed by Javier Bolanos                        *
*                  https://github.com/javierbolanosllano                     *
*                                                                            *
*                      UAXSAT IV Project - 2024                              *
*                   https://github.com/UAXSat/UAXSat                         *
*                                                                            *
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *"""

#checkqwiic
import smbus2
import time

class QwiicScanner:
    def __init__(self, bus_number=1, scan_interval=10):
        """
        Inicializa el esc  ner Qwiic.
        
        :param bus_number: El n  mero del bus I2C (1 corresponde a /dev/i2c-1)
        :param scan_interval: El intervalo de tiempo en segundos entre cada escaneo
        """
        self.bus_number = bus_number
        self.scan_interval = scan_interval
        self.bus = smbus2.SMBus(bus_number)
    
    def scan(self):
        """
        Escanea el bus I2C para encontrar dispositivos Qwiic.
        
        :return: Una lista de direcciones de dispositivos encontrados
        """
        devices = []

        print("Escaneando el bus I2C para dispositivos Qwiic...")

        for address in range(0x03, 0x77):
            try:
                self.bus.read_byte(address)
                devices.append(hex(address))
            except OSError:
                pass

        if devices:
            print("Dispositivos Qwiic encontrados en las siguientes direcciones:")
            for device in devices:
                print(f" - {device}")
        else:
            print("No se encontraron dispositivos Qwiic.")
        
        return devices

    def start_scanning(self):
        """
        Comienza a escanear peri  dicamente el bus I2C.
        """
        try:
            while True:
                self.scan()
                time.sleep(self.scan_interval)
        except KeyboardInterrupt:
            print("Escaneo detenido por el usuario.")
        finally:
            self.bus.close()

if __name__ == "__main__":
    scanner = QwiicScanner(scan_interval=2)  # Puedes ajustar el intervalo de escaneo aqu  
    scanner.start_scanning()