"""* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
*                                                                            *
*                         Developed by Javier Bolanos                        *
*                  https://github.com/javierbolanosllano                     *
*                                                                            *
*                      UAXSAT IV Project - 2024                              *
*                   https://github.com/UAXSat/UAXSat                         *
*                                                                            *
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *"""

# constants.py

# CONSTANTS (GPIO pin numbers for M0, M1, AUX)
M0 = 17
M1 = 27
AUX = 22

# Define operating modes for the E220 module
MODE_NORMAL = (0, 0)
MODE_WOR_TRANSMIT = (0, 1)
MODE_WOR_RECEIVE = (1, 0)
MODE_SLEEP = (1, 1)

# Define VID and PID for the E220 module
VID_PID_LIST = [
    (0x10C4, 0xEA60),  # Example VID and PID for the E220 module
    (0x1A86, 0x7523)   # Another possible VID and PID
]

# Define the initial coordenates (latitude and longitude)
initial_lat = 40.416775    # Puerta del Sol, Madrid
initial_lon = -3.703790    # Puerta del Sol, Madrid

'''
initial_lat = 40.416775  # Ejemplo de latitud inicial
initial_lon = -3.703790  # Ejemplo de longitud inicial
'''
