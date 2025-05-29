import os
import csv
from pymongo import MongoClient
from datetime import datetime

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "eventos")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "intento_1")

if not MONGO_URI:
    raise ValueError("La variable de entorno MONGO_URI no está definida")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]

print("Conectado a MongoDB Atlas")
print("Base de datos:", db.name)
print("Colección:", collection.name)

os.makedirs("outputs", exist_ok=True)

def estandarizar_evento(ev):
    try:
        uuid = (ev.get("uuid") or "").strip()
        tipo = (ev.get("type") or "").lower().strip()
        comuna = (ev.get("city") or "desconocida").strip()
        timestamp = ev.get("pubMillis")
        if timestamp:
            timestamp = datetime.fromtimestamp(timestamp / 1000).isoformat()
        else:
            timestamp = ""

        descripcion = (ev.get("subtype") or "").strip()

        if not uuid or not tipo:
            return None

        return [uuid, tipo, comuna, timestamp, descripcion]
    except Exception as e:
        print("Error estandarizando evento:", e)
        return None

total = collection.count_documents({})
print(f"Documentos encontrados en MongoDB: {total}")

exportados = 0
descartados = 0

with open("outputs/eventos_filtrados.csv", "w", newline='', encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["uuid", "tipo", "comuna", "timestamp", "descripcion"])

    for ev in collection.find():
        fila = estandarizar_evento(ev)
        if fila:
            writer.writerow(fila)
            exportados += 1
        else:
            descartados += 1

print(f"Exportación completada:")
print(f"Eventos válidos exportados: {exportados}")
print(f"Eventos descartados por formato inválido: {descartados}")
print(f"Archivo generado: outputs/eventos_filtrados.csv")
