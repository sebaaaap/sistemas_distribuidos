from fastapi import FastAPI, HTTPException
from cache import cache
import requests
import os

STORAGE_SERVICE_URL = os.getenv("STORAGE_SERVICE_URL", "http://almacenamiento:8000")
app = FastAPI()

@app.get("/eventos/{evento_id}")
async def leer_evento_cache(evento_id: str):
    # Buscar en Redis primero
    cached_event = cache.get(evento_id)
    if cached_event:
        return {"data": cached_event, "source": "cache"}
    
    # Si no está en cache, consultar al almacenamiento
    response = requests.get(f"{STORAGE_SERVICE_URL}/eventos/{evento_id}")
    if response.status_code == 200:
        evento = response.json()
        cache.set(evento_id, str(evento), ex=3600)  # TTL de 1 hora
        return {"data": evento, "source": "storage"}
    
    raise HTTPException(status_code=404, detail="Evento no encontrado")