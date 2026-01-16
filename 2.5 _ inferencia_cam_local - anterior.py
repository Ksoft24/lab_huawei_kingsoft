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

# -----------------------------
# Configuración
# -----------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)
model.eval()

BASE_DIR = "/home/calero/HUAWEI_ICT_TEACHING_2026/IMG"
os.makedirs(BASE_DIR, exist_ok=True)

CAMERA_ID = 0

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
    # Convertir a PIL
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return Image.fromarray(img)

def infer_clip(image):
    """Inferencia local CLIP sobre PIL Image"""
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
    return results, round(end_time - start_time, 4)

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

# -----------------------------
# Loop principal
# -----------------------------
def main():
    print("🎥 Programa de inferencia CLIP local iniciado")
    print("H=inferir | Q=salir")

    while True:
        key = get_key()

        if key == "h":
            frame = capture_frame()
            if frame is None:
                continue

            print("🧠 Inferencia local en curso...")
            results, t_inf = infer_clip(frame)
            print(f"✅ Resultados (tiempo: {t_inf}s):")
            for k, v in results.items():
                print(f"  {k.upper()}: {v:.1f}%")

            frame_marked = draw_results(frame.copy(), results)
            path = save_image(frame_marked)
            print(f"🖼 Imagen marcada guardada en: {path}")

            # Mostrar imagen con OpenCV
            cv2.imshow(f"Inferencia CLIP | Tiempo: {t_inf}s", cv2.cvtColor(np.array(frame_marked), cv2.COLOR_RGB2BGR))
            cv2.waitKey(0)  # espera hasta que presiones cualquier tecla
            cv2.destroyAllWindows()

        elif key == "q":
            print("🔚 Saliendo del programa...")
            break

if __name__ == "__main__":
    main()
