from pydantic import BaseModel, Field
from typing import Optional, Literal, Union
from datetime import datetime

class Ubicacion(BaseModel):
    x: float  # Longitud
    y: float  # Latitud

class EventoReal(BaseModel):
    id: str
    uuid: str
    country: str
    city: Optional[str] = None  # Ahora es opcional
    street: str
    location: dict  # O usa el modelo Ubicacion si prefieres
    type: str  # Permite cualquier tipo (POLICE, HAZARD, etc.)
    subtype: Optional[str] = None  # Ahora es opcional
    speed: int
    roadType: int  # Acepta cualquier número (1, 2, 3, etc.)
    inscale: bool  # Permite True/False sin restricción
    confidence: int
    reliability: int
    pubMillis: int
    # Campos opcionales adicionales
    nearBy: Optional[str] = None
    provider: Optional[str] = None
    providerId: Optional[str] = None
    nComments: Optional[int] = None
    # Campo calculado
    @property
    def event_date(self) -> datetime:
        return datetime.fromtimestamp(self.pubMillis / 1000)