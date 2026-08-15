import json
from flask import Flask, render_template, request
import paho.mqtt.client as mqtt

app = Flask(__name__)
sensor_data = {}


def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker with code: " + str(rc))
    client.subscribe("esp32/RUNECRAFT/data")  # unique topic


def on_message(client, userdata, msg):
    global sensor_data
    payload = msg.payload.decode()
    print(f"Message received: {payload}")
    try:
        sensor_data = json.loads(payload)
    except json.JSONDecodeError:
        print("Invalid JSON received")


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.loop_start()


@app.route('/')
def index():
    return sensor_data  # can be rendered to display HTML later


if __name__ == "__main__":
    app.run(debug=True, port=5000)