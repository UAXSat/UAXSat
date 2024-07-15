"""*********************************************************************************************************
*                                                                                                          *
*                                     UAXSAT IV Project - 2024                                             *
*                       Developed by Javier Bolaños Llano and Javier Lendinez                              *
*                                https://github.com/UAXSat                                                 *
*                                                                                                          *
*********************************************************************************************************"""

# ds18b20.py
import os
import time

class DallasSensor:
    BASE_DIR = '/sys/bus/w1/devices/'

    def __init__(self):
        self.sensors = self.detect_sensors()

    def detect_sensors(self):
        """Detects and returns a list of Dallas DS18B20 sensor IDs."""
        try:
            sensor_folders = [f for f in os.listdir(self.BASE_DIR) if f.startswith('28-')]
            return sensor_folders
        except FileNotFoundError:
            print("1-Wire interface not found. Ensure 1-Wire is enabled and the sensor is properly connected.")
            return []

    def read_sensor_data(self, sensor_id):
        """Reads the raw data from a specific Dallas sensor."""
        sensor_file = os.path.join(self.BASE_DIR, sensor_id, 'w1_slave')
        try:
            with open(sensor_file, 'r') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Sensor {sensor_id} data file not found.")
            return None

    def parse_temperature(self, raw_data):
        """Parses the temperature from the raw sensor data."""
        try:
            lines = raw_data.strip().split("\n")
            if "YES" in lines[0]:
                equals_pos = lines[1].find('t=')
                if equals_pos != -1:
                    temp_string = lines[1][equals_pos + 2:]
                    temp_c = float(temp_string) / 1000.0
                    return temp_c
        except Exception as e:
            print(f"Error parsing temperature: {e}")
        return None

    def get_sensor_info(self):
        """Returns a dictionary of sensor IDs and their temperatures."""
        info = {}
        for sensor in self.sensors:
            raw_data = self.read_sensor_data(sensor)
            if raw_data:
                temp = self.parse_temperature(raw_data)
                if temp is not None:
                    info[sensor] = temp
        return info

    def refresh(self):
        """Refresh the list of sensors and their data."""
        self.sensors = self.detect_sensors()

    def __repr__(self):
        return f"DallasSensor(sensors={self.sensors})"

def main():
    dallas_sensor = DallasSensor()
    
    while True:
        sensor_info = dallas_sensor.get_sensor_info()
        if sensor_info:
            for sensor_id, temperature in sensor_info.items():
                print(f"Sensor ID: {sensor_id}, Temperature: {temperature:.2f} °C")
        else:
            print("No sensors found. Retrying in 5 seconds...")
        
        time.sleep(1)

if __name__ == '__main__':
    main()

