import base64
import requests
import time
import random

from PIL import Image
from io import BytesIO
import os

# -----------------------------
# Configuración
# -----------------------------
API_URL = "http://20.40.210.148:5000/infer"

# === ELIGE UNA ===
url_o_ruta = "/home/calero/Descargas/istockphoto-1481370371-1024x1024.jpg"
#url_o_ruta = "/home/calero/Descargas/chef-apuntando-la-lateral-sobre-fondo-blanco.jpg"
#url_o_ruta = "https://img.freepik.com/fotos-premium/trabajador-ropa-especial-fabrica-casco-contexto-produccion_564714-11567.jpg"

OUTPUT_IMAGE = "resultado.png"

# -----------------------------
# Utils
# -----------------------------
def image_to_base64_from_local(path):
    with Image.open(path) as img:
        buffer = BytesIO()
        img.convert("RGB").save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

def image_to_base64_from_url(url):
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    img = Image.open(BytesIO(resp.content))
    buffer = BytesIO()
    img.convert("RGB").save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

def base64_to_image(base64_str, output_path):
    image_bytes = base64.b64decode(base64_str)
    image = Image.open(BytesIO(image_bytes))

    base_dir = "/home/calero/HUAWEI_ICT_TEACHING_2026/IMG"

    name, ext = os.path.splitext(output_path)
    unique_id = f"{int(time.time())}_{random.randint(1000,9999)}"

    final_name = f"{name}_{unique_id}{ext}"
    final_path = os.path.join(base_dir, final_name)

    image.save(final_path)
    return final_path


# -----------------------------
# Cargar imagen (auto)
# -----------------------------
if url_o_ruta.startswith("http"):
    print("📥 Cargando imagen desde URL...")
    image_base64 = image_to_base64_from_url(url_o_ruta)
else:
    if not os.path.exists(url_o_ruta):
        raise FileNotFoundError(f"No existe el archivo: {url_o_ruta}")
    print("📂 Cargando imagen local...")
    image_base64 = image_to_base64_from_local(url_o_ruta)

# -----------------------------
# Request
# -----------------------------
payload = {
    "id_equipo": "CAMARA_TEST",
    "image_base64": image_base64,
    "retorno_imagen": "SI"
}

response = requests.post(API_URL, json=payload, timeout=30)

# -----------------------------
# Respuesta
# -----------------------------
if response.status_code == 200:
    data = response.json()


    print("\n✅ RESPUESTA API")
    print("ID Equipo:", data["id_equipo"])
    print("Tiempo inferencia:", data["inference_time_seconds"], "s")
    print("Resultados:")
    for k, v in data["results"].items():
        print(f"  {k}: {v}%")

    if data.get("imagen_base64"):
        base64_to_image(data["imagen_base64"], OUTPUT_IMAGE)
        print(f"\n🖼 Imagen resultado guardada en: {OUTPUT_IMAGE}")

    

else:
    print("❌ Error:", response.status_code)
    print(response.text)
