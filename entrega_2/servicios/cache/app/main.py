from fastapi import FastAPI, HTTPException
from cache import cache
import requests
import os

STORAGE_SERVICE_URL = os.getenv("STORAGE_SERVICE_URL", "http://almacenamiento:8000")

# Obtiene el TTL desde una variable de entorno. Si no está definida, usa 1800 por defecto.
TTL = int(os.getenv("TTL_CACHE", 1800))

app = FastAPI()


@app.get("/eventos/{evento_id}", status_code=200 )
async def leer_evento_cache(evento_id: str):
    # Buscar en Redis primero
    cached_event = cache.get(evento_id)
    if cached_event:
        # return {"data": cached_event, "source": "la tengo aqui en CACHE ,che"}
        return {"message" : "CACHE"}
    
    # Si no está en cache, consultar al almacenamiento
    response = requests.get(f"{STORAGE_SERVICE_URL}/eventos/{evento_id}")
    if response.status_code == 200:
        evento = response.json()
        cache.set(evento_id, str(evento), ex=TTL)# TTL de media hora
        # cache.set(evento_id, str(evento))  # sin TTL
        # return {"data": evento, "source": "tuve q ir a buscar al BACK mi loko:("}
        return {"message" : "BACKEND"}
    
    raise HTTPException(status_code=404, detail="Evento no encontrado")