import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Conexión a base de datos en memoria
conn = sqlite3.connect(":memory:")
cursor = conn.cursor()

# Crear tablas
cursor.execute("""
CREATE TABLE usuarios (
    id_usuario INTEGER PRIMARY KEY,
    clave_usuario TEXT,
    tipo_usuario TEXT,
    area_departamento TEXT,
    estatus_usuario TEXT,
    tiene_qr INTEGER,
    tiene_rfid INTEGER,
    tiene_registro_facial INTEGER,
    fecha_alta TEXT
)
""")

cursor.execute("""
CREATE TABLE vehiculos (
    id_vehiculo INTEGER PRIMARY KEY,
    id_usuario INTEGER,
    placa_hash TEXT,
    tipo_vehiculo TEXT,
    marca TEXT,
    modelo TEXT,
    color TEXT,
    estatus_vehiculo TEXT
)
""")

cursor.execute("""
CREATE TABLE dispositivos (
    id_dispositivo INTEGER PRIMARY KEY,
    codigo_dispositivo TEXT,
    nombre_dispositivo TEXT,
    tipo_dispositivo TEXT,
    modelo TEXT,
    ubicacion TEXT,
    estatus_dispositivo TEXT
)
""")

cursor.execute("""
CREATE TABLE puntos_acceso (
    id_punto_acceso INTEGER PRIMARY KEY,
    nombre_punto TEXT,
    tipo_punto TEXT,
    sentido TEXT,
    ubicacion TEXT,
    estatus_punto TEXT
)
""")

cursor.execute("""
CREATE TABLE horarios (
    id_horario INTEGER PRIMARY KEY,
    id_usuario INTEGER,
    tipo_horario TEXT,
    dia_semana TEXT,
    hora_inicio TEXT,
    hora_fin TEXT,
    vigente INTEGER
)
""")

cursor.execute("""
CREATE TABLE invitaciones (
    id_invitacion INTEGER PRIMARY KEY,
    id_usuario_anfitrion INTEGER,
    id_usuario_invitado INTEGER,
    tipo_invitacion TEXT,
    estado_invitacion TEXT,
    fecha_creacion TEXT,
    fecha_inicio_vigencia TEXT,
    fecha_fin_vigencia TEXT,
    uso_unico INTEGER
)
""")

cursor.execute("""
CREATE TABLE accesos_iot (
    id_evento INTEGER PRIMARY KEY,
    fecha TEXT,
    hora TEXT,
    id_usuario INTEGER,
    id_vehiculo INTEGER,
    id_punto_acceso INTEGER,
    id_dispositivo INTEGER,
    id_horario INTEGER,
    id_invitacion INTEGER,
    tipo_usuario TEXT,
    tipo_acceso TEXT,
    tipo_movimiento TEXT,
    metodo_verificacion TEXT,
    resultado TEXT,
    motivo_resultado TEXT,
    confianza_ia REAL,
    tiempo_respuesta_ms INTEGER,
    uso_invitacion INTEGER,
    apertura_manual INTEGER,
    fallo_dispositivo INTEGER
)
""")

# Cargar archivos CSV
usuarios = pd.read_csv("usuarios.csv")
vehiculos = pd.read_csv("vehiculos.csv")
dispositivos = pd.read_csv("dispositivos.csv")
puntos_acceso = pd.read_csv("puntos_acceso.csv")
horarios = pd.read_csv("horarios.csv")
invitaciones = pd.read_csv("invitaciones.csv")
accesos_iot = pd.read_csv("accesos_iot.csv")

# Insertar datos en SQLite
usuarios.to_sql("usuarios", conn, if_exists="append", index=False)
vehiculos.to_sql("vehiculos", conn, if_exists="append", index=False)
dispositivos.to_sql("dispositivos", conn, if_exists="append", index=False)
puntos_acceso.to_sql("puntos_acceso", conn, if_exists="append", index=False)
horarios.to_sql("horarios", conn, if_exists="append", index=False)
invitaciones.to_sql("invitaciones", conn, if_exists="append", index=False)
accesos_iot.to_sql("accesos_iot", conn, if_exists="append", index=False)

# Consulta uniendo la tabla de hechos con dimensiones
query = """
SELECT 
    a.fecha,
    u.tipo_usuario,
    pa.nombre_punto,
    pa.tipo_punto,
    d.tipo_dispositivo,
    a.metodo_verificacion,
    a.resultado,
    COUNT(a.id_evento) AS total_accesos,
    SUM(a.apertura_manual) AS total_aperturas_manuales,
    SUM(a.fallo_dispositivo) AS total_fallas_dispositivo,
    AVG(a.tiempo_respuesta_ms) AS promedio_tiempo_respuesta
FROM accesos_iot a
JOIN usuarios u ON a.id_usuario = u.id_usuario
JOIN puntos_acceso pa ON a.id_punto_acceso = pa.id_punto_acceso
JOIN dispositivos d ON a.id_dispositivo = d.id_dispositivo
GROUP BY 
    a.fecha,
    u.tipo_usuario,
    pa.nombre_punto,
    pa.tipo_punto,
    d.tipo_dispositivo,
    a.metodo_verificacion,
    a.resultado
"""

df = pd.read_sql_query(query, conn)

print("Reporte general de accesos:")
print(df)

# Gráfica: accesos por método de verificación
query_grafica = """
SELECT 
    metodo_verificacion,
    COUNT(id_evento) AS total_accesos
FROM accesos_iot
GROUP BY metodo_verificacion
"""

df_grafica = pd.read_sql_query(query_grafica, conn)

plt.figure(figsize=(8, 6))
plt.bar(df_grafica["metodo_verificacion"], df_grafica["total_accesos"])
plt.xlabel("Método de verificación")
plt.ylabel("Total de accesos")
plt.title("Total de accesos por método de verificación")
plt.xticks(rotation=30)
plt.tight_layout()
plt.show()

# Gráfica: accesos autorizados y rechazados
query_resultado = """
SELECT 
    resultado,
    COUNT(id_evento) AS total
FROM accesos_iot
GROUP BY resultado
"""

df_resultado = pd.read_sql_query(query_resultado, conn)

plt.figure(figsize=(8, 6))
plt.bar(df_resultado["resultado"], df_resultado["total"])
plt.xlabel("Resultado del acceso")
plt.ylabel("Total")
plt.title("Accesos por resultado")
plt.xticks(rotation=20)
plt.tight_layout()
plt.show()