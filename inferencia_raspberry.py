import cv2
import base64
import requests
import os
import time
import random
import sys
import termios
import tty
from PIL import Image
from io import BytesIO

# -----------------------------
# Configuración
# -----------------------------
API_URL = "http://127.0.0.1:5000/infer"
CAMERA_ID = 0
BASE_DIR = "/home/calero/HUAWEI_ICT_TEACHING_2026/IMG"

os.makedirs(BASE_DIR, exist_ok=True)

# -----------------------------
# Utils
# -----------------------------
def get_key():
    """Lee una tecla sin enter (solo Linux/Unix)"""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        key = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return key.lower()

def frame_to_base64(frame):
    """Convierte frame OpenCV a base64 PNG"""
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil = Image.fromarray(img)
    buffer = BytesIO()
    pil.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

def save_image_from_base64(b64):
    """Guarda imagen base64 en BASE_DIR con nombre único"""
    img_bytes = base64.b64decode(b64)
    img = Image.open(BytesIO(img_bytes))
    unique_id = f"{int(time.time())}_{random.randint(1000,9999)}"
    filename = f"resultado_{unique_id}.png"
    final_path = os.path.join(BASE_DIR, filename)
    img.save(final_path)
    return final_path

# -----------------------------
# Captura de un frame
# -----------------------------
def capture_frame():
    cap = cv2.VideoCapture(CAMERA_ID)
    if not cap.isOpened():
        print("❌ No se pudo abrir la cámara")
        return None
    ret, frame = cap.read()
    cap.release()
    if not ret:
        print("❌ Error capturando frame")
        return None
    return frame

# -----------------------------
# Loop principal
# -----------------------------
def main():
    print("🎥 Programa iniciado")
    print("Presiona H para inferir | V para mostrar imagen | Q para salir")

    while True:
        key = get_key()

        if key == "h":
            frame = capture_frame()
            if frame is None:
                continue

            print("🧠 Inferencia en curso...")
            image_base64 = frame_to_base64(frame)
            payload = {
                "id_equipo": "RASPBERRY_CAM",
                "image_base64": image_base64,
                "retorno_imagen": "SI"
            }
            try:
                resp = requests.post(API_URL, json=payload, timeout=10)
                data = resp.json()
                print("✅ RESULTADOS INFERENCIA:")
                for k, v in data["results"].items():
                    print(f"  {k.upper()}: {v:.1f}%")

                if data.get("imagen_base64"):
                    path = save_image_from_base64(data["imagen_base64"])
                    print(f"🖼 Imagen inferida guardada en: {path}")

            except Exception as e:
                print("❌ Error API:", e)

        elif key == "v":
            frame = capture_frame()
            if frame is None:
                continue

            cv2.imshow("Frame Capturado", frame)
            print("Presiona cualquier tecla para cerrar la ventana")
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        elif key == "q":
            print("🔚 Saliendo del programa...")
            break

if __name__ == "__main__":
    main()
