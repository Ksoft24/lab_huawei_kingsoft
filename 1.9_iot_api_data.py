from flask import Flask, jsonify, request
import pymysql

app = Flask(__name__)

# ================== DB CONFIG ==================
DB_CONFIG = {
    "host": "localhost",
    "user": "kingsoft",
    "password": "Open@2026",
    "database": "db_iot_kingsoft",
    "cursorclass": pymysql.cursors.DictCursor
}

# ================== DB HELPER ==================
def get_connection():
    return pymysql.connect(**DB_CONFIG)

# ================== ROUTES ==================

@app.route("/api/readings", methods=["GET"])
def get_all_readings():
    """
    Endpoint principal para Power BI
    """
    limit = request.args.get("limit", 1000)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(f"""
        SELECT
            id,
            device_id,
            temperature,
            temperature_status,
            humidity,
            humidity_status,
            lux,
            lux_status,
            noise_level,
            noise_status,
            co_ppm,
            co_status,
            accel_x,
            accel_y,
            accel_z,
            accel_status,
          DATE_FORMAT(timestamp, '%%d/%%m/%%Y %%H:%%i:%%s') AS timestamp
        FROM sensor_readings
        ORDER BY timestamp  DESC
        LIMIT %s
    """, (int(limit),))

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(rows)


@app.route("/api/readings/latest", methods=["GET"])
def get_latest_reading():
    """
    Última lectura por dispositivo
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            id,
            device_id,
            temperature,
            temperature_status,
            humidity,
            humidity_status,
            lux,
            lux_status,
            noise_level,
            noise_status,
            co_ppm,
            co_status,
            accel_x,
            accel_y,
            accel_z,
            accel_status,
           DATE_FORMAT(timestamp, '%%d/%%m/%%Y %%H:%%i:%%s') AS timestamp
        FROM sensor_readings
        ORDER BY timestamp  DESC
        LIMIT 1
    """)

    row = cursor.fetchone()
    cursor.close()
    conn.close()

    return jsonify(row)


@app.route("/api/readings/device/<device_id>", methods=["GET"])
def get_by_device(device_id):
    """
    Lecturas por dispositivo
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            id,
            device_id,
            temperature,
            temperature_status,
            humidity,
            humidity_status,
            lux,
            lux_status,
            noise_level,
            noise_status,
            co_ppm,
            co_status,
            accel_x,
            accel_y,
            accel_z,
            accel_status,
            DATE_FORMAT(timestamp, '%%d/%%m/%%Y %%H:%%i:%%s') AS timestamp
        FROM sensor_readings
        WHERE device_id = %s
        ORDER BY timestamp  DESC
    """, (device_id,))

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(rows)


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

# ================== MAIN ==================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
