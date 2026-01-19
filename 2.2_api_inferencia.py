import os
import time
import json
import base64
from io import BytesIO

import torch
import clip
from PIL import Image, ImageDraw, ImageFont
from flask import Flask, request, jsonify
from flask_cors import CORS

# -----------------------------
# Inicialización Flask
# -----------------------------
app = Flask(__name__)

CORS(app)
# -----------------------------
# Modelo CLIP
# -----------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)
model.eval()

# -----------------------------
# PPE a detectar
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
def base64_to_pil(base64_str):
    image_bytes = base64.b64decode(base64_str)
    return Image.open(BytesIO(image_bytes)).convert("RGB")

def pil_to_base64(image):
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

def get_color(conf):
    if conf >= 60:
        return (0, 255, 0)
    elif conf >= 40:
        return (255, 165, 0)
    else:
        return (255, 0, 0)

def draw_results(image, results):
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 24)
    except:
        font = ImageFont.load_default()

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

    return image

# -----------------------------
# Endpoint
# -----------------------------
@app.route("/infer", methods=["POST"])
def infer():
    start_time = time.time()
    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON vacío"}), 400

    image_base64 = data.get("image_base64")
    id_equipo = data.get("id_equipo")
    retorno_imagen = data.get("retorno_imagen", "NO").upper()

    if not image_base64 or not id_equipo:
        return jsonify({"error": "Faltan campos requeridos"}), 400

    try:
        image = base64_to_pil(image_base64)
        image = image.resize((1024, 640))
    except Exception as e:
        return jsonify({"error": f"Error procesando imagen: {str(e)}"}), 400

    image_input = preprocess(image).unsqueeze(0).to(device)
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

    imagen_retorno_base64 = ""
    if retorno_imagen == "SI":
        image_marked = draw_results(image.copy(), results)
        imagen_retorno_base64 = pil_to_base64(image_marked)

    response = {
        "id_equipo": id_equipo,
        "inference_time_seconds": round(end_time - start_time, 4),
        "results": results,
        "imagen_base64": imagen_retorno_base64
    }

    return jsonify(response)

# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
