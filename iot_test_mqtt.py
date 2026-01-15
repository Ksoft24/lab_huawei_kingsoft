import json
import time
import random
import paho.mqtt.client as mqtt

# ================ MQTT CONFIG =================
BROKER_IP = "161.132.56.91"
BROKER_PORT = 1883
TOPIC = "lab/sensors/device01"

USERNAME = "adminmqtt"
PASSWORD = "calero2020"

# ================ MQTT CLIENT =================
client = mqtt.Client()
client.username_pw_set(USERNAME, PASSWORD)
client.connect(BROKER_IP, BROKER_PORT, 60)

# ================ PAYLOAD GENERATOR =================
def generate_payload(fall=False):
    if fall:
        ax = random.uniform(1.5, 2.5)
        ay = random.uniform(1.5, 2.5)
        az = random.uniform(2.2, 3.0)   # impacto
    else:
        ax = random.uniform(0.0, 0.2)
        ay = random.uniform(0.0, 0.2)
        az = random.uniform(0.8, 1.1)

    payload = {
        "device_id": "opta01",

        "temp": round(random.uniform(20, 38), 2),
        "hum": round(random.uniform(30, 85), 2),
        "lux": random.randint(50, 1400),
        "noise": random.randint(200, 900),
        "co": round(random.uniform(5, 120), 2),

        "ax": round(ax, 2),
        "ay": round(ay, 2),
        "az": round(az, 2)
    }

    return payload

# ================ MAIN LOOP =================
print("🚀 Sending test MQTT payloads...")

while True:
    # Cada 10 mensajes, simula una caída
    simulate_fall = random.randint(1, 10) == 10

    payload = generate_payload(fall=simulate_fall)
    client.publish(TOPIC, json.dumps(payload), qos=1)

    print("📤 Sent:", payload)
    time.sleep(3)
