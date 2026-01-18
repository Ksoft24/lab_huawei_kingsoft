import os
import clip
import torch
import time
import random
import string
import sys
import termios
import tty
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
import subprocess
import platform


# -----------------------------
# Detección de entorno
# -----------------------------
def is_raspberry():
    try:
        with open("/proc/device-tree/model") as f:
            return "raspberry" in f.read().lower()
    except:
        return False

HAS_GUI = bool(os.environ.get("DISPLAY"))
IS_RASPBERRY = is_raspberry()

print("🖥 GUI disponible:", HAS_GUI)
print("🍓 Raspberry detectado:", IS_RASPBERRY)

# -----------------------------
# Configuración CLIP
# -----------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)
model.eval()

# -----------------------------
# Carpeta de imágenes
# -----------------------------
BASE_DIR = os.path.expanduser("~/laboratorio_kingsoft")
os.makedirs(BASE_DIR, exist_ok=True)

print("📁 Imágenes se guardarán en:", BASE_DIR)

# -----------------------------
# Cámara
# -----------------------------
CAMERA_ID = 0   # cambia si es necesario

# -----------------------------
# Clases PPE
# -----------------------------
ppe_items = {
    "helmet": (
        "construction worker wearing a safety helmet",
        "person without a safety helmet"
    ),
    "vest": (
        "construction worker wearing an orange safety vest",
        "person without an safety vest"
    )
}

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

    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return Image.fromarray(img)

def infer_clip(image):
    """Inferencia local CLIP"""
    image_resized = image.resize((1024, 640))
    image_input = preprocess(image_resized).unsqueeze(0).to(device)

    results = {}
    start_time = time.time()
    with torch.no_grad():
        image_features = model.encode_image(image_input)
        image_features /= image_features.norm(dim=-1, keepdim=True)

        for item, texts in ppe_items.items():
            text_tokens = clip.tokenize(texts).to(device)
            text_features = model.encode_text(text_tokens)
            text_features /= text_features.norm(dim=-1, keepdim=True)

            logits = (image_features @ text_features.T) * 100
            probs = logits.softmax(dim=-1)

            confidence = probs[0][0].item() * 100
            results[item] = round(confidence, 2)

    end_time = time.time()
    return results, round(end_time - start_time, 3)

def draw_results(image, results):
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 24)
    except:
        font = ImageFont.load_default()

    x_text, y_text = 20, 20
    line_height = 40

    def get_color(conf):
        if conf >= 60:
            return (0, 255, 0)
        elif conf >= 40:
            return (255, 165, 0)
        else:
            return (255, 0, 0)

    for key, conf in results.items():
        draw.text(
            (x_text, y_text),
            f"{key.upper()}: {conf:.1f}%",
            fill=get_color(conf),
            font=font
        )
        y_text += line_height

    return image

def save_image(image):
    random_name = ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + ".png"
    save_path = os.path.join(BASE_DIR, random_name)
    image.save(save_path)
    return save_path

def show_image(path):
    """
    Decide automáticamente cómo mostrar la imagen
    """
    # Caso 1: hay entorno gráfico
    if HAS_GUI and not IS_RASPBERRY:
        print("🖥 Mostrando imagen con ventana gráfica")
        img = cv2.imread(path)
        cv2.imshow("Inferencia CLIP", img)
        cv2.waitKey(2000)
        cv2.destroyAllWindows()

    # Caso 2: Raspberry / sin GUI → ASCII en Python
    else:
        print("📟 Mostrando imagen en modo ASCII (Python)")
        try:
            show_ascii_image(path, width=80)
        except Exception as e:
            print("⚠️ Error mostrando ASCII:", e)


# -----------------------------
# Visualización ASCII (sin dependencias externas)
# -----------------------------
def show_ascii_image(image_path, width=80):
    chars = np.asarray(list(" .:-=+*#%@"))

    img = Image.open(image_path).convert("L")  # escala de grises
    w, h = img.size
    aspect_ratio = h / w
    new_height = int(aspect_ratio * width * 0.55)

    img = img.resize((width, new_height))
    img_array = np.array(img)

    img_norm = (img_array / 255.0) * (len(chars) - 1)
    img_chars = chars[img_norm.astype(int)]

    print("\n")
    for row in img_chars:
        print("".join(row))

# -----------------------------
# Loop principal
# -----------------------------
def main():
    print("\n🎥 Programa de inferencia CLIP iniciado")
    print("H = Inferir | Q = Salir\n")

    while True:
        key = get_key()

        if key == "h":
            frame = capture_frame()
            if frame is None:
                continue

            print("\n🧠 Inferencia en curso...")
            results, t_inf = infer_clip(frame)

            print(f"⏱ Tiempo: {t_inf}s")
            for k, v in results.items():
                print(f"  {k.upper()}: {v:.1f}%")

            frame_marked = draw_results(frame.copy(), results)
            path = save_image(frame_marked)
            print(f"🖼 Imagen guardada en: {path}")

            show_image(path)

        elif key == "q":
            print("🔚 Saliendo del programa...")
            break

if __name__ == "__main__":
    main()
