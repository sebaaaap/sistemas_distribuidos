from fastapi import FastAPI, HTTPException
from database import events_collection
from models import EventoReal
from bson import ObjectId
from datetime import datetime

app = FastAPI()

@app.post("/eventos/")
async def crear_evento(evento: EventoReal):
    # Convertimos a dict y añadimos fecha de creación
    evento_data = evento.dict()
    evento_data["created_at"] = datetime.utcnow()
    
    result = events_collection.insert_one(evento_data)
    return {"id": str(result.inserted_id)}

@app.get("/")
async def crear_evento():
    return { "messagge": "hola gai"}

@app.get("/eventos/{evento_id}")
async def leer_evento(evento_id: str):
    try:
        obj_id = ObjectId(evento_id)
        evento = events_collection.find_one({"_id": obj_id})
        if evento:
            evento["_id"] = str(evento["_id"])  # Convertir ObjectId a string
            return evento
    except:
        pass  
    raise HTTPException(status_code=404, detail="Evento no encontrado")