import csv
import io
import json
from collections import deque
from datetime import datetime

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from flask import Flask, Response
import paho.mqtt.client as mqtt
import plotly.graph_objs as go

# ============================================================================
# CONFIGURATION & PARAMETERS (MATCHING YOUR ESP32 SKETCH)
# ============================================================================
MQTT_BROKER = "10.115.205.163"       # ESP32 Broker IP
MQTT_PORT = 1883
MQTT_TOPIC = "esp32/RUNECRAFT/data"  # ESP32 Telemetry Topic

MAX_HISTORY = 30
temp_data = deque(maxlen=MAX_HISTORY)
humidity_data = deque(maxlen=MAX_HISTORY)
light_data = deque(maxlen=MAX_HISTORY)
distance_data = deque(maxlen=MAX_HISTORY)
time_data = deque(maxlen=MAX_HISTORY)

# ============================================================================
# FLASK & DASH SERVER INITIALIZATION
# ============================================================================
server = Flask(__name__)
app = dash.Dash(__name__, server=server)
app.title = "Lab 6 - RuneCraft Workstation"

@server.route('/export/csv')
def export_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Timestamp', 'Temperature_C', 'Humidity_Percent', 'Light_Raw', 'Distance_cm'])
    
    for t, temp, hum, light, dist in zip(time_data, temp_data, humidity_data, light_data, distance_data):
        writer.writerow([t, temp, hum, light, dist])
        
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=runecraft_snap_report.csv"}
    )

# ============================================================================
# MQTT LISTENER ROUTINES (Paho MQTT v2.x Compatible)
# ============================================================================
def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        print(f"[MQTT] Connected successfully to broker at {MQTT_BROKER}")
        client.subscribe(MQTT_TOPIC)
        print(f"[MQTT] Subscribed to topic: {MQTT_TOPIC}")
    else:
        print(f"[MQTT] Failed to connect, reason code: {reason_code}")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode('utf-8'))
        
        temp_data.append(payload.get('temperature', 0.0))
        humidity_data.append(payload.get('humidity', 0.0))
        light_data.append(payload.get('light', 0))
        distance_data.append(payload.get('distance', 0.0))
        time_data.append(datetime.now().strftime('%H:%M:%S'))
        
        print(f"[MQTT] Ingested: {payload}")
    except Exception as err:
        print(f"[MQTT Error] Ingestion failed: {err}")

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

try:
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()
except Exception as e:
    print(f"[MQTT Error] Broker connection failed: {e}")

# ============================================================================
# DASH UI LAYOUT
# ============================================================================
app.layout = html.Div(
    style={'padding': '24px', 'fontFamily': 'Segoe UI, Arial, sans-serif', 'backgroundColor': '#f8fafc', 'minHeight': '100vh'},
    children=[
        html.Div(
            style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'marginBottom': '20px'},
            children=[
                html.Div([
                    html.H1("RuneCraft Real-Time  Dashboard", style={'margin': '0', 'color': '#0f172a'}),
                    html.P("ESP32 Integrated Multi-Sensor MQTT Monitoring Station", style={'margin': '4px 0 0 0', 'color': '#64748b'})
                ]),
                html.A(
                    "Export CSV Report",
                    href="/export/csv",
                    target="_blank",
                    style={
                        'padding': '10px 18px',
                        'backgroundColor': '#2563eb',
                        'color': 'white',
                        'textDecoration': 'none',
                        'borderRadius': '6px',
                        'fontWeight': 'bold'
                    }
                )
            ]
        ),

        dcc.Interval(id='interval-component', interval=2000, n_intervals=0),

        # KPI Summary Grid
        html.Div(id='kpi-deck', style={'display': 'grid', 'gridTemplateColumns': 'repeat(4, 1fr)', 'gap': '16px', 'marginBottom': '20px'}),

        # Real-time Graph Plots
        html.Div(
            style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '20px'},
            children=[
                html.Div(dcc.Graph(id='temp-graph'), style={'backgroundColor': 'white', 'padding': '12px', 'borderRadius': '8px', 'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'}),
                html.Div(dcc.Graph(id='humidity-graph'), style={'backgroundColor': 'white', 'padding': '12px', 'borderRadius': '8px', 'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'}),
                html.Div(dcc.Graph(id='light-graph'), style={'backgroundColor': 'white', 'padding': '12px', 'borderRadius': '8px', 'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'}),
                html.Div(dcc.Graph(id='distance-graph'), style={'backgroundColor': 'white', 'padding': '12px', 'borderRadius': '8px', 'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'}),
            ]
        )
    ]
)

# ============================================================================
# REAL-TIME UPDATE CALLBACK
# ============================================================================
@app.callback(
    [
        Output('temp-graph', 'figure'),
        Output('humidity-graph', 'figure'),
        Output('light-graph', 'figure'),
        Output('distance-graph', 'figure'),
        Output('kpi-deck', 'children')
    ],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    timestamps = list(time_data)

    fig1 = go.Figure(data=[go.Scatter(x=timestamps, y=list(temp_data), mode='lines+markers', line={'color': '#ef4444', 'width': 2})])
    fig1.update_layout(title='Temperature (°C)', xaxis_title='Time', yaxis_title='Temp (°C)', plot_bgcolor='white')

    fig2 = go.Figure(data=[go.Scatter(x=timestamps, y=list(humidity_data), mode='lines+markers', line={'color': '#0284c7', 'width': 2})])
    fig2.update_layout(title='Humidity (%)', xaxis_title='Time', yaxis_title='Humidity (%)', plot_bgcolor='white')

    fig3 = go.Figure(data=[go.Scatter(x=timestamps, y=list(light_data), mode='lines+markers', line={'color': '#f59e0b', 'width': 2})])
    fig3.update_layout(title='LDR Light Level (Raw ADC)', xaxis_title='Time', yaxis_title='ADC Value (0-4095)', plot_bgcolor='white')

    fig4 = go.Figure(data=[go.Scatter(x=timestamps, y=list(distance_data), mode='lines+markers', line={'color': '#10b981', 'width': 2})])
    fig4.update_layout(title='Ultrasonic Distance (cm)', xaxis_title='Time', yaxis_title='Distance (cm)', plot_bgcolor='white')

    # KPI Card Displays
    cur_t = f"{temp_data[-1]:.1f} °C" if temp_data else "--"
    cur_h = f"{humidity_data[-1]:.1f} %" if humidity_data else "--"
    cur_l = f"{light_data[-1]}" if light_data else "--"
    cur_d = f"{distance_data[-1]:.1f} cm" if distance_data else "--"

    kpis = [
        html.Div([html.P("Temperature", style={'margin': '0', 'fontSize': '12px', 'color': '#64748b'}), html.H3(cur_t, style={'margin': '4px 0 0 0'})], style={'backgroundColor': 'white', 'padding': '16px', 'borderRadius': '8px', 'borderLeft': '4px solid #ef4444'}),
        html.Div([html.P("Humidity", style={'margin': '0', 'fontSize': '12px', 'color': '#64748b'}), html.H3(cur_h, style={'margin': '4px 0 0 0'})], style={'backgroundColor': 'white', 'padding': '16px', 'borderRadius': '8px', 'borderLeft': '4px solid #0284c7'}),
        html.Div([html.P("Light Level (ADC)", style={'margin': '0', 'fontSize': '12px', 'color': '#64748b'}), html.H3(cur_l, style={'margin': '4px 0 0 0'})], style={'backgroundColor': 'white', 'padding': '16px', 'borderRadius': '8px', 'borderLeft': '4px solid #f59e0b'}),
        html.Div([html.P("Proximity Distance", style={'margin': '0', 'fontSize': '12px', 'color': '#64748b'}), html.H3(cur_d, style={'margin': '4px 0 0 0'})], style={'backgroundColor': 'white', 'padding': '16px', 'borderRadius': '8px', 'borderLeft': '4px solid #10b981'}),
    ]

    return fig1, fig2, fig3, fig4, kpis


if __name__ == '__main__':
    app.run(debug=True)