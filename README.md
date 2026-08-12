 EE 288: Electrical Measurement and Instrumentation — Team RUNECRAFT (Group 14)

Welcome to the official GitHub repository for **Team RUNECRAFT (Group 14)** for **EE 288: Electrical Measurement and Instrumentation** at Kwame Nkrumah University of Science and Technology (KNUST).

This repository hosts all firmware sketches, Python scripts, Flask web applications, Plotly dashboards, and laboratory documentation developed throughout the course.

---

## 📌 Team & Course Details
* **Group Name:** RUNECRAFT (Group 14)
* **Team Author / Maintainer:** Prince Oscar Mwinnuo
* **Institution:** Kwame Nkrumah University of Science and Technology (KNUST)
* **Course Code:** EE 288 — Electrical Measurement and Instrumentation
* **Lecturer:** Dr. Griffith Serlom Klogo
* **Lab Instructors:** Evans Korletey, Nero Etornam Novor
* **Repository Note:** Hosted and maintained on an individual GitHub account on behalf of Team RUNECRAFT.

---

## 🚀 System Architecture & Overview

This project implements an end-to-end Internet of Things (IoT) measurement pipeline designed to acquire environmental data, transmit it via lightweight messaging protocols, and visualize readings in real time.

┌─────────────────┐      MQTT (1883)       ┌───────────────────┐      HTTP / JSON      ┌─────────────────────┐│  ESP32 Sensors  │ ────────────────────> │    MQTT Broker    │ ────────────────────> │ Flask + Dash Server ││ (DHT11, LDR, HC)│   JSON / String       │ (Mosquitto/HiveMQ)│    Paho-MQTT Sub      │ (Plotly Dashboards) │└─────────────────┘                        └───────────────────┘                       └─────────────────────┘
### Hardware & Software Ecosystem
* **Microcontroller:** ESP32 Development Board
* **Sensors Integrated:**
  * **DHT11:** Digital Temperature & Humidity Sensor (GPIO 4)
  * **LDR:** Light Dependent Resistor in Voltage Divider mode (GPIO 34)
  * **HC-SR04:** Ultrasonic Distance Sensor (Trig: GPIO 5, Echo: GPIO 18)
* **Protocols & Broker:** MQTT via local Eclipse Mosquitto 
* **Back-End Framework:** Python 3, Flask, Paho-MQTT, `ArduinoJson`
* **Front-End & Visualization:** Plotly & Dash real-time updating web dashboards

---
System Architecture & Software PrerequisitesTo run the IoT telemetry pipeline for EE 288 (Electrical Measurement and Instrumentation), your development environment requires tools spanning three main layers: Microcontroller Firmware (C++), Message Broker Infrastructure (MQTT), and Back-End Analytics/Visualization (Python).  ┌─────────────────────────┐     ┌─────────────────────────┐     ┌─────────────────────────┐
│     Firmware Layer      │     │     Broker Layer        │     │  Back-End & UI Layer    │
│  Arduino IDE 2.x        │ ──> │  Eclipse Mosquitto      │ ──> │  Python 3.8+            │
│  ESP32 Board Support    │     │  Port 1883 (TCP)        │     │  Flask / Plotly Dash    │
└─────────────────────────┘     └─────────────────────────┘     └─────────────────────────┘
1. Hardware Drivers & ESP32 Core SetupStep 1.1: Install USB-to-UART Bridge DriversMost ESP32 development boards use either the CP210x or CH340 serial converter chip. Without these drivers, Windows/macOS cannot create a virtual COM port.Download and install the driver corresponding to your board's USB interface chip:Silicon Labs CP210x Driver: Download CP210x VCP Drivers.WCH CH340 Driver: Download CH341SER Driver.Plug in your ESP32 board and verify the port connection:Windows: Open Device Manager $\rightarrow$ expand Ports (COM & LPT) $\rightarrow$ confirm device appears (e.g., Silicon Labs CP210x (COM3)).macOS/Linux: Open terminal and run ls /dev/tty.* (look for /dev/tty.usbserial-* or /dev/ttyUSB0).Step 1.2: Configure ESP32 Core in Arduino IDE 2.xDownload and install Arduino IDE 2.x.Open Arduino IDE $\rightarrow$ go to File $\rightarrow$ Preferences.Paste the following URL into the Additional Boards Manager URLs field:Plaintexthttps://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
Open the Boards Manager (left sidebar icon or Ctrl + Shift + B).Search for esp32 and click Install on esp32 by Espressif Systems.Select your target board: Tools $\rightarrow$ Board $\rightarrow$ esp32 $\rightarrow$ ESP32 Dev Module.
2. Arduino C++ Libraries InstallationThe firmware requires three core libraries to acquire sensor data, serialize readings to JSON, and handle MQTT publishing.  Required C++ LibrariesPubSubClient (by Nick O'Leary): Enables MQTT communication over TCP/IP.DHT sensor library (by Adafruit): Interfaces with DHT11 / DHT22 temperature and humidity sensors.Adafruit Unified Sensor (by Adafruit): Dependency required by Adafruit DHT library.ArduinoJson (by Benoit Blanchon): Formats telemetry values into structured JSON payloads.  Installation Steps (Via Arduino IDE Library Manager)In Arduino IDE, click the Library Manager icon on the left navigation panel (or press Ctrl + Shift + I).Search and install each library sequentially:Search PubSubClient $\rightarrow$ Install PubSubClient by Nick O'Leary.Search DHT sensor library $\rightarrow$ Install DHT sensor library by Adafruit (Click Install All if prompted to install Adafruit Unified Sensor).Search ArduinoJson $\rightarrow$ Install ArduinoJson by Benoit Blanchon (Select version 6.x or 7.x).
3. MQTT Broker Setup (Eclipse Mosquitto)The system requires a local broker running on Port 1883 to receive messages from the ESP32 and forward them to Python.  Windows InstallationDownload the executable installer from mosquitto.org/download.Run the installer and keep default installation paths (typically C:\Program Files\Mosquitto).Open C:\Program Files\Mosquitto\mosquitto.conf in a text editor as Administrator, and append the following lines to allow local network connections:  Ini, TOMLlistener 1883
allow_anonymous true
Open PowerShell or Command Prompt as Administrator and start Mosquitto:  PowerShellcd "C:\Program Files\Mosquitto"
.\mosquitto -c mosquitto.conf -v
```

macOS / Linux InstallationBash# macOS via Homebrew
brew install mosquitto
brew services start mosquitto

# Ubuntu/Debian Linux
sudo apt update
sudo apt install -y mosquitto mosquitto-clients
sudo systemctl enable mosquitto --now
4. Python Back-End & Dashboard SetupThe Python application subcribes to MQTT sensor streams and serves real-time graphs via Flask and Plotly Dash.  Step 4.1: Python Environment SetupEnsure Python 3.8 or newer is installed. Verify by running:  Bashpython --version
pip --version
(Optional but recommended) Create and activate a isolated virtual environment:Bash# Create environment
python -m venv venv

# Activate on Windows:
.\venv\Scripts\activate

# Activate on macOS/Linux:
source venv/bin/activate
Step 4.2: Install Required PackagesRun the following pip command to install all mandatory dependencies:  Bashpip install flask paho-mqtt dash plotly pandas
```[cite: 2]

#### Package Function Breakdown
| Package | Role in Architecture |
| :--- | :--- |
| `paho-mqtt` | Handles background MQTT subscriptions and message callback parsing[cite: 2]. |
| `flask` | Provides HTTP REST endpoint structure and routing[cite: 2]. |
| `dash` | React-based web dashboard framework built on Flask for live UI updates[cite: 1]. |
| `plotly` | Renders dynamic time-series line charts for temperature, humidity, and distance[cite: 1]. |
| `pandas` | Formats and structures incoming sensor stream payloads in memory. |

---

### 5. Installation Verification Checklist

To confirm that all components are configured properly before running lab experiments:

1. **Check Hardware Connection:** Open Arduino Serial Monitor (`115200` baud rate) while ESP32 is running to confirm sensor initialized logs.
2. **Check Broker Port:** Verify Mosquitto is active on port `1883` by running:
   * Windows: `netstat -ano | findstr 1883`
   * Linux/macOS: `sudo lsof -i :1883`
3. **Test MQTT Subscriptions:** Test payload transmission using Mosquitto CLI:
   ```bash
   # Terminal 1: Subscribe to test channel
   mosquitto_sub -h localhost -t "runecraft/test"

   # Terminal 2: Publish dummy message
   mosquitto_pub -h localhost -t "runecraft/test" -m "Hello EE288"
   ```[cite: 2]
## 📁 Repository Structure

```text
.
├── Lab_01_ADC_Sensor_Interfacing/   # ESP32 configuration, LDR ADC readings, HC-SR04 timing
├── Lab_02_Digital_Measurement/      # ADC resolution, signal processing, DHT11 integration
├── Lab_03_MQTT_Publishing/          # Mosquitto setup, PubSubClient, string & JSON payloads
├── Lab_04_Flask_Server/             # Python Flask backend & HTTP API endpoints
├── Lab_05_Plotly_Dashboard/         # Live multi-graph streaming dashboard with Plotly/Dash
├── Lab_06_Final_Integration/        # Full end-to-end system integration firmware & backend
└── Reports/                         # Lab reports and academic deliverables (PDFs)
🛠️ Summary of Executed Lab Modules1. Lab 1 & 2: Sensor Interfacing & Signal ConditioningConfigured ESP32 12-bit ADC channels for analog light intensity measurements.  Applied time-of-flight sound propagation calculations to measure distance using the HC-SR04[cite: 1].Integrated DHT11 digital temperature and humidity sensing[cite: 1].2. Lab 3: MQTT Data Transmission PipelineConfigured local Eclipse Mosquitto broker listening on port 1883 (0.0.0.0).  Established communication using topics formatted under runecraft/# and esp32/sensors/#.  Formatted data transmissions into lightweight structured JSON payloads[cite: 1, 2].3. Lab 4: Flask Web Server IntegrationBuilt a local Python Flask server utilizing paho-mqtt to subscribe to telemetry topics[cite: 1, 2].Exposed live JSON payloads directly to local web endpoints (http://127.0.0.1:5000/)[cite: 1, 2].4. Lab 5 & 6: Real-Time Visualization & System IntegrationDesigned multi-sensor Plotly/Dash web interfaces updating dynamically via live callbacks[cite: 1].Integrated full end-to-end hardware-to-cloud data streaming pipeline[cite: 1].⚡ Setup and Execution GuidePrerequisitesArduino IDE 2.x with ESP32 board support and libraries (PubSubClient, DHT sensor library, ArduinoJson)[cite: 1, 2].Python 3.8+ runtime environment[cite: 1, 2].Eclipse Mosquitto or an active internet connection for HiveMQ[cite: 1, 2].Installing Python DependenciesBashpip install flask paho-mqtt dash plotly
Running the SystemStart Mosquitto Broker (Local Setup):PowerShellcd "C:\Program Files\Mosquitto"
.\mosquitto -c mosquitto.conf -v
```[cite: 2]
Flash ESP32 Firmware: Open Lab_06_Final_Integration/Lab_06_Final_Integration.ino in Arduino IDE, select your COM port and upload[cite: 1].Start Back-End Server & Dashboard:Bashpython Lab_06_Final_Integration/realtime_dashboard.py
Access Web View: Open browser at http://127.0.0.1:8050 or http://127.0.0.1:5000[cite: 1, 2].📜 Academic Integrity & LicenseThis repository is authored by Prince Oscar Mwinnuo for Team RUNECRAFT (Group 14) as part of the academic requirements for EE 288 at KNUST (2024–2026 academic sessions)[cite: 1, 2]. All original code and documentation remain under team authorship
