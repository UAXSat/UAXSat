---

## 💾 Software  

The software is **modularized** for better **readability and maintainability.**  

### 🔹 **Modules**  
Each module follows a structured pattern:  
1️⃣ **Sensor Initialization** – Setting up the sensor.  
2️⃣ **Data Acquisition** – Retrieving data from the sensor.  
3️⃣ **Function for Main Code** – Callable functions for use in the main program.  

### 🔍 **System Check**  
We have developed scripts to verify protocol connections, including **I²C, Serial, SPI, and UART.**  

### ⚙️ **Configuration**  
The `configuration` folder contains scripts for **LoRa communication**:  
- **`E220900T30D.py`** – The main module for the LoRa module.  
- **`set_param.py`** – A script for configuring specific LoRa parameters.  

### 🛠️ **Utility Scripts**  
Several additional scripts provide essential functions used in the **emitter and receiver** codes:  
- **`db_function.py`** – Handles database operations.  
- **`lora_functions.py`** – Contains functions for LoRa communication.  
- **`constants.py`** – Stores predefined values and configurations.

---
