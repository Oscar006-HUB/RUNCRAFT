#include <WiFi.h>
#include <PubSubClient.h>
#include "DHT.h"
#include <ArduinoJson.h>

// ---------- PIN DEFINITIONS (CORRECTED) ----------
#define DHTPIN 18     // Moved off GPIO 2 to GPIO 18 for stable reading
#define DHTTYPE DHT11
#define LDR_PIN 34    // FIXED: GPIO 34 is ADC1_CH6 (GPIO 21 has no ADC!)
#define TRIG_PIN 4    // HC-SR04 Trigger
#define ECHO_PIN 23   // HC-SR04 Echo

// ---------- WIFI & MQTT ----------
const char* ssid = "Oscar's S23";
const char* password = "u47qp2q8rhtqrb6";
const char* mqtt_server = "10.115.205.163"; 
const char* mqtt_topic  = "esp32/RUNECRAFT/data"; 

WiFiClient espClient;
PubSubClient client(espClient);
DHT dht(DHTPIN, DHTTYPE);

void setup_wifi() {
  delay(100);
  Serial.print("Connecting to WiFi ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
  Serial.print("ESP32 IP Address: ");
  Serial.println(WiFi.localIP());
}

float readDistance() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH, 30000); // 30ms timeout
  if (duration == 0) return -1.0;

  float distance = duration * 0.034 / 2.0; 
  return distance;
}

void reconnectMQTT() {
  while (!client.connected()) {
    String clientId = "RuneCraft-";
    clientId += String(random(0xffff), HEX);
    Serial.print("Attempting MQTT connection...");

    if (client.connect(clientId.c_str())) {
      Serial.println("Connected to MQTT Broker!");
    } else {
      Serial.print("Failed, rc=");
      Serial.print(client.state());
      Serial.println(" Try again in 2 seconds...");
      delay(2000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  dht.begin();

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(LDR_PIN, INPUT); // GPIO 34 is input-only analog pin

  setup_wifi();
  client.setServer(mqtt_server, 1883);
}

void loop() {
  if (!client.connected()) {
    reconnectMQTT();
  }
  client.loop();

  // Read Sensors
  float temp = dht.readTemperature();
  float hum = dht.readHumidity();
  int light = analogRead(LDR_PIN); // Reading 0-4095 from GPIO 34
  float dist = readDistance();

  // JSON Construction
  #if ARDUINOJSON_VERSION_MAJOR >= 7
    JsonDocument doc;
  #else
    StaticJsonDocument<256> doc;
  #endif

  doc["temperature"] = isnan(temp) ? 0.0 : temp;
  doc["humidity"] = isnan(hum) ? 0.0 : hum;
  doc["light"] = light;
  doc["distance"] = dist;

  char jsonBuffer[256];
  serializeJson(doc, jsonBuffer);

  if (client.publish(mqtt_topic, jsonBuffer)) {
    Serial.print("Published JSON: ");
    Serial.println(jsonBuffer);
  } else {
    Serial.println("Publish failed!");
  }

  delay(5000); 
}