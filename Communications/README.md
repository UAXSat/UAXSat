# 📡 Communications  

UAXSat IV has **LoRa communications**. The data from the satellite is sent to a **ground station (LoRa)**, which is then transmitted to a **server (Postgres SQL)**. The server then sends the data to the **client (Grafana)** for real-time visualization.  

---

## 🌍 LoRa  

LoRa is a **long-range, low-power wireless platform** that has become the **de facto technology** for Internet of Things (IoT) networks worldwide. It is a **modulation technique** that provides significantly **longer range** than competing technologies. LoRa is a proprietary **spread spectrum modulation scheme** derived from **chirp spread spectrum modulation (CSS)**, which trades **data rate for sensitivity** within a fixed channel bandwidth.  

---

## 📊 Grafana  

**Grafana** is an open-source platform for **monitoring and observability**. It allows you to:  

✔️ **Query, visualize, and alert on data**  
✔️ **Create and share interactive dashboards**  
✔️ **Connect to various data sources (PostgreSQL, MQTT, etc.)**  

---

# ⚙️ Instructions for Using the Code  

## 🛠️ Connecting PostgreSQL Database to Grafana for Data Visualization  

This guide explains how to:  

1. **Install and Set Up Grafana**  
2. **Connect PostgreSQL as a Data Source**  
3. **Create Dashboards and Visualizations**  
4. **Import a Pre-Designed JSON Dashboard** (NEW ✅)  

---

## 1️⃣ Install and Set Up Grafana  

### 📥 Installing Grafana  

For **Linux users**, run:  

```bash
# Add Grafana repository and install
sudo apt-get install -y software-properties-common  
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"  
sudo apt-get update  
sudo apt-get install grafana  

# Enable and start Grafana service
sudo systemctl enable grafana-server  
sudo systemctl start grafana-server  

```

### 🌐 Accessing Grafana
Once Grafana is installed and the server is running, open your browser and go to:

```internet
http://localhost:3000
```
The default login credentials are:
- Username: admin
- Password: admin (you will be prompted to change this after your first login)

---

## 2️⃣ Configuring PostgreSQL as a Data Source

Now that Grafana is running, follow these steps to connect your PostgreSQL database as a data source:

### Step 1: Access Data Sources

1. In the Grafana dashboard, click on the gear icon ⚙️ on the left panel to open the Configuration menu.

2. Select Data Sources.

### Step 2: Add PostgreSQL Data Source

1. Click the Add data source button.

2. Scroll down or search for PostgreSQL and select it.

3. Fill in the following details:

- Host: localhost:5432 (or your PostgreSQL server address)
- Database: cubesat_db (the database you created)
- User: cubesat (the user you created)
- Password: The password for the cubesat user
- SSL Mode: Choose disable if SSL is not configured.

Optionally, you can customize the Max Open Connections and Connection Max Lifetime settings based on your needs.

4. Click Save & Test to verify the connection. If everything is configured correctly, you should see a message indicating that the database connection was successful.

---

## 3️⃣ Creating Dashboards and Visualizations

### Step 1: Create a New Dashboard

1. In Grafana, click the “+” icon on the left panel and select Create Dashboard.
2. Click Add New Panel to begin building your visualizations.

### Step 2: Query Data from PostgreSQL
1. In the new panel, choose PostgreSQL as the data source.
2. Use SQL queries to pull data from the sensor_readings table. For example, to display the latest accelerometer data:
```sql
SELECT
  timestamp AS "time",
  acelx,
  acely,
  acelz
FROM
  sensor_readings
ORDER BY
  timestamp DESC
LIMIT 100
```

3. Grafana will automatically create a time series visualization based on your data.

### Step 3: Customize the Visualization
1. On the right-hand side, choose the visualization type (e.g., Graph, Gauge, Table).
2. Customize the appearance, labels, and units as needed.
3. Click Apply to save the panel to the dashboard.

## 4️⃣ Importing a Pre-Designed JSON Dashboard
Follow these steps to upload it into Grafana instead of creating panels manually.

### Step 1: Open Import Section
1. In Grafana, click the + (Create) button in the left menu.
2. Select Import.
### Step 2: Upload the JSON File
1. Click Upload JSON file and select your .json dashboard file.
2. Alternatively, paste our JSON code (UAXSAT GRAFANA VISUALIZATION.json) into the provided text box.
### Step 3: Configure Data Source
1. Under "Select a data source", choose your PostgreSQL database (e.g., cubesat).
2. Click Import.
