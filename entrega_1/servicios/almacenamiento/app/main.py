from fastapi import FastAPI, HTTPException
from database import events_collection
from models import Evento
from bson import ObjectId
import os

app = FastAPI()
@app.post("/eventos/")
async def crear_evento(evento: Evento):
    result = events_collection.insert_one(evento.dict())
    return {"id": str(result.inserted_id)}

@app.get("/")
async def crear_evento():
    return { "messagge": "hola que tal"}

@app.get("/eventos/{evento_id}")
async def leer_evento(evento_id: str):
    try:
        # Convierte el string a ObjectId de MongoDB
        obj_id = ObjectId(evento_id)
        evento = events_collection.find_one({"_id": obj_id})  # Busca con ObjectId
        if evento:
            evento["_id"] = str(evento["_id"])  # Convierte ObjectId a string para la respuesta
            return evento
    except:
        pass  
    raise HTTPException(status_code=404, detail="Evento no encontrado")