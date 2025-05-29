from pymongo import MongoClient
import os
import certifi

MONGO_URI = os.getenv("MONGO_URI", 
    f"mongodb+srv://{os.getenv('MONGO_USER')}:{os.getenv('MONGO_PASSWORD')}@"
    f"{os.getenv('MONGO_CLUSTER')}/{os.getenv('MONGO_DB', 'eventos')}"
    "?retryWrites=true&w=majority&tls=true&tlsCAFile={}".format(certifi.where()))

client = MongoClient(
    MONGO_URI,
    connectTimeoutMS=5000,
    socketTimeoutMS=30000,
    serverSelectionTimeoutMS=5000
)

db = client.get_database(os.getenv("MONGO_DB", "eventos"))

# Colecciones
legacy_data = db.intento_1  # Solo para migración (luego se puede eliminar)
events_standardized = db.eventos_clean  # Única colección activa

# Índices para optimización
events_standardized.create_index("id_evento", unique=True)
events_standardized.create_index([("comuna", 1), ("tipo", 1)])
events_standardized.create_index("fecha")