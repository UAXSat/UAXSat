# install_all.sh

#!/bin/bash

# Actualizar el sistema
sudo apt-get update -y && sudo apt-get upgrade -y

# Instalar PostgreSQL
echo "Instalando PostgreSQL..."
sudo apt-get install -y postgresql postgresql-contrib

# Habilitar y arrancar PostgreSQL
sudo systemctl enable postgresql
sudo systemctl start postgresql
echo "PostgreSQL instalado y ejecutándose."

# Añadir repositorio de Grafana
echo "Añadiendo repositorio de Grafana..."
sudo apt-get install -y software-properties-common
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"

# Actualizar repositorios e instalar Grafana
echo "Instalando Grafana..."
sudo apt-get update -y
sudo apt-get install -y grafana

# Habilitar y arrancar Grafana
sudo systemctl enable grafana-server
sudo systemctl start grafana-server
echo "Grafana instalado y ejecutándose."

# Mostrar estado de PostgreSQL y Grafana
echo "PostgreSQL status:"
sudo systemctl status postgresql

echo "Grafana status:"
sudo systemctl status grafana-server

# Instalar librerías de Python con pip3
echo "Instalando librerías de Python necesarias..."
sudo pip3 install adafruit-circuitpython-icm20x --break-system-packages
sudo pip3 install adafruit-circuitpython-bmp3xx --break-system-packages
sudo pip3 install sparkfun-ublox-gps --break-system-packages
sudo pip3 install adafruit-blinka --break-system-packages
sudo pip3 install adafruit-circuitpython-busdevice --break-system-packages
sudo pip3 install psycopg2-binary --break-system-packages
sudo pip3 install gpiozero --break-system-packages

sudo usermod -aG gpio $USER

echo "Instalación de PostgreSQL, Grafana y librerías Python completada."


""" Ejecuta los siguientes comandos para proceder a la instalacion

chmod +x install.sh
./install.sh

"""