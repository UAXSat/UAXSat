import smbus
import time

def scan_i2c_bus(bus_number=1):
    bus = smbus.SMBus(bus_number)
    devices = []
    for address in range(3, 128):
        try:
            bus.write_quick(address)
            devices.append(hex(address))
        except IOError:
            pass
    return devices

if __name__ == "__main__":
    print("Scanning I2C bus for devices... (Press Ctrl+C to stop)")
    while True:
        devices = scan_i2c_bus()
        if devices:
            print(f"Found devices at addresses: {', '.join(devices)}")
        else:
            print("No devices found.")
        time.sleep(1)  # Añade un retraso de 1 segundo entre escaneos para evitar saturar la CPU
