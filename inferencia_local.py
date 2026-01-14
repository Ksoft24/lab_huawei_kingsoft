import os
import clip
import torch
import time
import json
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import matplotlib.pyplot as plt
import random
import string

# -----------------------------
# Configuración
# -----------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)
model.eval()

# -----------------------------
# Cargar imagen (archivo local o URL)
# -----------------------------
#url_o_ruta = "/home/calero/Descargas/istockphoto-1481370371-1024x1024.jpg"
#url_o_ruta = "/home/calero/Descargas/chef-apuntando-la-lateral-sobre-fondo-blanco.jpg"
url_o_ruta  = "https://img.freepik.com/fotos-premium/trabajador-ropa-especial-fabrica-casco-contexto-produccion_564714-11567.jpg"
try:
    if os.path.exists(url_o_ruta):
        print(f"Cargando archivo local: {url_o_ruta}")
        image = Image.open(url_o_ruta).convert("RGB")
    elif url_o_ruta.startswith(('http://', 'https://')):
        print(f"Cargando imagen desde URL: {url_o_ruta}")
        response = requests.get(url_o_ruta)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content)).convert("RGB")
    else:
        raise FileNotFoundError(f"La ruta o URL no es válida o no existe: {url_o_ruta}")

    image = image.resize((1024, 640))
    print("Imagen cargada y redimensionada con éxito.")

except requests.exceptions.RequestException as e:
    print(f"Error al cargar la imagen desde la URL: {e}")
except FileNotFoundError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"Ocurrió un error inesperado: {e}")

# -----------------------------
# Preprocesamiento
# -----------------------------
image_input = preprocess(image).unsqueeze(0).to(device)

# -----------------------------
# PPE a detectar (BINARIO + PROMPTS FUERTES)
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
# Inferencia + tiempo
# -----------------------------
start_time = time.time()
results = {}

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

# -----------------------------
# JSON final
# -----------------------------
output_json = {
    "inference_time_seconds": round(end_time - start_time, 4),
    "results": results
}

print("\nJSON de salida:")
print(json.dumps(output_json, indent=4))

# -----------------------------
# Dibujar labels laterales
# -----------------------------
draw = ImageDraw.Draw(image)

try:
    font = ImageFont.truetype("DejaVuSans-Bold.ttf", 24)
except:
    font = ImageFont.load_default()

def get_color(conf):
    if conf >= 60:
        return (0, 255, 0)
    elif conf >= 40:
        return (255, 165, 0)
    else:
        return (255, 0, 0)

x_text, y_text = 20, 20
line_height = 40

for key, conf in results.items():
    draw.text(
        (x_text, y_text),
        f"{key.upper()}: {conf:.1f}%",
        fill=get_color(conf),
        font=font
    )
    y_text += line_height
    

# -----------------------------
# Guardar imagen con nombre aleatorio
# -----------------------------
random_name = ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + ".png"
save_path = os.path.join(os.getcwd(), random_name)
image.save(save_path)
print(f"Imagen guardada localmente como: {save_path}")

# -----------------------------
# Mostrar imagen final
# -----------------------------
plt.figure(figsize=(12, 7))
plt.imshow(image)
plt.axis("off")
plt.title(f"Inferencia CLIP | Tiempo: {output_json['inference_time_seconds']}s")
plt.show()