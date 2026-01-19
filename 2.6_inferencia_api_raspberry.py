import cv2
import base64
import requests
import os
import time
import random
import sys
from PIL import Image
from io import BytesIO
import platform

# -----------------------------
# Detección de sistema
# -----------------------------
IS_WINDOWS = platform.system().lower().startswith("win")

if not IS_WINDOWS:
    import termios
    import tty

# -----------------------------
# Configuración
# -----------------------------
API_URL = "http://20.40.210.148:5001/infer"
CAMERA_ID = 1

# Carpeta base:
if IS_WINDOWS:
    BASE_DIR = os.path.join(os.getcwd(), "IMG")
else:
    BASE_DIR = "/home/calero/HUAWEI_ICT_TEACHING_2026/IMG"

os.makedirs(BASE_DIR, exist_ok=True)

# -----------------------------
# Utils teclado
# -----------------------------
def get_key():
    """Lee una tecla sin enter (Windows y Linux)"""
    if IS_WINDOWS:
        import msvcrt
        return msvcrt.getch().decode("utf-8").lower()
    else:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            key = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return key.lower()

# -----------------------------
# Utils imagen
# -----------------------------
def frame_to_base64(frame):
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil = Image.fromarray(img)
    buffer = BytesIO()
    pil.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

def save_image_from_base64(b64):
    img_bytes = base64.b64decode(b64)
    img = Image.open(BytesIO(img_bytes))
    unique_id = f"{int(time.time())}_{random.randint(1000,9999)}"
    filename = f"resultado_{unique_id}.png"
    final_path = os.path.join(BASE_DIR, filename)
    img.save(final_path)
    return final_path

# -----------------------------
# ASCII Viewer (Linux/Raspberry)
# -----------------------------
def show_ascii_image(image_path, width=80):
    img = Image.open(image_path).convert("L")
    aspect_ratio = img.height / img.width
    height = int(width * aspect_ratio * 0.55)
    img = img.resize((width, height))

    pixels = img.getdata()
    chars = "@%#*+=-:. "
    new_pixels = [chars[pixel // 25] for pixel in pixels]
    ascii_str = "".join(new_pixels)

    ascii_img = "\n".join(
        ascii_str[i:i+width] for i in range(0, len(ascii_str), width)
    )

    os.system("clear")
    print(ascii_img)

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
# Mostrar imagen según sistema
# -----------------------------
def display_image(image_path):
    if IS_WINDOWS:
        img = cv2.imread(image_path)
        cv2.imshow("Resultado Inferencia", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        show_ascii_image(image_path)

# -----------------------------
# Loop principal
# -----------------------------
def main():
    print("🎥 Programa iniciado")
    print("H = Inferir | Q = Salir")

    while True:
        key = get_key()

        if key == "h":
            frame = capture_frame()
            if frame is None:
                continue

            print("🧠 Inferencia en curso...")
            image_base64 = frame_to_base64(frame)

            payload = {
                "id_equipo": "CAM_PC" if IS_WINDOWS else "RASPBERRY_CAM",
                "image_base64": image_base64,
                "retorno_imagen": "SI"
            }

            try:
                resp = requests.post(API_URL, json=payload, timeout=15)
                data = resp.json()

                print("✅ RESULTADOS:")
                for k, v in data["results"].items():
                    print(f"  {k.upper()}: {v:.1f}%")

                if data.get("imagen_base64"):
                    path = save_image_from_base64(data["imagen_base64"])
                    print(f"🖼 Imagen guardada en: {path}")
                    display_image(path)

            except Exception as e:
                print("❌ Error API:", e)

        elif key == "q":
            print("🔚 Saliendo...")
            break

# -----------------------------
if __name__ == "__main__":
    main()
