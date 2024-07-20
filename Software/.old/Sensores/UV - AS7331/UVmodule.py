"""***************************************************************************
*                                                                            *
*                      UAXSAT IV Project - 2024                              *
*                  Developed by Javier Bolaños Llano                         *
*                 https://github.com/javierbolanosllano                      *
*                                                                            *
***************************************************************************"""

# UVmodule.py
import sys
import board
import AS7331 as as7331

sys.path.append('src')

def initialize_sensor():
    sensor = as7331.AS7331(board.I2C())
    sensor.gain = as7331.GAIN_512X
    sensor.integration_time = as7331.INTEGRATION_TIME_128MS
    return sensor

def get_sensor_status(sensor):
    return {
        'chip_id': sensor.chip_id,
        'device_state': sensor.device_state_as_string,
        'gain': sensor.gain_as_string,
        'integration_time': sensor.integration_time_as_string,
        'divider_enabled': sensor.divider_enabled,
        'divider': sensor.divider,
        'power_down_enable': sensor.power_down_enable,
        'standby_state': sensor.standby_state
    }

def read_sensor_data(sensor):
    try:
        uva, uvb, uvc, temp = sensor.values
        return {'UVA': uva, 'UVB': uvb, 'UVC': uvc, 'temp': temp}
    except as7331.AS7331Overflow as err:
        print('Sensor Overflow Error:', err)
        return None