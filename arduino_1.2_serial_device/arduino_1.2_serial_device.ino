#include <Wire.h>
#include <DHT.h>
#include <BH1750.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>

// ================= PINES =================
#define MQ7_PIN    A0
#define SOUND_PIN  A1
#define DHT_PIN    3
#define DHTTYPE    DHT22   // Cambia a DHT11 si corresponde

// ================= OBJETOS =================
DHT dht(DHT_PIN, DHTTYPE);
BH1750 lightMeter;
Adafruit_MPU6050 mpu;

// ================= SETUP =================
void setup() {
  Serial.begin(9600);
  delay(1000);

  Serial.println("=== INICIANDO SENSORES ===");

  // I2C
  Wire.begin();

  // DHT
  dht.begin();

  // BH1750
  if (!lightMeter.begin(BH1750::CONTINUOUS_HIGH_RES_MODE)) {
    Serial.println("❌ Error: BH1750 no detectado");
    while (1);
  }

  // MPU6050
  if (!mpu.begin()) {
    Serial.println("❌ Error: MPU6050 no detectado");
    while (1);
  }

  mpu.setAccelerometerRange(MPU6050_RANGE_4_G);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

  Serial.println("✅ Sensores listos\n");
}

// ================= LOOP =================
void loop() {

  // ---------- Lecturas analógicas ----------
  int mq7Raw   = analogRead(MQ7_PIN);
  int soundRaw = analogRead(SOUND_PIN);

  // ---------- DHT ----------
  float temp = dht.readTemperature();
  float hum  = dht.readHumidity();

  if (isnan(temp) || isnan(hum)) {
    Serial.println("⚠️ Error leyendo DHT");
  }

  // ---------- BH1750 ----------
  float lux = lightMeter.readLightLevel();

  // ---------- MPU6050 ----------
  sensors_event_t accel, gyro, temp_mpu;
  mpu.getEvent(&accel, &gyro, &temp_mpu);

  float ax = accel.acceleration.x;
  float ay = accel.acceleration.y;
  float az = accel.acceleration.z;

  // ---------- Mostrar por Serial ----------
  Serial.println("----------- LECTURAS -----------");

  Serial.print("MQ7 (CO RAW): ");
  Serial.println(mq7Raw);

  Serial.print("Sonido RAW: ");
  Serial.println(soundRaw);

  Serial.print("Temperatura (°C): ");
  Serial.println(temp);

  Serial.print("Humedad (%): ");
  Serial.println(hum);

  Serial.print("Luz (Lux): ");
  Serial.println(lux);

  Serial.print("Accel X (m/s2): ");
  Serial.println(ax);

  Serial.print("Accel Y (m/s2): ");
  Serial.println(ay);

  Serial.print("Accel Z (m/s2): ");
  Serial.println(az);

  Serial.println("--------------------------------\n");

  delay(2000);   // cada 2 segundos
}
