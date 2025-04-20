from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime

class Evento(BaseModel):
    id: Optional[str] = None
    tipo: str
    ubicacion: dict
    timestamp: datetime = datetime.now()
    
class Ubicacion(BaseModel):
    x: float  # Longitud
    y: float  # Latitud

class EventoReal(BaseModel):
    id: str
    uuid: str
    country: str
    city: str
    street: str
    location: Ubicacion
    type: Literal['ROAD_CLOSED']  # Tipo principal del evento
    subtype: Literal['ROAD_CLOSED_EVENT']  # Subtipo específico
    speed: int
    roadType: int
    inscale: bool
    confidence: int
    reliability: int
    pubMillis: int  # Timestamp en milisegundos
    timestamp: datetime = datetime.now()  # Fecha de procesamiento en tu sistema

    # Campo calculado para obtener la fecha del evento
    @property
    def event_date(self) -> datetime:
        return datetime.fromtimestamp(self.pubMillis / 1000)