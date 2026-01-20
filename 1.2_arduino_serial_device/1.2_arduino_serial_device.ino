#include <Wire.h>
#include <DHT.h>
#include <BH1750.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>

// ================= PINS =================
#define MQ7_PIN    A0
#define SOUND_PIN  A1
#define DHT_PIN    3
#define DHTTYPE    DHT22   // Change to DHT11 if needed

// ================= OBJECTS =================
DHT dht(DHT_PIN, DHTTYPE);
BH1750 lightMeter;
Adafruit_MPU6050 mpu;

// ================= SETUP =================
void setup() {
  Serial.begin(9600);
  delay(1000);

  Serial.println("=== INITIALIZING SENSORS ===");

  // I2C
  Wire.begin();

  // DHT
  dht.begin();

  // BH1750
  if (!lightMeter.begin(BH1750::CONTINUOUS_HIGH_RES_MODE)) {
    Serial.println("❌ Error: BH1750 not detected");
    while (1);
  }

  // MPU6050
  if (!mpu.begin()) {
    Serial.println("❌ Error: MPU6050 not detected");
    while (1);
  }

  mpu.setAccelerometerRange(MPU6050_RANGE_4_G);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

  Serial.println("✅ Sensors ready\n");
}

// ================= LOOP =================
void loop() {

  // ---------- Analog readings ----------
  int mq7Raw   = analogRead(MQ7_PIN);
  int soundRaw = analogRead(SOUND_PIN);

  // ---------- DHT ----------
  float temp = dht.readTemperature();
  float hum  = dht.readHumidity();

  if (isnan(temp) || isnan(hum)) {
    Serial.println("⚠️ Error reading DHT sensor");
  }

  // ---------- BH1750 ----------
  float lux = lightMeter.readLightLevel();

  // ---------- MPU6050 ----------
  sensors_event_t accel, gyro, temp_mpu;
  mpu.getEvent(&accel, &gyro, &temp_mpu);

  float ax = accel.acceleration.x;
  float ay = accel.acceleration.y;
  float az = accel.acceleration.z;

  // ---------- Display on Serial ----------
  Serial.println("----------- SENSOR READINGS -----------");

  Serial.print("MQ7 (CO RAW): ");
  Serial.println(mq7Raw);

  Serial.print("Sound RAW: ");
  Serial.println(soundRaw);

  Serial.print("Temperature (°C): ");
  Serial.println(temp);

  Serial.print("Humidity (%): ");
  Serial.println(hum);

  Serial.print("Light (Lux): ");
  Serial.println(lux);

  Serial.print("Accel X (m/s2): ");
  Serial.println(ax);

  Serial.print("Accel Y (m/s2): ");
  Serial.println(ay);

  Serial.print("Accel Z (m/s2): ");
  Serial.println(az);

  Serial.println("---------------------------------------\n");

  delay(2000);   // every 2 seconds
}
