import json
import math
import mysql.connector
import paho.mqtt.client as mqtt

# ================= MQTT CONFIG =================
MQTT_BROKER = "20.83.43.2"
MQTT_PORT = 1883
MQTT_TOPIC = "lab/sensors/#"

MQTT_USERNAME = "adminmqtt"
MQTT_PASSWORD = "calero2020"

# ================= MYSQL CONFIG =================
DB_CONFIG = {
    "host": "localhost",
    "user": "kingsoft",
    "password": "Open@2026",
    "database": "db_iot_kingsoft",
    "port": 3306
}

# ================= THRESHOLDS =================
THRESHOLDS = {
    "temperature": {"min": 18, "max": 30, "critical": 35},
    "humidity": {"min": 30, "max": 70, "critical": 80},
    "lux": {"min": 100, "max": 800, "critical": 1200},
    "noise": {"max": 600, "critical": 850},
    "co": {"max": 35, "critical": 100},
    "accel": {
        "fall_drop": 0.5,   # sudden Z change (g)
        "fall_peak": 2.0   # impact magnitude (g)
    }
}

previous_z = None

# ================= FUNCTIONS =================
def get_status(value, limits):
    if value is None or value == 0:
        return "NORMAL"

    if "min" in limits and value < limits["min"]:
        return "RISK"

    if value >= limits.get("critical", float("inf")):
        return "CRITICAL"

    if value > limits.get("max", float("inf")):
        return "RISK"

    return "NORMAL"


def detect_fall(ax, ay, az):
    global previous_z

    if az is None:
        return "NORMAL"

    magnitude = math.sqrt(ax**2 + ay**2 + az**2)
    fall = False

    if previous_z is not None:
        dz = abs(az - previous_z)
        if dz > THRESHOLDS["accel"]["fall_drop"] and magnitude > THRESHOLDS["accel"]["fall_peak"]:
            fall = True

    previous_z = az
    return "FALL" if fall else "NORMAL"


def save_to_db(r):
    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor()

    sql = """
        INSERT INTO sensor_readings (
            device_id,
            temperature, temperature_status,
            humidity, humidity_status,
            lux, lux_status,
            noise_level, noise_status,
            co_ppm, co_status,
            accel_x, accel_y, accel_z, accel_status
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    values = (
        r["device_id"],
        r["temperature"], r["temperature_status"],
        r["humidity"], r["humidity_status"],
        r["lux"], r["lux_status"],
        r["noise"], r["noise_status"],
        r["co"], r["co_status"],
        r["ax"], r["ay"], r["az"], r["accel_status"]
    )

    cur.execute(sql, values)
    conn.commit()
    cur.close()
    conn.close()

# ================= MQTT CALLBACKS =================

def on_connect(client, userdata, flags, reasonCode, properties=None):
    if reasonCode == 0:
        print("✅ Connected to MQTT broker")
        client.subscribe(MQTT_TOPIC, qos=1)
    else:
        print("❌ MQTT connection failed, code:", reasonCode)

def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode())

    ax = payload.get("ax", 0)
    ay = payload.get("ay", 0)
    az = payload.get("az", 0)

    record = {
        "device_id": payload.get("device_id", "opta01"),

        "temperature": payload.get("temp", 0),
        "humidity": payload.get("hum", 0),
        "lux": payload.get("lux", 0),
        "noise": payload.get("noise", 0),
        "co": payload.get("co", 0),

        "ax": ax,
        "ay": ay,
        "az": az
    }

    record["temperature_status"] = get_status(record["temperature"], THRESHOLDS["temperature"])
    record["humidity_status"] = get_status(record["humidity"], THRESHOLDS["humidity"])
    record["lux_status"] = get_status(record["lux"], THRESHOLDS["lux"])
    record["noise_status"] = get_status(record["noise"], THRESHOLDS["noise"])
    record["co_status"] = get_status(record["co"], THRESHOLDS["co"])
    record["accel_status"] = detect_fall(ax, ay, az)

    save_to_db(record)
    print("💾 Saved:", record)

# ================= MQTT CLIENT =================
client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    protocol=mqtt.MQTTv311
)
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

client.on_connect = on_connect
client.on_message = on_message

client.reconnect_delay_set(min_delay=1, max_delay=120)
client.connect(MQTT_BROKER, MQTT_PORT, 60)

print("📡 Listening to MQTT messages...")
client.loop_forever()
