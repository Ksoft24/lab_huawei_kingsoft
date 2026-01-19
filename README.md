# LABORATORIO SOFTWARE IOT-CLOUD-IA

Este repositorio contiene el material **práctico y teórico** para el
laboratorio de **IoT + Cloud + IA** usando tecnologías como **MQTT,
Huawei Cloud, OpenEuler, Python, MySQL, Flask y modelos de inferencia**.
Cada sección está enlazada con el código y recursos dentro de este
repositorio según los subtítulos del laboratorio.

------------------------------------------------------------------------

# 🧠 1 --- IOT-CLOUD

El objetivo de esta sección es implementar un **ecosistema IoT completo**, donde los dispositivos físicos (sensores y microcontroladores) capturan datos, los transmiten mediante el protocolo **MQTT**, se almacenan en una base de datos en la nube y finalmente se exponen mediante una **API para su visualización y análisis**.

Se desarrolla el flujo completo de datos:

**dispositivo → broker MQTT → procesamiento → base de datos → API → visualización**

Este laboratorio permite comprender la integración entre **hardware, redes, sistemas operativos en la nube (OpenEuler), bases de datos, servicios web y herramientas de analítica**, simulando un escenario real de arquitectura IoT empresarial.

## **1.1 --- Gráfico del circuito**

Incluye un esquema de conexión de dispositivos con microcontralador y tarjeta Wifi con los sensores necesarios para el laboratorio.


<p align="center">
  <img src="1.1 img_board_bb.png" width="500">
</p>

Materiales

✅ Arduino R4 WiFi
Para lectura de sensores y envío de datos vía serial o MQTT.

✅ ESP32-CAM
Captura y envío de imágenes para inferencia de IA.

✅ Raspberry Pi 4 B
Nodo de procesamiento y pruebas con OpenEuler.

🌡️ DHT11 / DHT22 - Sensor de temperatura y humedad.

💡 BH1750 - Sensor de luminosidad (lux).

🧭 MPU6050 - Acelerómetro y giroscopio (movimiento y orientación).

🛢️ MQ-7 - Sensor de Monoxido de Carbono

Camara web USB

Realizar la Integracion del Arduino conforme el Diagrama
Realizar la Integracion de la ESP32-CAM, conforme al diagram
Colocar la Camara Web al puerto usb de Raspberry pi 4B
------------------------------------------------------------------------

## **1.2 --- Código Arduino**

Este código se usa para probar la obtencion de datos desde un Microcontrolador.\

📄 **Archivo:** `arduino_1.2_serial_device.ino`


------------------------------------------------------------------------

## **1.3 --- Crear un ECS en Huawei Cloud**

Un **ECS (Elastic Cloud Server)** es una instancia de máquina virtual
dentro de Huawei Cloud donde puedes desplegar servicios (por ejemplo,
MQTT Broker, API, bases de datos).

-   Inicia sesión en **Huawei Cloud Console**.\
-   Elige **ECS \> Crear instancia** y selecciona configuración de
    red/SO.\
-   Asigna **IP pública o elástica** para acceso externo.\
-   Accede con **SSH** y configura tus servicios.

------------------------------------------------------------------------

## **1.4 ---  Instalación y configuración MQTT en OpenEuler**

MQTT es un **protocolo ligero de mensajería para IoT**.

En nuestro servidor con OpenEuler, instalaremos el broker Mosquitto:

    sudo dnf install mosquitto
    sudo systemctl enable --now mosquitto

Configura el archivo **mosquitto.conf** para permitir conexiones.

Asi mismo revisa la guia detallada de instalacion en el documento

📄 **Archivo:** `1.4_OpenEuler_MQTT.docx`

📌 **El broker escuchará conexiones MQTT a las que tus dispositivos se
suscribirán/publicarán.**

------------------------------------------------------------------------

## **1.5 --- Test Python MQTT**

📄 **Archivo:** `1.5_iot_test_mqtt.py`

Este script prueba la conexión vía MQTT desde Python al broker, publica
y/o consume mensajes.

------------------------------------------------------------------------

## **1.6 --- Código Arduino --- con MQTT**

Versión más completa del sketch Arduino que se conecta al broker MQTT
con credenciales y publica datos periódicamente.

📄 **Archivo:** `arduino_1.6_iot_device.ino`

📌 **Debes cargar el sketch en tu placa compatible y configurar el
broker MQTT (URL y credenciales).**

------------------------------------------------------------------------

## **1.7 ---  Instalación y configuración Mariadb en OpenEuler**

Mariadb es un **motor de base de datos relacional** que almacenará los
eventos/datos recolectados desde MQTT.

En tu ECS con OpenEuler:

    sudo dnf install mysql-server
    sudo systemctl enable --now mysqld

Asegura tu instalación (**mysql_secure_installation**).\
Crea base y tablas para almacenar los datos de IoT.

Asi mismo revisa la guia detallada de instalacion en el documento

📄 **Archivo:** `1.7_OpenEuler_Mariadb.docx`

------------------------------------------------------------------------

## **1.7 --- Script para base de datos**

📄 **Archivo:** `1.7_bd.sql`

Contiene el esquema de la base de datos (tablas y campos).

------------------------------------------------------------------------

## **1.8 --- Código de almacenamiento MQTT a MySQL**

📄 **Archivo:** `1.8_iot_to_mysql_safety.py`

Este script: - Se conecta al broker MQTT.\
- Se subscribe a topics.\
- Inserta los mensajes recibidos en MySQL.

Este puente permite la persistencia de datos IoT.

Realizaremos la prueba corriendo el script y observaremos en el log que se se almacena correctamente

**python3 1.8_iot_to_mariadb.py**

Ahora tambien correremos el proceso en segundo plano para que este no bloquee la terminal

**nohup python3 1.8_iot_to_mariadb.py > demo_iot_mariadb.log 2>&1 &**

📌 ojo que **nohup** es una forma temporal de ejecutar un script en segundo plano, lo ideal es utilizar un servicio para entornos de produccion.
------------------------------------------------------------------------

## **1.9 --- Construcción de API para consumo de datos**

Construcción de una API ( con Flask) para exponer datos que se encuentra almacenados en nuestra base de datos.

Instalmos primero **pip install flask** , **pip install flask-cors**, **pip install pymysql**

Los principales metodos son:

GET **/api/health**
Permite verificar que la API se encuentra operativa. Retorna un mensaje de estado confirmando que el servicio Flask está activo y respondiendo correctamente.

GET **/api/readings**
Devuelve el listado de lecturas de sensores almacenadas en la base de datos MariaDB. Admite el parámetro opcional limit para restringir la cantidad de registros retornados (por ejemplo: /api/readings?limit=50).

GET **/api/readings/latest**
Retorna la última lectura registrada en el sistema, permitiendo acceder rápidamente al dato más reciente generado por los dispositivos IoT.

GET **/api/readings/device/<device_id>**
Permite consultar todas las lecturas asociadas a un dispositivo específico, identificado por su device_id, facilitando el análisis individual por equipo o sensor.

El archivo del api es:
📄 **Archivo:** `1.9_iot_api_data.py`

Asi mismo agregar a la regla de entrada el puerto **5000**

Realizaremos la prueba corriendo el script y observaremos en el log que se se expone correctamente

**python3 1.9_iot_api_data.py**

Ahora tambien correremos el proceso en segundo plano para que este no bloquee la terminal

**nohup python3 1.9_iot_api_data.py > demo_api_data.log 2>&1 &**

📌 ojo que **nohup** es una forma temporal de ejecutar un script en segundo plano, lo ideal es utilizar un servicio para entornos de produccion.
------------------------------------------------------------------------

## **1.10 --- Test Python API**

📄 **Archivo:** `1.10_iot_test_data.py`

Script que consume la API y valida su funcionamiento.

------------------------------------------------------------------------

## **1.11 --- Conexión a Power BI**

Para visualizar datos: - Power BI Desktop → **Obtener datos \>
Web/API**\
- Ingresa la URL de tu API.\
- Carga y crea dashboards.

------------------------------------------------------------------------

# 🧠 2 --- IA-CLOUD

El objetivo de esta sección es aplicar **Inteligencia Artificial para análisis de imágenes**, desplegar modelos como servicios en la nube y permitir que distintos dispositivos (PC, Raspberry y ESP32-CAM) consuman estos servicios mediante APIs.

Se trabaja el flujo completo:  
**captura de imagen → inferencia → exposición por API → consumo desde dispositivos**.

------------------------------------------------------------------------

## **2.1 --- Notebook Python con CLIP**

📄 **Archivo:** `2.1_inferencia_local.py`

Este módulo permite realizar **inferencia local de imágenes** utilizando una librería de visión e interpretación de contexto (por ejemplo, CLIP).  
Se emplea para validar el modelo, comprender su funcionamiento y evaluar resultados antes de desplegarlo como servicio.

------------------------------------------------------------------------

## **2.2 --- Crear API Flask Python**

📄 **Archivo:** `2.2_api_inferencia.py`

En este archivo se construye una **API REST con Flask** que expone el modelo de inferencia.  
La API recibe imágenes desde clientes externos y retorna los resultados del análisis, permitiendo desacoplar el modelo del dispositivo que captura la imagen.

------------------------------------------------------------------------

## **2.3 --- Código test para probar API**

📄 **Archivo:** `2.3_test_api_inferencia.py`

Este script permite **validar el funcionamiento de la API**, enviando una imagen de prueba y verificando la respuesta del modelo.  
Es fundamental para comprobar conectividad, formato de datos y estabilidad del servicio.

------------------------------------------------------------------------

## **2.4 --- Código ESP32-CAM**

Este módulo integra un **ESP32-CAM** para capturar imágenes y enviarlas directamente a la API de inferencia.  
Permite evaluar escenarios de **edge computing e IoT visual**, donde un dispositivo embebido interactúa con servicios de IA en la nube.

<p align="center">
  <img src="1.1 img_esp32-cam.png" width="500">
</p>

------------------------------------------------------------------------

## **2.5 --- PC con OpenEuler**

📄 **Archivo:** `2.5_inferencia_cam_local.py`

Este código captura imágenes desde una **cámara conectada a un PC con OpenEuler** y las envía a la API para su análisis.  
Se utiliza para pruebas de escritorio, validación de rendimiento y depuración del sistema.

------------------------------------------------------------------------

## **2.6 --- Raspberry con OpenEuler**

📄 **Archivo:** `2.6_inferencia_raspberry.py`

Versión adaptada para ejecutarse en una **Raspberry Pi con OpenEuler**, permitiendo realizar inferencias remotas desde un dispositivo de bajo consumo.  
Simula escenarios reales de despliegue en campo.

<p align="center">
  <img src="1.1 img_raspberry pi4.png" width="500">
</p>

------------------------------------------------------------------------

## **2.7 --- Inferencia local en Raspberry**

*(Pendiente de implementación)*

Este módulo permitirá ejecutar el modelo de **Inteligencia Artificial directamente en la Raspberry**, sin depender de una API externa.  
Este enfoque reduce latencia, dependencia de red y mejora la autonomía del sistema.


------------------------------------------------------------------------

# 📌 Notas de teoría relevantes

## ☁️ Sobre MQTT y Huawei IoT

MQTT es un protocolo ligero para mensajería IoT.\
Huawei IoT Device SDK facilita la conexión a Huawei Cloud IoTDA.

------------------------------------------------------------------------

# 📌 Tips útiles

### ✔ Revisa variables de conexión

-   Broker MQTT\
-   Usuario / contraseña\
-   Base de datos MySQL

### ✔ Prueba paso a paso

1.  MQTT local\
2.  MySQL\
3.  API\
4.  Visualización

------------------------------------------------------------------------

# 📄 Licencia

Los materiales, laboratorios y ejemplos incluidos en este repositorio
han sido elaborados como apoyo para actividades académicas y están
alineados a los lineamientos y objetivos de la **Huawei Teaching
Competition**, con fines de formación, demostración tecnológica y
fortalecimiento de competencias en **IoT, Cloud e Inteligencia
Artificial**.


Arduino es una marca registrada de Arduino AG. 
Este proyecto utiliza placas y herramientas compatibles con Arduino únicamente con fines educativos y demostrativos. 
El uso del nombre Arduino en este repositorio es solo referencial y no implica afiliación, patrocinio ni aprobación oficial por parte de Arduino.
