import spidev

class SpiDeviceDetector:
    def __init__(self):
        self.detected_devices = self.detect_spi_devices()

    def detect_spi_devices(self):
        """Detecta los dispositivos SPI disponibles en los buses 0, 1 y 2."""
        detected_devices = []

        for bus in range(3):  # Buses 0, 1, 2 son los posibles en una Raspberry Pi
            for device in range(2):  # Dispositivos 0, 1 son los posibles
                try:
                    spi = spidev.SpiDev()
                    spi.open(bus, device)
                    spi.max_speed_hz = 50000  # Ajusta según las necesidades del dispositivo
                    spi.xfer([0x00])  # Envía un byte de prueba

                    # Si no se produce una excepción, el dispositivo está presente y responde
                    detected_devices.append((bus, device))
                    spi.close()
                    print(f"SPI device detected on bus {bus}, device {device}")
                except Exception as e:
                    # Si hay una excepción, el dispositivo no está presente o no responde
                    print(f"No SPI device on bus {bus}, device {device}: {e}")

        return detected_devices

    def print_detected_devices(self):
        """Imprime en consola la lista de dispositivos SPI detectados."""
        if self.detected_devices:
            print("Detected SPI devices:")
            for device in self.detected_devices:
                print(f"Bus {device[0]}, Device {device[1]}")
        else:
            print("No SPI devices detected.")

# Uso de la clase SpiDeviceDetector
if __name__ == '__main__':
    detector = SpiDeviceDetector()
    detector.print_detected_devices()
