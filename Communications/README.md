# Communications

UAXSat IV has LoRa communications, we developed a custom MQTT protocol to send and receive data from the satellite. The data from the satellite is sent to a ground station (LoRa), which is then sent to a server. The server (MQTT) then sends the data to the client (Grafana).

## LoRa

LoRa is a long-range, low-power wireless platform that has become the de facto technology for Internet of Things (IoT) networks worldwide. It is a modulation technique that provides significantly longer range than competing technologies. LoRa is a proprietary spread spectrum modulation scheme that is derivative of chirp spread spectrum modulation (CSS) and which trades data rate for sensitivity within a fixed channel bandwidth.

## MQTT

MQTT is a machine-to-machine (M2M)/"Internet of Things" connectivity protocol. It was designed as an extremely lightweight publish/subscribe messaging transport. It is useful for connections with remote locations where a small code footprint is required and/or network bandwidth is at a premium.

## Grafana

Grafana is an open-source platform for monitoring and observability. It allows you to query, visualize, alert on, and understand your metrics no matter where they are stored. Create, explore, and share dashboards with your team and foster a data-driven culture.

# Instructions for using the code

## Libraries
When running MQTTdata.py you will need to have the following libraries installed:

- paho-mqtt
- board
- busio
- adafruit_icm20x
- adafruit_bmp3xx
- serial
- ublox_gps
- adafruit_bus_device

## Data logging
- For logging data from the sensors, you will need to modify the path of the file in the code to save it where you want. (logging.basicConfi)
- For saving the data transmitted to a csv file you would have to specify the path in the code. (csv_file_path = "/home/user/sensor_data.csv")

## MQTT
- You will need to have a server running to receive the data from the satellite. The default hostname is "localhost" and the default port is 3000. 
- You will need to have a client running to receive the data from the server. The default hostname is "localhost" and the default port is 3000.
- Tu run the MQTT client you will need to run the MQTTdata.py file.

### Running the MQTT code
- For ease of use you can create a service to run the MQTT code in the background.
- To create a service you will need to create a file in /etc/systemd/system/ called mqttclient.service
- In the file you will need to add the following code:
```bash
[Unit]
Description=MQTT client service
After=multi-user.target

[Service]
Type=simple
Environment=TERM=xterm
ExecStart=/usr/bin/python3 /home/user/UAXSat/Communications/MQTTdata.py
User=yourusername
Group=yourusername
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```
- After creating the file you will need to run the following commands:
```bash
sudo systemctl daemon-reload
sudo systemctl enable mqttclient.service
sudo systemctl start mqttclient.service
```
- To check the status of the service you can run:
```bash
sudo systemctl status mqttclient.service
```

-To check de error log you can:
```bash
journalctl -u mqttclient.service
tail -f error.log
```

### Using PostgreSQL

- To install PostgreSQL you can run the following commands:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```
- To create a new user you can run the following commands:
```bash
sudo -i -u postgres
psql
CREATE DATABASE grafana;
CREATE USER grafana WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE grafana TO grafana;
\q
exit
```
- Configure Grafana to use PostgreSQL as the database.
```bash
sudo nano /etc/grafana/grafana.ini
```

- Locate the [database] section. It should look something like this:
```bash
#################################### Postgres DB ####################################
[database]
type = postgres
host = 127.0.0.1:5432
name = grafana
user = grafana
password = yourpassword
```

- Change Authentication Method:

```bash
sudo nano /etc/postgresql/15/main/pg_hba.conf
```
- Change the following line:
```bash
local   all             all                                     peer
```
- To:
```bash
local   all             all                                     md5
```
- Reload PostgreSQL:
```bash
sudo systemctl reload postgresql
```

- Create a new schema
First you need to sign in as the postgres user and then create a new schema and grant the necessary permissions to the user grafana.
```bash
sudo -i -u postgres
psql
CREATE SCHEMA grafana_schema AUTHORIZATION grafana;
GRANT CREATE ON SCHEMA grafana_schema TO grafana;
```

- Create a new table
```bash
CREATE TABLE grafana_schema.sensor_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    cpu_temp FLOAT,
    cpu_usage FLOAT,
    ram_usage FLOAT,
    latitude FLOAT,
    longitude FLOAT,
    altitude FLOAT,
    heading_motion FLOAT,
    roll TEXT,
    pitch TEXT,
    heading TEXT,
    nmea_sentence TEXT,
    acceleration JSONB,
    gyro JSONB,
    magnetic JSONB,
    uva FLOAT,
    uvb FLOAT,
    uvc FLOAT,
    uv_temp FLOAT,
    temperature FLOAT
);
```

- Final verifications:
```bash
\dt grafana_schema.sensor_data
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE grafana_schema.sensor_data TO grafana;
```

- To sign is as grafana user:
```bash
psql -U grafana -d grafana
```


## Grafana
To be done...

- Restart the Grafana service:
```bash
sudo systemctl restart grafana-server
```

- To check the status of the service you can run:
```bash
sudo systemctl status grafana-server
```

![graf](https://github.com/user-attachments/assets/c89a8089-0d4d-4fb3-bfcc-7217d1fd9937)
