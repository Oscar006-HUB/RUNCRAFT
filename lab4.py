import json
import csv
import io
import threading
from datetime import datetime
from flask import Flask, render_template_string, Response
import paho.mqtt.client as mqtt

app = Flask(__name__)

# Thread-safe data stores
data_lock = threading.Lock()
sensor_data = {}
data_history = []
MAX_HISTORY = 500  # Keep last 200 readings for graph history


def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker with code: " + str(rc))
    client.subscribe("esp32/RUNECRAFT/data")


def on_message(client, userdata, msg):
    global sensor_data, data_history
    payload = msg.payload.decode()
    print(f"Message received: {payload}")
    try:
        data = json.loads(payload)
        # Inject timestamp if ESP32 doesn't send one
        if "timestamp" not in data:
            data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with data_lock:
            sensor_data = data
            data_history.append(data)
            if len(data_history) > MAX_HISTORY:
                data_history.pop(0)
    except json.JSONDecodeError:
        print("Invalid JSON received")


# MQTT Client setup (paho-mqtt v1.x style)
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.loop_start()


# ============================================================================
# EMBEDDED PROFESSIONAL DASHBOARD HTML
# ============================================================================
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RUNECRAFT | Instrumentation And Measurements Lab</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
    <style>
        :root {
            --bg-body: #090d16;
            --bg-surface: #111827;
            --bg-card: rgba(17, 24, 39, 0.7);
            --border-card: rgba(255, 255, 255, 0.08);
            --border-hover: rgba(99, 102, 241, 0.4);
            
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --text-muted: #475569;
            
            --accent-temp: #f43f5e;
            --accent-temp-glow: rgba(244, 63, 94, 0.15);
            --accent-hum: #06b6d4;
            --accent-hum-glow: rgba(6, 182, 212, 0.15);
            --accent-light: #f59e0b;
            --accent-light-glow: rgba(245, 158, 11, 0.15);
            --accent-dist: #10b981;
            --accent-dist-glow: rgba(16, 185, 129, 0.15);
            
            --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: var(--font-sans);
            background-color: var(--bg-body);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 32px 20px 48px;
            background-image: 
                radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.08) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(16, 185, 129, 0.05) 0px, transparent 50%);
            background-attachment: fixed;
            -webkit-font-smoothing: antialiased;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        /* Top Header */
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 28px;
            margin-bottom: 28px;
            border-bottom: 1px solid var(--border-card);
            flex-wrap: wrap;
            gap: 20px;
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 16px;
        }

        .brand-logo {
            width: 46px;
            height: 46px;
            background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 1.4rem;
            color: #ffffff;
            box-shadow: 0 0 20px rgba(99, 102, 241, 0.4);
            letter-spacing: -1px;
        }

        .brand-info h1 {
            font-size: 1.6rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            background: linear-gradient(180deg, #ffffff 0%, #cbd5e1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .brand-info p {
            font-size: 0.85rem;
            color: var(--text-secondary);
            font-weight: 500;
        }

        .header-actions {
            display: flex;
            align-items: center;
            gap: 16px;
        }

        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--border-card);
            padding: 8px 18px;
            border-radius: 99px;
            font-size: 0.825rem;
            font-weight: 600;
            color: var(--text-secondary);
            backdrop-filter: blur(12px);
        }

        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: #64748b;
            transition: all 0.3s ease;
        }

        .status-dot.active {
            background-color: #10b981;
            box-shadow: 0 0 10px #10b981;
            animation: pulse-ring 2s infinite;
        }

        .status-dot.error {
            background-color: #ef4444;
            box-shadow: 0 0 10px #ef4444;
        }

        @keyframes pulse-ring {
            0% { transform: scale(0.95); opacity: 1; }
            50% { transform: scale(1.2); opacity: 0.7; }
            100% { transform: scale(0.95); opacity: 1; }
        }

        .btn-download {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 10px 20px;
            background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%);
            color: #ffffff;
            border: none;
            border-radius: 10px;
            font-size: 0.875rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.25s ease;
            box-shadow: 0 4px 14px rgba(79, 70, 229, 0.35);
            text-decoration: none;
        }

        .btn-download:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(79, 70, 229, 0.5);
            background: linear-gradient(135deg, #6366f1 0%, #60a5fa 100%);
        }

        /* Overview Summary Bar */
        .summary-bar {
            display: flex;
            gap: 24px;
            margin-bottom: 28px;
            background: var(--bg-card);
            border: 1px solid var(--border-card);
            border-radius: 12px;
            padding: 14px 24px;
            backdrop-filter: blur(12px);
            align-items: center;
            justify-content: space-between;
            font-size: 0.85rem;
            color: var(--text-secondary);
        }

        .summary-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .summary-item strong {
            color: var(--text-primary);
            font-family: var(--font-mono);
        }

        /* KPI Metric Cards */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 20px;
            margin-bottom: 28px;
        }

        .metric-card {
            background: var(--bg-card);
            border: 1px solid var(--border-card);
            border-radius: 16px;
            padding: 22px;
            backdrop-filter: blur(12px);
            position: relative;
            overflow: hidden;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .metric-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 2px;
            background: transparent;
            transition: background 0.3s ease;
        }

        .metric-card.temp::before { background: var(--accent-temp); }
        .metric-card.hum::before { background: var(--accent-hum); }
        .metric-card.light::before { background: var(--accent-light); }
        .metric-card.dist::before { background: var(--accent-dist); }

        .metric-card:hover {
            border-color: var(--border-hover);
            transform: translateY(-3px);
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4);
        }

        .metric-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }

        .metric-title {
            font-size: 0.8rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--text-secondary);
        }

        .metric-icon {
            width: 40px;
            height: 40px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .metric-card.temp .metric-icon { background: var(--accent-temp-glow); color: var(--accent-temp); }
        .metric-card.hum .metric-icon { background: var(--accent-hum-glow); color: var(--accent-hum); }
        .metric-card.light .metric-icon { background: var(--accent-light-glow); color: var(--accent-light); }
        .metric-card.dist .metric-icon { background: var(--accent-dist-glow); color: var(--accent-dist); }

        .metric-body {
            display: flex;
            align-items: baseline;
            gap: 10px;
            margin-bottom: 14px;
        }

        .metric-value {
            font-family: var(--font-mono);
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--text-primary);
            letter-spacing: -0.03em;
            line-height: 1;
        }

        .metric-unit {
            font-size: 0.95rem;
            color: var(--text-muted);
            font-weight: 600;
        }

        .metric-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 12px;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            font-size: 0.75rem;
            color: var(--text-muted);
            font-family: var(--font-mono);
        }

        /* Telemetry Charts */
        .charts-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
        }

        .chart-card {
            background: var(--bg-card);
            border: 1px solid var(--border-card);
            border-radius: 16px;
            padding: 24px;
            backdrop-filter: blur(12px);
            display: flex;
            flex-direction: column;
            transition: border-color 0.3s ease;
        }

        .chart-card:hover {
            border-color: rgba(255, 255, 255, 0.15);
        }

        .chart-card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }

        .chart-card-title {
            font-size: 0.95rem;
            font-weight: 700;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .chart-card-title::before {
            content: '';
            width: 8px;
            height: 8px;
            border-radius: 50%;
        }

        .chart-card.temp .chart-card-title::before { background: var(--accent-temp); box-shadow: 0 0 8px var(--accent-temp); }
        .chart-card.hum .chart-card-title::before { background: var(--accent-hum); box-shadow: 0 0 8px var(--accent-hum); }
        .chart-card.light .chart-card-title::before { background: var(--accent-light); box-shadow: 0 0 8px var(--accent-light); }
        .chart-card.dist .chart-card-title::before { background: var(--accent-dist); box-shadow: 0 0 8px var(--accent-dist); }

        .chart-container {
            position: relative;
            height: 270px;
            width: 100%;
        }

        @media (max-width: 1024px) {
            .charts-grid { grid-template-columns: 1fr; }
            .summary-bar { flex-direction: column; align-items: flex-start; gap: 8px; }
        }

        @media (max-width: 640px) {
            header { flex-direction: column; align-items: flex-start; }
            .header-actions { width: 100%; justify-content: space-between; }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header Section -->
        <header>
            <div class="brand">
                <div class="brand-logo">R</div>
                <div class="brand-info">
                    <h1>RUNECRAFT </h1>
                    <p>Instrumentation And Measurements Lab </p>
                </div>
            </div>
            
            <div class="header-actions">
                <div class="status-badge">
                    <span class="status-dot" id="status-dot"></span>
                    <span id="status-text">Establishing Stream...</span>
                </div>
                <button class="btn-download" onclick="downloadCSV()">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y3="3"/></svg>
                    Export CSV
                </button>
            </div>
        </header>

        <!-- Dynamic Overview Summary Bar -->
        <div class="summary-bar">
            <div class="summary-item">
                <span>Broker Status:</span> <strong style="color: #10b981;">CONNECTED</strong>
            </div>
            <div class="summary-item">
                <span>Total Samples:</span> <strong id="total-samples">0</strong>
            </div>
            <div class="summary-item">
                <span>System Clock:</span> <strong id="clock-display">--:--:--</strong>
            </div>
            <div class="summary-item">
                <span>Telemetry Refresh Rate:</span> <strong>2.0s</strong>
            </div>
        </div>

        <!-- KPI Metric Cards -->
        <div class="metrics-grid">
            <!-- Temperature Card -->
            <div class="metric-card temp">
                <div class="metric-header">
                    <span class="metric-title">Temperature</span>
                    <div class="metric-icon">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 4v10.54a4 4 0 1 1-4 0V4a2 2 0 0 1 4 0Z"/></svg>
                    </div>
                </div>
                <div class="metric-body">
                    <span class="metric-value" id="val-temp">--</span>
                    <span class="metric-unit">°C</span>
                </div>
                <div class="metric-footer">
                    <span>MIN: <strong id="min-temp" style="color: #f8fafc;">--</strong></span>
                    <span>MAX: <strong id="max-temp" style="color: #f8fafc;">--</strong></span>
                </div>
            </div>

            <!-- Humidity Card -->
            <div class="metric-card hum">
                <div class="metric-header">
                    <span class="metric-title">Humidity</span>
                    <div class="metric-icon">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22a7 7 0 0 0 7-7c0-2-1-3.9-3-5.5s-3.5-4-4-6.5c-.5 2.5-2 4.9-4 6.5C6 11.1 5 13 5 15a7 7 0 0 0 7 7z"/></svg>
                    </div>
                </div>
                <div class="metric-body">
                    <span class="metric-value" id="val-hum">--</span>
                    <span class="metric-unit">% RH</span>
                </div>
                <div class="metric-footer">
                    <span>MIN: <strong id="min-hum" style="color: #f8fafc;">--</strong></span>
                    <span>MAX: <strong id="max-hum" style="color: #f8fafc;">--</strong></span>
                </div>
            </div>

            <!-- Light Card -->
            <div class="metric-card light">
                <div class="metric-header">
                    <span class="metric-title">Light Intensity</span>
                    <div class="metric-icon">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>
                    </div>
                </div>
                <div class="metric-body">
                    <span class="metric-value" id="val-light">--</span>
                    <span class="metric-unit">Lux</span>
                </div>
                <div class="metric-footer">
                    <span>MIN: <strong id="min-light" style="color: #f8fafc;">--</strong></span>
                    <span>MAX: <strong id="max-light" style="color: #f8fafc;">--</strong></span>
                </div>
            </div>

            <!-- Distance Card -->
            <div class="metric-card dist">
                <div class="metric-header">
                    <span class="metric-title">Proximity Distance</span>
                    <div class="metric-icon">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 12h20"/><path d="M6 8v8"/><path d="M12 9v6"/><path d="M18 8v8"/></svg>
                    </div>
                </div>
                <div class="metric-body">
                    <span class="metric-value" id="val-dist">--</span>
                    <span class="metric-unit">cm</span>
                </div>
                <div class="metric-footer">
                    <span>MIN: <strong id="min-dist" style="color: #f8fafc;">--</strong></span>
                    <span>MAX: <strong id="max-dist" style="color: #f8fafc;">--</strong></span>
                </div>
            </div>
        </div>

        <!-- Telemetry Horizon Charts -->
        <div class="charts-grid">
            <div class="chart-card temp">
                <div class="chart-card-header">
                    <div class="chart-card-title">Temperature Horizon (°C)</div>
                </div>
                <div class="chart-container">
                    <canvas id="chart-temp"></canvas>
                </div>
            </div>

            <div class="chart-card hum">
                <div class="chart-card-header">
                    <div class="chart-card-title">Relative Humidity Horizon (%)</div>
                </div>
                <div class="chart-container">
                    <canvas id="chart-hum"></canvas>
                </div>
            </div>

            <div class="chart-card light">
                <div class="chart-card-header">
                    <div class="chart-card-title">Ambient Illuminance (Lux)</div>
                </div>
                <div class="chart-container">
                    <canvas id="chart-light"></canvas>
                </div>
            </div>

            <div class="chart-card dist">
                <div class="chart-card-header">
                    <div class="chart-card-title">Proximity / Distance Horizon (cm)</div>
                </div>
                <div class="chart-container">
                    <canvas id="chart-dist"></canvas>
                </div>
            </div>
        </div>
    </div>

    <script>
        const charts = {};

        // Clock display handler
        setInterval(() => {
            const now = new Date();
            document.getElementById('clock-display').textContent = now.toLocaleTimeString();
        }, 1000);

        function initChart(canvasId, label, color) {
            const ctx = document.getElementById(canvasId).getContext('2d');
            
            const gradient = ctx.createLinearGradient(0, 0, 0, 260);
            gradient.addColorStop(0, color + '40');
            gradient.addColorStop(1, color + '00');

            return new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: label,
                        data: [],
                        borderColor: color,
                        borderWidth: 2.5,
                        backgroundColor: gradient,
                        fill: true,
                        tension: 0.3,
                        pointRadius: 0,
                        pointHoverRadius: 6,
                        pointHoverBackgroundColor: color,
                        pointHoverBorderColor: '#ffffff',
                        pointHoverBorderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                            backgroundColor: '#1e293b',
                            titleColor: '#94a3b8',
                            bodyColor: '#f8fafc',
                            borderColor: 'rgba(255,255,255,0.1)',
                            borderWidth: 1,
                            padding: 12,
                            displayColors: false,
                            bodyFont: { family: 'JetBrains Mono', weight: 'bold', size: 13 }
                        }
                    },
                    scales: {
                        y: {
                            grid: { color: 'rgba(255, 255, 255, 0.04)', drawBorder: false },
                            ticks: { color: '#64748b', font: { family: 'Plus Jakarta Sans', size: 11 } }
                        },
                        x: {
                            grid: { display: false },
                            ticks: { color: '#64748b', maxTicksLimit: 7, font: { family: 'Plus Jakarta Sans', size: 11 } }
                        }
                    },
                    interaction: { mode: 'index', intersect: false },
                    animation: false
                }
            });
        }

        document.addEventListener('DOMContentLoaded', () => {
            charts.temp = initChart('chart-temp', 'Temperature', '#f43f5e');
            charts.hum = initChart('chart-hum', 'Humidity', '#06b6d4');
            charts.light = initChart('chart-light', 'Light', '#f59e0b');
            charts.dist = initChart('chart-dist', 'Distance', '#10b981');

            fetchData();
            setInterval(fetchData, 2000);
        });

        async function fetchData() {
            const statusDot = document.getElementById('status-dot');
            const statusText = document.getElementById('status-text');

            try {
                const res = await fetch('/api/data');
                const json = await res.json();

                if (json.current && Object.keys(json.current).length > 0) {
                    const d = json.current;
                    
                    const temp = d.temperature !== undefined ? d.temperature : '--';
                    const hum = d.humidity !== undefined ? d.humidity : (d.umidity !== undefined ? d.umidity : '--');
                    const light = d.light !== undefined ? d.light : '--';
                    const dist = d.distance !== undefined ? d.distance : '--';

                    document.getElementById('val-temp').textContent = temp;
                    document.getElementById('val-hum').textContent = hum;
                    document.getElementById('val-light').textContent = light;
                    document.getElementById('val-dist').textContent = dist;

                    const ts = d.timestamp ? d.timestamp.split(' ')[1] || d.timestamp : new Date().toLocaleTimeString();
                    statusText.textContent = `Live Payload (${ts})`;
                    statusDot.className = 'status-dot active';
                } else {
                    statusText.textContent = 'Awaiting Telemetry...';
                    statusDot.className = 'status-dot';
                }

                if (json.history && json.history.length > 0) {
                    document.getElementById('total-samples').textContent = json.history.length;
                    calculateKPIStats(json.history);
                    updateCharts(json.history);
                }
            } catch (err) {
                statusText.textContent = 'Disconnected';
                statusDot.className = 'status-dot error';
            }
        }

        function calculateKPIStats(history) {
            const getValidNums = (key, altKey) => history.map(h => h[key] !== undefined ? h[key] : h[altKey]).filter(v => typeof v === 'number');

            const updateMinMax = (key, altKey, minElId, maxElId) => {
                const vals = getValidNums(key, altKey);
                if (vals.length > 0) {
                    document.getElementById(minElId).textContent = Math.min(...vals);
                    document.getElementById(maxElId).textContent = Math.max(...vals);
                }
            };

            updateMinMax('temperature', null, 'min-temp', 'max-temp');
            updateMinMax('humidity', 'umidity', 'min-hum', 'max-hum');
            updateMinMax('light', null, 'min-light', 'max-light');
            updateMinMax('distance', null, 'min-dist', 'max-dist');
        }

        function updateCharts(history) {
            const labels = history.map(h => {
                if (!h.timestamp) return '';
                return h.timestamp.split(' ')[1] || h.timestamp;
            });

            const updateSet = (chart, dataKey, altKey) => {
                chart.data.labels = labels;
                chart.data.datasets[0].data = history.map(h => h[dataKey] !== undefined ? h[dataKey] : h[altKey]);
                chart.update('none');
            };

            updateSet(charts.temp, 'temperature');
            updateSet(charts.hum, 'humidity', 'umidity');
            updateSet(charts.light, 'light');
            updateSet(charts.dist, 'distance');
        }

        function downloadCSV() {
            window.location.href = '/download';
        }
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    return render_template_string(DASHBOARD_HTML)


@app.route('/api/data')
def api_data():
    with data_lock:
        current = sensor_data.copy()
        history = list(data_history)
    return {"current": current, "history": history}


@app.route('/download')
def download_csv():
    with data_lock:
        history = list(data_history)

    if not history:
        return "No data available yet. Wait for sensor readings.", 404

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        "timestamp", "temperature", "humidity", "light", "distance"
    ])
    writer.writeheader()

    for row in history:
        writer.writerow({
            "timestamp": row.get("timestamp", ""),
            "temperature": row.get("temperature", ""),
            "humidity": row.get("humidity", row.get("umidity", "")),
            "light": row.get("light", ""),
            "distance": row.get("distance", "")
        })

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=RUNECRAFT_report.csv",
            "Content-Type": "text/csv; charset=utf-8"
        }
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)