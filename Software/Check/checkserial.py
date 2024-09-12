"""* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
*                                                                            *
*                         Developed by Javier Bolanos                        *
*                  https://github.com/javierbolanosllano                     *
*                                                                            *
*                      UAXSAT IV Project - 2024                              *
*                   https://github.com/UAXSat/UAXSat                         *
*                                                                            *
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *"""

#checkserial
import serial.tools.list_ports

class SerialDeviceScanner:
    def __init__(self):
        self.serial_devices = self.list_serial_devices()

    def list_serial_devices(self):
        """Lista todos los dispositivos serie disponibles."""
        ports = serial.tools.list_ports.comports()
        devices = []
        for port in ports:
            devices.append({
                "port": port.device,
                "description": port.description,
                "hwid": port.hwid
            })
        return devices

    def get_serial_device_by_port(self, port_name):
        """Obtiene informaci  n detallada de un dispositivo serie dado su nombre de puerto."""
        for device in self.serial_devices:
            if device['port'] == port_name:
                return device
        return None

    def get_serial_device_by_hwid(self, hwid):
        """Obtiene informaci  n detallada de un dispositivo serie dado su HWID."""
        for device in self.serial_devices:
            if device['hwid'] == hwid:
                return device
        return None

    def print_serial_devices(self):
        """Imprime en consola la informaci  n de todos los dispositivos serie encontrados."""
        if self.serial_devices:
            print("Dispositivos serie encontrados:")
            for device in self.serial_devices:
                print(f"Puerto: {device['port']}")
                print(f"Descripci  n: {device['description']}")
                print(f"HWID: {device['hwid']}\n")
        else:
            print("No se encontraron dispositivos serie.")

# Uso de la clase SerialDeviceScanner
if __name__ == "__main__":
    scanner = SerialDeviceScanner()
    scanner.print_serial_devices()