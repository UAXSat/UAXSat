# 🚀 UAXSAT IV  

Welcome to the **UAXSat IV** project repository!  

## 📖 About  

UAXSat IV is a **cubesat project** developed by 2nd and 3rd-year Aerospace Engineering students at **Universidad Alfonso X el Sabio (UAX).** The objective is to **design, build, and launch** a small satellite into the **stratosphere** for scientific research and Earth observation.  

---

## 🌍 Features  

✅ **GPS tracking**  
✅ **LoRa communications**  
✅ **Earth observation (forests monitoring)**  
✅ **Temperature measurements**  
✅ **Pressure measurements**  
✅ **UV measurements**  
✅ **Inertial measurements**  

---

## 🛰️ Hardware  

### 🔧 **Sensors**  

| Sensor | Component |
|--------|-----------|
| **GPS** | Sparkfun GPS NEO M9N SMA |
| **LoRa Module** | Ebyte E220 900T30D |
| **Temperature Sensor** | DS18B20 |
| **Pressure Sensor** | BMP390 |
| **IMU Sensor** | ICM 20948 |
| **UV Sensor** | AS7331 |
| **Camera Module** | GoPro Hero 11 |

### 💻 **On-Board Computer**  
- Raspberry Pi 4  

### 🏠 **Ground Station**  
- **Main Computer**: Raspberry Pi 3B  
- **LoRa Module**: Ebyte E220 900T30D  
- **Antenna**: Yagi Antenna  

📡 The ground station runs **PostgreSQL** and **Grafana** servers on a Raspberry Pi 3B. It is connected to the **LoRa module**, which interfaces with the **Yagi antenna** for communication with the CubeSat.  

---

## Libraries
You will need to have the following libraries installed:

- board
- busio
- adafruit_icm20x
- adafruit_bmp3xx
- serial
- ublox_gps
- adafruit_bus_device

### 🔧 Installing Dependencies Automatically  

To simplify the installation process, we have provided an **install script** that automatically installs all the necessary dependencies.  

#### 📌 Steps to Run the Installation Script  

1️⃣ Open a terminal and navigate to the **root folder of the repository**.  

2️⃣ Run the following commands:  

```bash
# Grant execution permissions to the install script
chmod +x install.sh  

# Run the script to install all required dependencies
./install.sh  
```
✅ This script will:
- Install all necessary libraries
- Set up required system dependencies
- Ensure your environment is correctly configured for Grafana, PostgreSQL, and other tools

---

## 🌍 Community  

Join our **community discussions** to stay updated, collaborate, and contribute:  
📢 [GitHub Discussions](https://github.com/JaviLendi/UAXSat/discussions)  

---

## ⚖️ License  

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.  

---

## 👨‍💻 Developers & Organizers  

### 🎯 **Project Organizers**  
- **Javier Bolaños** ([GitHub](https://github.com/javierbolanosllano)) ([LinkedIn](https://www.linkedin.com/in/javierbolanosllano/))  
- **Javier Lendínez Castillo** ([GitHub](https://github.com/JaviLendi)) ([LinkedIn](https://www.linkedin.com/in/javierlendinez/))  

### 💻 **Software Developers**  
- **Javier Bolaños Llano** ([GitHub](https://github.com/javierbolanosllano)) ([LinkedIn](https://www.linkedin.com/in/javierbolanosllano/))  
- **Javier Lendínez Castillo** ([GitHub](https://github.com/JaviLendi)) ([LinkedIn](https://www.linkedin.com/in/javierlendinez/))  
- **Alonso Lozano Garcia** ([LinkedIn](https://www.linkedin.com/in/alonso-l-b75102254/))  

### 🔩 **Hardware Developers**  
- **Javier Lendínez Castillo** ([GitHub](https://github.com/JaviLendi)) ([LinkedIn](https://www.linkedin.com/in/javierlendinez/))  
- **Laura Rodríguez** ([LinkedIn](https://www.linkedin.com/in/laura-rodr%C3%ADguez-sotillo-3711811a5/))  
- **Alonso Lozano Garcia** ([LinkedIn](https://www.linkedin.com/in/alonso-l-b75102254/))  
- **Juan Coleto** ([LinkedIn](https://www.linkedin.com/in/juan-coleto-arteche-4b2600309/))  
- **Alba Herrero** ([LinkedIn](https://www.linkedin.com/in/alba-herrero-prado-515102257/))  
- **Pablo del Río Torrecilla** ([LinkedIn]())  
- **Álvaro Rodríguez** ([LinkedIn]())  
- **Mónica Martín** ([LinkedIn]())  

---

## 🙌 Acknowledgements  

Special thanks to the following organizations and individuals for their support:  

- 🎓 **Universidad Alfonso X el Sabio** ([Website](https://www.uax.com/))  
- 🚀 **B2Space** ([Website](https://b2-space.com/))  
- 🎖 **Ricardo Atienza** ([LinkedIn](https://www.linkedin.com/in/ricardo-atienza))  
- 🎖 **Jesús Isidro Jiménez** ([LinkedIn](https://www.linkedin.com/in/jesus-isidro-jimenez-3577b8153/))  

---

