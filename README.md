 EE 288: Electrical Measurement and Instrumentation — Team RUNECRAFT (Group 14)

Welcome to the official GitHub repository for **Team RUNECRAFT (Group 14)** for **EE 288: Electrical Measurement and Instrumentation** at Kwame Nkrumah University of Science and Technology (KNUST).

This repository hosts all firmware sketches, Python scripts, Flask web applications, Plotly dashboards, and laboratory documentation developed throughout the course.

---

## 📌 Team & Course Details
* **Group Name:** RUNECRAFT (Group 14)[cite: 2]
* **Team Author / Maintainer:** Prince Oscar Mwinnuo[cite: 2]
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
* **Protocols & Broker:** MQTT via local Eclipse Mosquitto or Public Broker (`broker.hivemq.com`)
* **Back-End Framework:** Python 3, Flask, Paho-MQTT, `ArduinoJson`
* **Front-End & Visualization:** Plotly & Dash real-time updating web dashboards

---

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
