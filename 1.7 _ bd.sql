CREATE TABLE sensor_readings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_id VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    temperature FLOAT,
    temperature_status VARCHAR(10),

    humidity FLOAT,
    humidity_status VARCHAR(10),

    lux FLOAT,
    lux_status VARCHAR(10),

    noise_level INT,
    noise_status VARCHAR(10),

    co_ppm FLOAT,
    co_status VARCHAR(10),

    accel_x FLOAT,
    accel_y FLOAT,
    accel_z FLOAT,
    accel_status VARCHAR(10)
);



🌐 Endpoints listos para Power BI
Endpoint	Uso
/api/readings	Todas las lecturas
/api/readings?limit=500	Últimos 500
/api/readings/latest	Última lectura
/api/readings/device/opta01	Por dispositivo