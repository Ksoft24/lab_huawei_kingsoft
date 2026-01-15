#include <WiFiS3.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include <DHT.h>
#include <BH1750.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>

// ================= WIFI =================
const char* WIFI_SSID = "CALERO";
const char* WIFI_PASS = "wendy12345";

// ================= MQTT =================
const char* MQTT_BROKER   = "161.132.56.91";
const int   MQTT_PORT     = 1883;
const char* MQTT_USER     = "adminmqtt";
const char* MQTT_PASSWORD = "calero2020";
const char* MQTT_TOPIC    = "lab/sensors/device01";

// ================= PINES =================
#define MQ7_PIN    A0
#define SOUND_PIN  A1
#define DHT_PIN    3
#define DHTTYPE    DHT22   // cambia si usas DHT11

// ================= OBJETOS =================
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

DHT dht(DHT_PIN, DHTTYPE);
BH1750 lightMeter;
Adafruit_MPU6050 mpu;

// ================= FUNCIONES =================

void connectWiFi() {
  Serial.print("Conectando a WiFi");
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\n✅ WiFi conectado");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
}

void connectMQTT() {
  mqttClient.setServer(MQTT_BROKER, MQTT_PORT);

  while (!mqttClient.connected()) {
    Serial.print("Conectando a MQTT... ");

    if (mqttClient.connect("arduino-device01", MQTT_USER, MQTT_PASSWORD)) {
      Serial.println("✅ Conectado");
    } else {
      Serial.print("❌ Error rc=");
      Serial.print(mqttClient.state());
      Serial.println(" | Reintentando...");
      delay(3000);
    }
  }
}

// ================= SETUP =================
void setup() {
  Serial.begin(9600);
  delay(1000);

  Wire.begin();
  dht.begin();
  lightMeter.begin(BH1750::CONTINUOUS_HIGH_RES_MODE);

  // -------- Inicializar MPU6050 --------
  if (!mpu.begin()) {
    Serial.println("❌ MPU6050 no detectado");
    while (1) delay(10);
  }

  mpu.setAccelerometerRange(MPU6050_RANGE_4_G);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

  Serial.println("✅ MPU6050 listo");

  connectWiFi();
  connectMQTT();
}

// ================= LOOP =================
void loop() {

  if (WiFi.status() != WL_CONNECTED) {
    connectWiFi();
  }

  if (!mqttClient.connected()) {
    connectMQTT();
  }

  mqttClient.loop();

  // -------- Lecturas --------
  int mq7Raw     = analogRead(MQ7_PIN);
  int soundRaw   = analogRead(SOUND_PIN);
  float temp     = dht.readTemperature();
  float hum      = dht.readHumidity();
  float lux      = lightMeter.readLightLevel();

  sensors_event_t accel, gyro, temp_mpu;
  mpu.getEvent(&accel, &gyro, &temp_mpu);

  if (isnan(temp) || isnan(hum)) {
    Serial.println("⚠️ Error leyendo DHT");
    return;
  }

  // -------- Conversión ADC (UNO R4 = 12 bits) --------
  float coVoltage    = mq7Raw   * (5.0 / 4095.0);
  float noiseVoltage = soundRaw * (5.0 / 4095.0);

  // Aproximaciones (ajustables)
  float co_ppm = coVoltage * 100.0;
  int noise    = soundRaw;

  // -------- Acelerómetro (m/s²) --------
  float ax = accel.acceleration.x;
  float ay = accel.acceleration.y;
  float az = accel.acceleration.z;

  // -------- JSON --------
  StaticJsonDocument<256> doc;

  doc["device_id"] = "device01";
  doc["temp"]  = temp;
  doc["hum"]   = hum;
  doc["lux"]   = (int)lux;
  doc["noise"] = noise;
  doc["co"]    = co_ppm;

  doc["ax"] = ax;
  doc["ay"] = ay;
  doc["az"] = az;

  char payload[256];
  serializeJson(doc, payload);

  // -------- Publicar --------
  if (mqttClient.publish(MQTT_TOPIC, payload)) {
    Serial.print("📤 MQTT: ");
    Serial.println(payload);
  } else {
    Serial.println("❌ Error publicando MQTT");
  }

  delay(2000);   // cada 2 segundos
}
