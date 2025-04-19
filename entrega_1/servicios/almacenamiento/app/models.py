from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Evento(BaseModel):
    id: Optional[str] = None
    tipo: str
    ubicacion: dict
    timestamp: datetime = datetime.now()