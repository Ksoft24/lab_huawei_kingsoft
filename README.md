LABORATORIO SOFTWARE IOT-CLOUD-IA

Este repositorio contiene el material práctico y teórico para el laboratorio de IoT + Cloud + IA usando tecnologías como MQTT, Huawei Cloud, OpenEuler, Python, MySQL, Flask y modelos de inferencia. Cada sección está enlazada con el código y recursos dentro de este repositorio según los subtítulos del laboratorio.

🧠 1 — IOT-CLOUD
1.1 — Gráfico del circuito

Incluye un esquema de conexión de dispositivos (por ejemplo, Arduino) para simular sensores o dispositivos que envían datos al broker MQTT.

📌 Revisa las imágenes o diagramas en la carpeta arduino.

1.2 — Código Arduino

Este código se usa para enviar datos desde un Arduino al servidor/cloud usando MQTT.
Ejemplo de uso dentro de: arduino/

📌 Debes cargar el sketch en tu placa compatible y configurar el broker MQTT (URL y credenciales).

1.3 — (Teoría) Crear un ECS en Huawei Cloud

Un ECS (Elastic Cloud Server) es una instancia de máquina virtual dentro de Huawei Cloud donde puedes desplegar servicios (por ejemplo, MQTT Broker, API, bases de datos).

Inicia sesión en Huawei Cloud Console.

Elige ECS > Crear instancia y selecciona configuración de red/SO.

Asigna IP pública o elástica para acceso externo.

Accede con SSH y configura tus servicios.

1.4 — (Teoría) Instalación y configuración MQTT en OpenEuler

MQTT es un protocolo ligero de mensajería para IoT.

En tu ECS con OpenEuler, instala un broker (por ejemplo, Mosquitto):

sudo dnf install mosquitto
sudo systemctl enable --now mosquitto


Configura el archivo mosquitto.conf para permitir conexiones.

📌 El broker escuchará conexiones MQTT a las que tus dispositivos se suscribirán/públicarán.

1.5 — Test Python MQTT

Archivo: 1.5_iot_test_mqtt.py

Este script prueba la conexión vía MQTT desde Python al broker, publica y/o consume mensajes.

1.6 — Código Arduino — con MQTT

Versión más completa del sketch Arduino que se conecta al broker MQTT con credenciales y publica datos periódicamente.

📌 Ajusta las variables como URL y topics según tu broker configurado.

1.7 — (Teoría) Instalación y configuración MySQL en OpenEuler

MySQL es un motor de base de datos relacional que almacenará los eventos/datos recolectados desde MQTT.

En tu ECS con OpenEuler:

sudo dnf install mysql-server
sudo systemctl enable --now mysqld


Asegura tu instalación (mysql_secure_installation).

Crea base y tablas para almacenar los datos de IoT.

1.7 — Script para base de datos

Archivo: 1.7_bd.sql

Contiene el esquema de la base de datos (tablas, campos) para guardar los mensajes IoT.
Ejemplo:

CREATE TABLE messages (...);


Importa con:

mysql -u root -p < 1.7_bd.sql

1.8 — Código de almacenamiento MQTT a MySQL

Archivo: 1.8_iot_to_mysql_safety.py

Este script:

Se conecta al broker MQTT.

Se subscribe a topics.

Inserta los mensajes recibidos en tu base MySQL.

Este puente es fundamental para persistir tus datos IoT.

1.9 — Construcción de API para consumo de datos

Archivo: 1.9_iot_api_data.py

Aquí se construye una API (por ejemplo con Flask) que expone tus datos desde la base para consumo de aplicaciones/reportes.

Ejemplo de funciones:

/messages: devuelve datos IoT

/status: salud del servidor

1.10 — Test Python API

Archivo: 1.10_iot_test_data.py

Script que consume tu API y muestra los resultados. Permite verificar que la API responde correctamente.

1.11 — (Teoría) Conexión a Power BI

Para visualizar datos:

Desde Power BI Desktop, elige Obtener datos > Web/API.

Ingresa la URL de tu API (por ejemplo, http://<ip_ecs>:5000/messages).

Carga y crea reportes/dashboard usando tus datos IoT.

💡 Esto permite análisis visual de tendencias de sensores.

🧠 2 — IA-CLOUD

El objetivo de esta parte es usar IA para inferencia de imágenes con modelos y exponerlo como un API que pueda consumir dispositivos.

2.1 — Notebook Python para uso de biblioteca CLIP (análisis de imágenes y contexto)

Archivo: 2.1_inferencia_local.py

Este script usa una librería de IA que mezcla visión y texto (por ejemplo CLIP) para analizar imágenes. Permite clasificar o entender el contexto.

2.2 — Crear API Flask Python y exponerla

Archivo: 2.2_api_inferencia.py

Este servidor expone una API REST que recibe imágenes y retorna inferencias del modelo de IA.

2.3 — Código test para probar API

Archivo: 2.3_test_api_inferencia.py

Script que envía imágenes a tu API y recibe la respuesta del modelo, útil para validar que funciona correctamente.

2.4 — Código ESP32-CAM para consumir API enviando imagen

Dentro de esta parte deberías integrar en tu ESP32-CAM un sketch que capture una imagen y la envíe a la API de inferencia.

📌 Usa la dirección de tu API y formato JSON/multipart según el endpoint.

2.5 — Código para PC con OpenEuler — inferencia enviando imagen de cámara

Archivo: 2.5_inferencia_cam_local.py

Este código captura imágenes desde una cámara conectada a tu ECS/OpenEuler y las envía a la API para inferencia.

2.6 — Código para Raspberry con OpenEuler — inferencia enviando imagen de cámara

Archivo: 2.6_inferencia_raspberry.py

Similar al anterior, pero adaptado para una Raspberry Pi con OpenEuler.

2.7 — Código para Raspberry con OpenEuler — inferir localmente

(pendiente agregar si aplica)
Este módulo permitiría ejecutar el modelo de IA directamente en la Raspberry, sin llamar a API.

📌 Notas de teoría relevantes
☁️ Sobre MQTT y Huawei IoT

MQTT es un protocolo ligero de mensajería muy usado en IoT para enviar mensajes desde dispositivos al servidor/broker.

Huawei IoT Device SDK proporciona ejemplos y métodos para conectar con MQTT sobre Huawei Cloud IoTDA y obtener mensajes, autenticación y seguridad.

📌 Tips útiles

✔ Revisa variables de conexión:
Los scripts Python esperarán que especifiques:

broker MQTT (IP o dominio)

usuario/contraseña si corresponde

base de datos MySQL (host, usuario, pass)

✔ Prueba paso a paso:

MQTT local

Guardar datos a MySQL

API de datos

Visualización

📄 Licencia

Los materiales, laboratorios y ejemplos incluidos en este repositorio han sido elaborados como apoyo para actividades académicas y están alineados a los lineamientos y objetivos de la Huawei Teaching Competition, con fines de formación, demostración tecnológica y fortalecimiento de competencias en IoT, Cloud e Inteligencia Artificial.
