from fastapi import FastAPI, HTTPException
from app.database import events_collection
from app.models import EventoReal
from bson import ObjectId
from datetime import datetime
from typing import List, Dict, Any

app = FastAPI()

#prueba xdddd

@app.post("/eventos")
async def crear_evento(evento: EventoReal):
    # Convertimos a dict y añadimos fecha de creación
    evento_data = evento.dict()
    evento_data["created_at"] = datetime.utcnow()
    
    result = events_collection.insert_one(evento_data)
    return {"id": str(result.inserted_id)}

@app.get("/")
async def crear_evento():
    return { "messagge": "ola sebita "}

@app.get("/eventos/getall_ids")
async def get_all():
    try:
        # Obtener todos los documentos y extraer solo el campo "_id"
        eventos = events_collection.find({}, {"_id": 1}) # Proyección: solo el _id)
        
        # Convertir los ObjectId a strings (MongoDB devuelve ObjectId por defecto)
        eventos_ids = [str(evento["_id"]) for evento in eventos]
        
        return { "ids" : eventos_ids}
        print(eventos)
        # return {"lista": eventos}
    
    except Exception as e:
        print(f"Error: {e}")  # Para debug
        raise HTTPException(status_code=500, detail=f"Error al obtener eventos: {str(e)}")
        

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

@app.get("/eventos/getall_bruto", response_model=List[Dict[str, Any]])
async def get_all_bruto_events():
    try:
        # 1. Obtener TODOS los eventos de la colección (sin filtros)
        eventos = list(events_collection.find({}))
        
        if not eventos:
            raise HTTPException(status_code=404, detail="No hay eventos en la base de datos")

        # 2. Convertir ObjectId a string para cada evento
        for evento in eventos:
            evento["_id"] = str(evento["_id"])

        return eventos

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")



