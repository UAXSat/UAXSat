"""* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
*                                                                            *
*                         Developed by Javier Bolanos                        *
*                  https://github.com/javierbolanosllano                     *
*                                                                            *
*                      UAXSAT IV Project - 2024                              *
*                   https://github.com/UAXSat/UAXSat                         *
*                                                                            *
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *"""

#checkuart
import os

class UartPortDetector:
    def __init__(self):
        self.uart_ports = self.detect_uart_ports()

    def detect_uart_ports(self):
        """Detecta los puertos UART disponibles en /dev."""
        uart_ports = []
        for device in os.listdir('/dev'):
            if device.startswith('ttyAMA') or device.startswith('ttyS'):
                uart_ports.append('/dev/' + device)
        return uart_ports

    def print_uart_ports(self):
        """Imprime en consola la lista de puertos UART detectados."""
        if not self.uart_ports:
            print("No se encontraron puertos UART activos.")
        else:
            print("Puertos UART detectados:")
            for port in self.uart_ports:
                print(port)

# Uso de la clase UartPortDetector
if __name__ == "__main__":
    detector = UartPortDetector()
    detector.print_uart_ports()