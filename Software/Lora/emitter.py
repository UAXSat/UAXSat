# emitter.py
# emitter.py
import json
import time
from datetime import datetime
import logging
from serial.tools import list_ports
from e220 import E220
from constants import M0, M1, AUX, VID_PID_LIST, MODE_NORMAL, initial_lat, initial_lon

# Import sensor modules
from Modules.IMUmodule import get_IMU_data
from Modules.UVmodule import get_UV_data
from Modules.BMPmodule import get_BMP_data
from Modules.DS18B20module import get_DS18B20_data
from Modules.GPSmodule import get_GPS_data
from Modules.SYSTEMmodule import get_system_data

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_all_sensor_data():
    """
    Gather data from all connected sensors.
    :return: Dictionary containing sensor data
    """
    logger.debug("Gathering data from all sensors.")
    sensor_data = {
        'IMU': get_IMU_data(),
        'UV': get_UV_data(),
        'BMP': get_BMP_data(),
        'Dallas': get_DS18B20_data(),
        'GPS': get_GPS_data(initial_lat, initial_lon),
        'System': get_system_data()
    }
    logger.debug(f"Sensor data collected: {sensor_data}")
    return sensor_data

def main():
    uart_port = None
    # Try to find the E220 LoRa module's serial port by its VID and PID
    for vid, pid in VID_PID_LIST:
        uart_port = E220.find_serial_port(vid, pid)
        if uart_port:
            break

    if uart_port is None:
        logger.error("LoRa module not found. Check connections.")
        exit(1)

    logger.info(f"LoRa module found at {uart_port}, initializing.")

    try:
        # Initialize the E220 module
        lora_module = E220(m0_pin=17, m1_pin=27, aux_pin=22, uart_port=uart_port)
        logger.info("E220 module initialized and set to normal mode.")

        while True:
            # Gather sensor data
            all_sensor_data = get_all_sensor_data()

            # Add timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            all_sensor_data['timestamp'] = timestamp

            # Convert sensor data to JSON format
            all_sensor_data_json = json.dumps(all_sensor_data)

            # Prepare the message with markers
            message = f"<<<{all_sensor_data_json}>>>"

            # Log the message to be sent
            logger.debug(f"Message to be sent: {message}")

            # Send the data via LoRa
            lora_module.send_data(message)
            logger.info("Data sent to ground station successfully.")

            # Wait for 5 seconds before the next transmission
            time.sleep(5)

    except KeyboardInterrupt:
        logger.info("Program interrupted by user, exiting.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        # Ensure the module is closed properly
        lora_module.close()

if __name__ == "__main__":
    main()
