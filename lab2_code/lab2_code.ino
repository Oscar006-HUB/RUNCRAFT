#include <WiFi.h>              // Fixed: WiFi (capital W and F)
#include <PubSubClient.h>      // Fixed: PubSubClient (capital P, S, C)
#include "DHT.h"

#define DHTPIN 4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// Add your WiFi and MQTT credentials
//WiFi Credentials
const char* ssid = "Oscar's S23";
const char* password ="u47qp2q8rhtqrb6";

//MQTT Broker IP
const char* mqtt_server = " 10.41.24.36";

WiFiClient espClient;          // Fixed: WiFiClient (capital W and C)
PubSubClient client(espClient);
 
void setup_wifi(){             // Fixed: was declared as set_wifi() below
  delay(100);
  WiFi.begin(ssid, password);  // Fixed: WiFi (capital W)
  while (WiFi.status() != WL_CONNECTED){  // Fixed: WiFi (capital W)
    delay(500);
    Serial.print(".");
  }
  Serial.println("WiFi connected");  // Fixed: println (lowercase L, not I)
}

void setup(){
  Serial.begin(115200);
  dht.begin();
  setup_wifi();                // Fixed: matches function name above
  client.setServer(mqtt_server, 1883);  // Fixed: client (lowercase), single dot
}

void loop(){
  if (!client.connected()){
    while(!client.connected()){
      String clientId = "RUNECRAFT";               // Fixed: String (capital S)
      clientId += String(random(0xffff), HEX);      // Fixed: String, HEX (capital)
      if(client.connect(clientId.c_str())){         // Fixed: connect, not connected
        Serial.println("connected to MQTT");        // Fixed: Serial.println
      } else {
        delay(2000);
      }
    }
  }

  float temp = dht.readTemperature();   // Fixed: added missing closing )
  float hum = dht.readHumidity();
  
  char tempStr[8], humStr[8];
  dtostrf(temp, 1, 2, tempStr);         // Fixed: tempStr (capital S)
  dtostrf(hum, 1, 2, humStr);           // Fixed: humStr (capital S)
  
  client.publish("esp32/RUNECRAFT/temperature", tempStr);
  client.publish("esp32/RUNECRAFT/humidity", humStr);   // Fixed: humStr (capital S)
  
  Serial.println("Published to MQTT");  // Fixed: println
  client.loop();                        // Added: keeps MQTT connection alive
  delay(5000);
}