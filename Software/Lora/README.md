# PostgreSQL Setup and Database Management Guide

This guide provides instructions for setting up a PostgreSQL database, creating users, tables, and performing common database operations. It’s designed to help you get started from scratch, even if PostgreSQL has just been installed.

## Table of Contents
1. [Installation and Access](#1-installation-and-access)
2. [Creating a User and Database](#2-creating-a-user-and-database)
3. [Creating Tables](#3-creating-tables)
4. [Modifying Tables](#4-modifying-tables)
5. [Manipulating Data](#5-manipulating-data)
6. [Granting Privileges](#6-granting-privileges)
7. [Viewing Data](#7-viewing-data)
8. [Monitoring Real-Time Data](#8-monitoring-real-time-data)
9. [Exiting PostgreSQL](#9-exiting-postgresql)

---

## 1. Installation and Access

### Installing PostgreSQL
Before using PostgreSQL, make sure it’s installed on your system. Follow these commands to install PostgreSQL on Linux:

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

### Verify PostgreSQL is Running
To verify that PostgreSQL is running, check its status:

```bash
sudo systemctl status postgresql
```

### Accessing PostgreSQL
To access PostgreSQL as the superuser `postgres`, use the following command:

```bash
sudo -i -u postgres
psql
```

## 2. Creating a User and Database

### Creating a User
To create a dedicated user for database operations, run the following SQL command inside the PostgreSQL prompt. In this example, we create a user named cubesat with a password:

```sql
CREATE USER cubesat WITH PASSWORD 'yourpassword';
```
Replace 'yourpassword' with your chosen password.

### Creating a Database
Next, create a new database that the cubesat user can manage. Run this command to create a database named cubesat_db:

```sql
CREATE DATABASE cubesat_db;
```
### Connecting to the Database
Once the database is created, connect to it using the following command:
```sql
\c cubesat_db;
```
This will switch your session to the cubesat_db database.

## 3. Creating Tables

Once connected to the database, you can create tables. Here’s an example of how to create a sensor_readings table to store sensor data:
```
sql
CREATE TABLE sensor_readings (
    id SERIAL PRIMARY KEY,
    imu_acelx NUMERIC,
    imu_acely NUMERIC,
    imu_acelz NUMERIC,
    imu_girox NUMERIC,
    imu_giroy NUMERIC,
    imu_giroz NUMERIC,
    imu_magx NUMERIC,
    imu_magy NUMERIC,
    imu_magz NUMERIC,
    lat NUMERIC,
    lon NUMERIC,
    alt NUMERIC,
    speed DOUBLE PRECISION,
    satellites DOUBLE PRECISION,
    heading DOUBLE PRECISION,
    distance DOUBLE PRECISION,
    bmp_pressure NUMERIC,
    bmp_temperature NUMERIC,
    bmp_altitude NUMERIC,
    uv_uva NUMERIC,
    uv_uvb NUMERIC,
    uv_uvc NUMERIC,
    uv_temperature NUMERIC,
    cpu_usage NUMERIC,
    ram_usage NUMERIC,
    total_ram NUMERIC,
    disk_usage NUMERIC,
    disk_usage_gb NUMERIC,
    total_disk_gb NUMERIC,
    sys_temperature NUMERIC,
    ds18b20_temperature_interior NUMERIC,
    ds18b20_temperature_exterior NUMERIC,
    timestamp TIMESTAMP WITHOUT TIME ZONE
);
```
This creates a table with columns that store sensor readings such as accelerometer values, magnetometer data, and timestamps.

## 4. Modifying Tables

### Adding a Column
To add a new column to the sensor_readings table, use the ALTER TABLE command. For example, to add a column for sensor_type:
```
sql
ALTER TABLE sensor_readings ADD COLUMN sensor_type TEXT;
```
### Dropping a Column
If a column is no longer needed, you can remove it with the following command:
```sql
ALTER TABLE sensor_readings DROP COLUMN sensor_type;
```

## 5. Manipulating Data

### Inserting Data
To insert data into the sensor_readings table, use the INSERT INTO command. Here’s an example of inserting a new row with accelerometer data and a timestamp:

```sql
INSERT INTO sensor_readings (acelx, acely, acelz, timestamp) 
VALUES (0.5, 0.3, -0.2, NOW());
```

### Deleting Data
To delete specific data, for example, all rows where acelx is less than 0, use the DELETE statement:
```sql
DELETE FROM sensor_readings WHERE acelx < 0;
```
### Updating Data
To update existing data, for instance, to set acelx to 0 where it's negative:
```sql
UPDATE sensor_readings SET acelx = 0 WHERE acelx < 0;
```

## 6. Granting Privileges

### Granting All Privileges on the Database
To grant the cubesat user all privileges on the cubesat_db database, use the following command:
```sql
GRANT ALL PRIVILEGES ON DATABASE cubesat_db TO cubesat;
```

### Granting Schema-Level Permissions
You can create a schema for more specific privileges and grant the cubesat user permission to create objects within that schema:
```sql
CREATE SCHEMA grafana_schema AUTHORIZATION cubesat;
GRANT CREATE ON SCHEMA grafana_schema TO cubesat;
```
This grants the cubesat user permission to manage objects within the grafana_schema.

## 7. Viewing Data

### Viewing Table Structure
To inspect the structure of the sensor_readings table (i.e., the columns and data types), use the following command:
```sql
\d sensor_readings;
```
This will display the table schema with all column definitions.

### Querying Data
To view data in the table, use a SELECT query. For example, to retrieve the first 10 rows:
```sql
SELECT * FROM sensor_readings LIMIT 10;
```

## 8. Monitoring Real-Time Data

You can monitor the latest data from the sensor_readings table in real-time by using the watch command in the terminal. This example refreshes every 5 seconds to show the 10 most recent entries, ordered by timestamp:

```bash
watch -n 5 psql -U cubesat -d cubesat_db -c "SELECT * FROM sensor_readings ORDER BY timestamp DESC LIMIT 10;"
```
This allows you to continuously view the latest data.

## 9. Exiting PostgreSQL

When you’re finished with your PostgreSQL session, exit the psql prompt by typing:
```sql
\q
```

# Servicio para Emisor LoRa

Este documento describe cómo crear un servicio `systemd` para ejecutar un emisor LoRa utilizando un script de Python en un sistema Linux.

## Instrucciones

### 1. Crear el archivo de servicio

Primero, crea un archivo de servicio llamado `emisor.service` en el directorio `/etc/systemd/system/`.

```bash
sudo nano /etc/systemd/system/emisor.service
```

### 2. Escribir el contenido del archivo de servicio

Añade el siguiente contenido en el archivo emisor.service. Asegúrate de ajustar la ruta de tu script Python y verificar la ruta del ejecutable de Python (/usr/bin/python3 en este ejemplo).

```ini
[Unit]
Description=Servicio para Emisor LoRa
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/cubesat/UAXSat/Software/Lora/emitter.py
WorkingDirectory=/home/cubesat/UAXSat/Software/Lora/
Restart=always
RestartSec=10
User=cubesat
Group=cubesat
StandardOutput=file:/var/log/emisor.log
StandardError=file:/var/log/emisor_error.log

[Install]
WantedBy=multi-user.target
```

### 3. Verificar permisos de ejecución

Asegúrate de que el script de Python tenga permisos de ejecución. Usa el siguiente comando:

```bash
chmod +x /home/cubesat/UAXSat/Software/Lora/emiterauxtest.py
```

### 4. Recargar systemd

Una vez creado y guardado el archivo de servicio, recarga la configuración de systemd para que detecte el nuevo servicio:

```bash
sudo systemctl daemon-reload
```

### 5. Iniciar y habilitar el servicio

Para iniciar el servicio manualmente:

```bash
sudo systemctl start emisor.service
```

Para habilitar el servicio y que se ejecute automáticamente al arrancar el sistema:

```bash
sudo systemctl enable emisor.service
```

### 6. Verificar el estado del servicio

Puedes verificar el estado del servicio con el siguiente comando:

```bash
sudo systemctl status emisor.service
```

### 7. Ver logs del servicio

En caso de errores o para depurar el servicio, puedes ver los registros usando:

```bash
sudo journalctl -u emisor.service
cat /var/log/emisor.log
cat /var/log/emisor_error.log
```
This will close the connection to the database and exit the PostgreSQL environment.