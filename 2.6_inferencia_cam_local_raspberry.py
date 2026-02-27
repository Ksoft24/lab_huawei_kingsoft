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
# Environment detection
# -----------------------------
def is_raspberry():
    try:
        with open("/proc/device-tree/model") as f:
            return "raspberry" in f.read().lower()
    except:
        return False

HAS_GUI = bool(os.environ.get("DISPLAY"))
IS_RASPBERRY = is_raspberry()

print("🖥 GUI available:", HAS_GUI)
print("🍓 Raspberry detected:", IS_RASPBERRY)

# -----------------------------
# CLIP configuration
# -----------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)
model.eval()

# -----------------------------
# Image folder
# -----------------------------
BASE_DIR = os.path.expanduser("~/laboratorio_kingsoft")
os.makedirs(BASE_DIR, exist_ok=True)

print("📁 Images will be saved in:", BASE_DIR)

# -----------------------------
# Camera
# -----------------------------
CAMERA_ID = 0   # change if necessary

# -----------------------------
# PPE classes
# -----------------------------
ppe_items = {
    "helmet": (
        "construction worker wearing a safety helmet",
        "person without a safety helmet"
    ),
    "vest": (
        "construction worker wearing an orange safety vest",
        "person without a safety vest"
    )
}

# -----------------------------
# Utils
# -----------------------------
def get_key():
    """Reads a single key without pressing Enter (Linux/Unix only)"""
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
        print("❌ Unable to open camera")
        return None
    ret, frame = cap.read()
    cap.release()
    if not ret:
        print("❌ Error capturing frame")
        return None

    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return Image.fromarray(img)

def infer_clip(image):
    """Local CLIP inference"""
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
    Automatically decides how to display the image
    """
    # Case 1: graphical environment available
    if HAS_GUI and not IS_RASPBERRY:
        print("🖥 Displaying image using GUI window")
        img = cv2.imread(path)
        cv2.imshow("CLIP Inference", img)
        cv2.waitKey(2000)
        cv2.destroyAllWindows()

    # Case 2: Raspberry / no GUI → ASCII in terminal
    else:
        print("📟 Displaying image in ASCII mode (Python)")
        try:
            show_ascii_image(path, width=80)
        except Exception as e:
            print("⚠️ ASCII display error:", e)


# -----------------------------
# ASCII visualization (no external dependencies)
# -----------------------------
def show_ascii_image(image_path, width=80):
    chars = np.asarray(list(" .:-=+*#%@"))

    img = Image.open(image_path).convert("L")  # grayscale
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
# Main loop
# -----------------------------
def main():
    print("\n🎥 CLIP inference program started")
    print("H = Infer | Q = Exit\n")

    while True:
        key = get_key()

        if key == "h":
            frame = capture_frame()
            if frame is None:
                continue

            print("\n🧠 Running inference...")
            results, t_inf = infer_clip(frame)

            print(f"⏱ Inference time: {t_inf}s")
            for k, v in results.items():
                print(f"  {k.upper()}: {v:.1f}%")

            frame_marked = draw_results(frame.copy(), results)
            path = save_image(frame_marked)
            print(f"🖼 Image saved at: {path}")

            show_image(path)

        elif key == "q":
            print("🔚 Exiting program...")
            break

if __name__ == "__main__":
    main()