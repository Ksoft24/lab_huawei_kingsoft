import time
import json
import ssl
import sys
import random
import paho.mqtt.client as mqtt

# =====================================================
# 🔧 CONFIGURACIÓN IOTDA
# =====================================================
DEVICE_ID = "6986a85a6c06717b23ceba8b_0001"
DEVICE_SECRET = "0c59ebe5d5c711980b21c6aa5c99899acea31be8aea2571079ceba5fa7b0039a"

HOSTNAME = "8097b99f91.st1.iotda-device.ap-southeast-2.myhuaweicloud.com"
PORT = 8883

CLIENT_ID = "6986a85a6c06717b23ceba8b_0001_0_0_2026020703"
USERNAME = DEVICE_ID
PASSWORD = DEVICE_SECRET

TOPIC_PUB = f"$oc/devices/{DEVICE_ID}/sys/properties/report"

# =====================================================
# 🔔 FLAGS
# =====================================================
connected = False

# =====================================================
# 📡 CALLBACKS
# =====================================================
def on_connect(client, userdata, flags, rc):
    global connected
    if rc == 0:
        connected = True
        print("✅ CONECTADO A HUAWEI IOTDA")
    else:
        print(f"❌ ERROR MQTT rc={rc}")

def on_disconnect(client, userdata, rc):
    print("🔌 DESCONECTADO", rc)

def on_publish(client, userdata, mid):
    print("📤 Publicación confirmada (mid:", mid, ")")

# =====================================================
# 🚀 MQTT CLIENT
# =====================================================
client = mqtt.Client(client_id=CLIENT_ID, protocol=mqtt.MQTTv311)
client.username_pw_set(USERNAME, PASSWORD)

client.tls_set(
    cert_reqs=ssl.CERT_REQUIRED,
    tls_version=ssl.PROTOCOL_TLSv1_2
)

client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_publish = on_publish

print("☁️ Conectando a IoTDA...")
client.connect(HOSTNAME, PORT, keepalive=60)
client.loop_start()

# =====================================================
# ⏳ ESPERAR CONEXIÓN
# =====================================================
timeout = time.time() + 10
while not connected and time.time() < timeout:
    time.sleep(0.2)

if not connected:
    print("❌ NO AUTENTICADO")
    client.loop_stop()
    sys.exit(1)

# =====================================================
# 🔁 ENVÍO DE 50 VALORES CADA 1 MINUTO
# =====================================================
INTERVALO_ENTRE_MENSAJES = 60 / 50  # 1.2 segundos

try:
    while True:
        print("⏱️ Enviando 50 valores...")

        for i in range(50):
            payload = {
                "services": [
                    {
                        "service_id": "kingsoft_data",
                        "properties": {
                            "temp": round(random.uniform(20, 30), 2),
                            "hum": round(random.uniform(40, 70), 2),
                            "lux": random.randint(100, 600),
                            "noise": round(random.uniform(30, 60), 2),
                            "co": round(random.uniform(1, 10), 2),
                            "ax": round(random.uniform(-5, 5), 2),
                            "ay": round(random.uniform(-5, 5), 2),
                            "az": round(random.uniform(-5, 5), 2)
                        }
                    }
                ]
            }

            client.publish(TOPIC_PUB, json.dumps(payload), qos=1)
            time.sleep(INTERVALO_ENTRE_MENSAJES)

        print("✅ Lote completado — esperando próximo minuto\n")

except KeyboardInterrupt:
    print("🛑 Deteniendo cliente...")

# =====================================================
# ⏹️ CIERRE LIMPIO
# =====================================================
client.loop_stop()
client.disconnect()
print("🧹 Cliente cerrado correctamente")
