from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class Ubicacion(BaseModel):
    longitud: float = Field(..., alias="x")
    latitud: float = Field(..., alias="y")

class EventoWazeRaw(BaseModel):
    """Modelo para los datos crudos de Waze"""
    id: str
    uuid: str
    country: str
    city: Optional[str] = None
    street: str
    location: dict
    type: str
    subtype: Optional[str] = None
    speed: int
    roadType: int
    inscale: bool
    confidence: int
    reliability: int
    pubMillis: int
    nearBy: Optional[str] = None
    provider: Optional[str] = None
    providerId: Optional[str] = None
    nComments: Optional[int] = None
    nThumbsUp: Optional[int] = None

    @property
    def event_date(self) -> datetime:
        return datetime.fromtimestamp(self.pubMillis / 1000)

class EventoEstandar(BaseModel):
    """Modelo para los datos estandarizados"""
    id_evento: str
    tipo: Literal["accidente", "congestion", "peligro", "obras", "policia", "cierre", "otro"]
    subtipo: Optional[str]
    comuna: str
    calle: str
    ubicacion: Ubicacion
    fecha: datetime
    gravedad: Literal["baja", "media", "alta"]
    confirmaciones: int = 0
    comentarios: int = 0
    fuente: Literal["waze"] = "waze"
    raw_data: dict  # Conservamos los datos originales

    @classmethod
    def from_waze_event(cls, waze_event: EventoWazeRaw):
        # Mapeo de tipos Waze a nuestros tipos estandarizados
        tipo_map = {
            "ACCIDENT": "accidente",
            "JAM": "congestion",
            "ROAD_CLOSED": "cierre",
            "POLICE": "policia",
            "HAZARD": {
                "HAZARD_ON_ROAD_POT_HOLE": "obras",
                "HAZARD_ON_ROAD_LANE_CLOSED": "obras",
                "HAZARD_ON_ROAD_CONSTRUCTION": "obras",
                "HAZARD_ON_ROAD_OBJECT": "peligro"
            }
        }
        
        waze_type = waze_event.type
        waze_subtype = waze_event.subtype or ""
        
        if waze_type in tipo_map:
            if isinstance(tipo_map[waze_type], dict):
                tipo = tipo_map[waze_type].get(waze_subtype, "peligro")
            else:
                tipo = tipo_map[waze_type]
        else:
            tipo = "otro"

        # Calcular gravedad
        score = waze_event.confidence * waze_event.reliability
        gravedad = "alta" if score > 60 else "media" if score > 30 else "baja"

        return cls(
            id_evento=waze_event.uuid,
            tipo=tipo,
            subtipo=waze_subtype if waze_subtype else None,
            comuna=waze_event.city.strip().title() if waze_event.city else "Desconocido",
            calle=waze_event.street,
            ubicacion=Ubicacion(**waze_event.location),
            fecha=waze_event.event_date,
            gravedad=gravedad,
            confirmaciones=waze_event.nThumbsUp or 0,
            comentarios=waze_event.nComments or 0,
            raw_data=waze_event.dict()
        )