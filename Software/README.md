## Software

The software is organized into separate modules for each sensor to improve code readability and maintainability.

### Modules
Each module follows a consistent structure:
- Sensor Initialization – Setting up the sensor.
- Data Acquisition – Retrieving data from the sensor.
- Function for Main Code – A callable function for use in the main program.

### Check
We have developed several scripts to verify the proper functioning of protocol connections, including I²C, Serial, SPI, and UART.

### Configuration
The configuration folder contains all the modules developed for the LoRa communication system.
- `E220900T30D` Script – The main module for the LoRa module.
- `set_param` Script – A utility script for configuring specific parameters on the LoRa module.

### Utility Scripts
Several additional scripts provide essential functions used in the main emitter and receiver codes:
- `db_function` – Handles database-related operations.
- `lora_functions` – Contains functions for LoRa communication.
- `constants` – Stores predefined values and configurations used throughout the system.
