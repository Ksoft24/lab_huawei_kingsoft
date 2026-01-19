#include "WiFi.h"
#include <HTTPClient.h>
#include "esp_camera.h"
#include "Base64.h"

// ================= WIFI =================
const char* ssid = "KINGSOFT";
const char* password = "wendy12345";

// ================= API ==================
const char* API_URL = "http://20.40.210.148:5001/infer";

// ================= CAMARA (AI THINKER) ==
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// =================================================

void setup() {
  Serial.begin(115200);
  delay(1000);

  // 🔌 Conectar WiFi
  WiFi.begin(ssid, password);
  Serial.print("Conectando WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n✅ WiFi conectado");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());

  // 📷 Configurar cámara
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer   = LEDC_TIMER_0;
  config.pin_d0       = Y2_GPIO_NUM;
  config.pin_d1       = Y3_GPIO_NUM;
  config.pin_d2       = Y4_GPIO_NUM;
  config.pin_d3       = Y5_GPIO_NUM;
  config.pin_d4       = Y6_GPIO_NUM;
  config.pin_d5       = Y7_GPIO_NUM;
  config.pin_d6       = Y8_GPIO_NUM;
  config.pin_d7       = Y9_GPIO_NUM;
  config.pin_xclk     = XCLK_GPIO_NUM;
  config.pin_pclk     = PCLK_GPIO_NUM;
  config.pin_vsync    = VSYNC_GPIO_NUM;
  config.pin_href     = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn     = PWDN_GPIO_NUM;
  config.pin_reset    = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  // ⚠️ Para estabilidad en envío base64
  config.frame_size   = FRAMESIZE_QVGA;   // 320x240
  config.jpeg_quality = 12;
  config.fb_count     = 1;

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("❌ Error cámara: 0x%x\n", err);
    ESP.restart();
  }

  Serial.println("✅ Cámara inicializada");
}

// =================================================

void loop() {

  Serial.println("\n📸 Capturando imagen...");

  camera_fb_t * fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("❌ Error capturando imagen");
    delay(3000);
    return;
  }

  // 📦 Convertir a Base64
  String imageBase64 = base64::encode(fb->buf, fb->len);
  esp_camera_fb_return(fb);

  Serial.print("✅ Imagen codificada. Tamaño base64: ");
  Serial.println(imageBase64.length());

  // 🌐 Enviar al API
  if (WiFi.status() == WL_CONNECTED) {

    HTTPClient http;
    http.begin(API_URL);
    http.addHeader("Content-Type", "application/json");

    String payload = "{";
    payload += "\"id_equipo\":\"ESP32_CAM_01\",";
    payload += "\"image_base64\":\"" + imageBase64 + "\",";
    payload += "\"retorno_imagen\":\"NO\"";
    payload += "}";

    Serial.println("🚀 Enviando imagen al API...");
    int httpCode = http.POST(payload);
    String response = http.getString();

    Serial.print("📡 HTTP Code: ");
    Serial.println(httpCode);

    Serial.println("📨 Respuesta API:");
    Serial.println(response);

    http.end();
  }
  else {
    Serial.println("⚠️ WiFi desconectado");
  }

  // ⏱️ Enviar cada 20 segundos
  delay(20000);
}
