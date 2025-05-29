from fastapi import FastAPI, HTTPException, Query
from app.database import legacy_data, events_standardized
from app.models import EventoEstandar, EventoWazeRaw
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/eventos")
async def crear_evento(evento: Dict[str, Any]):
    """
    Endpoint para nuevos eventos. Estandariza y guarda DIRECTAMENTE en eventos_estandarizados.
    """
    try:
        # Validar y estandarizar
        evento_estandar = EventoEstandar.from_waze_event(evento)
        
        # Guardar solo en la colección estandarizada
        result = events_standardized.replace_one(
            {"id_evento": evento_estandar.id_evento},
            evento_estandar.dict(),
            upsert=True
        )
        
        return {
            "status": "success",
            "id": evento_estandar.id_evento,
            "action": "inserted" if result.upserted_id else "updated"
        }
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/migrar")
async def migrar_legacy_data():
    """
    Migra UNA SOLA VEZ los datos de intento_1 a eventos_estandarizados.
    """
    try:
        total = legacy_data.count_documents({})
        if total == 0:
            return {"status": "skip", "message": "No hay datos para migrar"}
        
        logger.info(f"Iniciando migración de {total} registros...")
        migrados = 0
        
        for doc in legacy_data.find({}):
            try:
                evento = EventoEstandar.from_waze_event(doc)
                events_standardized.replace_one(
                    {"id_evento": evento.id_evento},
                    evento.dict(),
                    upsert=True
                )
                migrados += 1
            except Exception as e:
                logger.warning(f"Error en documento {doc.get('_id')}: {str(e)}")
        
        return {
            "status": "completed",
            "total": total,
            "migrados": migrados,
            "errores": total - migrados
        }
        
    except Exception as e:
        logger.error(f"Error en migración: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/eventos")
async def obtener_eventos(
    comuna: Optional[str] = None,
    tipo: Optional[str] = None,
    fecha_desde: Optional[datetime] = None,
    fecha_hasta: Optional[datetime] = None,
    limit: int = 100
):
    """
    Consulta eventos estandarizados con filtros.
    """
    try:
        query = {}
        if comuna:
            query["comuna"] = comuna.title()
        if tipo:
            query["tipo"] = tipo.lower()
        if fecha_desde or fecha_hasta:
            query["fecha"] = {}
            if fecha_desde:
                query["fecha"]["$gte"] = fecha_desde
            if fecha_hasta:
                query["fecha"]["$lte"] = fecha_hasta
        
        eventos = list(events_standardized.find(query).limit(limit))
        for ev in eventos:
            ev["_id"] = str(ev["_id"])
        
        return {
            "count": len(eventos),
            "results": eventos
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/legacy")
async def eliminar_legacy_data():
    """
    Elimina los datos legacy (ejecutar solo después de migrar).
    """
    try:
        result = legacy_data.drop()
        return {"status": "success", "message": "Colección 'intento_1' eliminada"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))