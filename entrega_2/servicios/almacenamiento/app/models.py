from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
from datetime import datetime
from enum import Enum

class TipoEvento(str, Enum):
    ACCIDENTE = "accidente"
    CONGESTION = "congestion"
    PELIGRO = "peligro"
    OBRAS = "obras"
    POLICIA = "policia"
    CIERRE = "cierre"
    OTRO = "otro"

class Gravedad(str, Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"

class Ubicacion(BaseModel):
    """Modelo para coordenadas geográficas estandarizadas"""
    longitud: float = Field(..., alias="x")
    latitud: float = Field(..., alias="y")

class EventoWazeRaw(BaseModel):
    """
    Modelo para validar la estructura de datos crudos de Waze antes de procesarlos.
    Todos los campos son opcionales excepto los esenciales para la estandarización.
    """
    uuid: str
    type: str
    subtype: Optional[str] = None
    city: Optional[str] = None
    street: Optional[str] = "Desconocido"
    location: dict
    pubMillis: int
    confidence: Optional[int] = 1
    reliability: Optional[int] = 1
    nThumbsUp: Optional[int] = 0
    nComments: Optional[int] = 0
    
    # Campos adicionales de Waze (opcionales)
    country: Optional[str] = None
    speed: Optional[int] = None
    roadType: Optional[int] = None
    inscale: Optional[bool] = None
    nearBy: Optional[str] = None
    provider: Optional[str] = None
    providerId: Optional[str] = None

    @validator('location')
    def validate_location(cls, value):
        """Valida que location tenga las coordenadas x e y"""
        if 'x' not in value or 'y' not in value:
            raise ValueError("Location debe contener x e y")
        return value

    @property
    def fecha_evento(self) -> datetime:
        """Convierte milisegundos a datetime"""
        return datetime.fromtimestamp(self.pubMillis / 1000)

class EventoEstandar(BaseModel):
    """
    Modelo para datos estandarizados que se almacenarán en MongoDB.
    Todos los campos son requeridos excepto donde se indique.
    """
    id_evento: str = Field(..., description="UUID del evento de Waze")
    tipo: TipoEvento = Field(..., description="Tipo estandarizado del evento")
    subtipo: Optional[str] = Field(None, description="Subtipo original de Waze")
    comuna: str = Field(..., description="Nombre de la comuna estandarizado")
    calle: str = Field(..., description="Nombre de la calle")
    ubicacion: Ubicacion = Field(..., description="Coordenadas estandarizadas")
    fecha: datetime = Field(..., description="Fecha del evento")
    gravedad: Gravedad = Field(..., description="Nivel de gravedad calculado")
    confirmaciones: int = Field(0, description="Número de confirmaciones (nThumbsUp)")
    comentarios: int = Field(0, description="Número de comentarios (nComments)")
    raw_data: dict = Field(..., description="Datos crudos originales de Waze")
    comentarios: int = Field(default=0, description="Número de comentarios (nComments)")

    @validator('comentarios', pre=True)
    def handle_none_comments(cls, value):
        """Convierte None a 0 para el campo comentarios"""
        return value if value is not None else 0

    @classmethod
    def from_waze_event(cls, data: dict):
        """
        Transforma un evento crudo de Waze al formato estandarizado.
        
        Args:
            data: Diccionario con datos crudos de Waze
            
        Returns:
            EventoEstandar: Evento procesado y validado
        """
        # Validar primero los datos crudos
        waze_event = EventoWazeRaw(**data)
        
        # Determinar el tipo estandarizado
        tipo = cls._determinar_tipo(waze_event.type, waze_event.subtype)
        
        # Calcular gravedad
        gravedad = cls._calcular_gravedad(waze_event.confidence, waze_event.reliability)
        
        # Normalizar nombre de comuna
        comuna = cls._normalizar_comuna(waze_event.city)
        
        return cls(
            id_evento=waze_event.uuid,
            tipo=tipo,
            subtipo=waze_event.subtype,
            comuna=comuna,
            calle=waze_event.street,
            ubicacion=Ubicacion(**waze_event.location),
            fecha=waze_event.fecha_evento,
            gravedad=gravedad,
            confirmaciones=waze_event.nThumbsUp,
            comentarios=waze_event.nComments,
            raw_data=data  # Conservamos todos los datos originales
        )

    @staticmethod
    def _determinar_tipo(tipo_waze: str, subtipo_waze: Optional[str]) -> TipoEvento:
        """Mapea los tipos de Waze a nuestros tipos estandarizados"""
        tipo_waze = tipo_waze.upper() if tipo_waze else ""
        subtipo_waze = subtipo_waze.upper() if subtipo_waze else ""
        
        mapeo = {
            "ACCIDENT": TipoEvento.ACCIDENTE,
            "JAM": TipoEvento.CONGESTION,
            "ROAD_CLOSED": TipoEvento.CIERRE,
            "POLICE": TipoEvento.POLICIA,
            "HAZARD": {
                "HAZARD_ON_ROAD_POT_HOLE": TipoEvento.OBRAS,
                "HAZARD_ON_ROAD_LANE_CLOSED": TipoEvento.OBRAS,
                "HAZARD_ON_ROAD_CONSTRUCTION": TipoEvento.OBRAS,
                "HAZARD_ON_ROAD_OBJECT": TipoEvento.PELIGRO,
                "HAZARD_ON_SHOULDER_CAR_STOPPED": TipoEvento.PELIGRO,
                "HAZARD_ON_ROAD_TRAFFIC_LIGHT_FAULT": TipoEvento.PELIGRO
            }
        }
        
        if tipo_waze in mapeo:
            if isinstance(mapeo[tipo_waze], dict):
                return mapeo[tipo_waze].get(subtipo_waze, TipoEvento.PELIGRO)
            return mapeo[tipo_waze]
        return TipoEvento.OTRO

    @staticmethod
    def _calcular_gravedad(confianza: int, fiabilidad: int) -> Gravedad:
        """Determina la gravedad basada en confianza y fiabilidad"""
        score = confianza * fiabilidad
        if score > 60:
            return Gravedad.ALTA
        if score > 30:
            return Gravedad.MEDIA
        return Gravedad.BAJA

    @staticmethod
    def _normalizar_comuna(nombre_comuna: Optional[str]) -> str:
        """Estandariza el nombre de la comuna"""
        if not nombre_comuna or nombre_comuna.strip() == "":
            return "Desconocido"
        
        nombre = nombre_comuna.strip().title()
        
        # Correcciones específicas para nombres de comunas
        correcciones = {
            "Santiago Centro": "Santiago",
            "Providencia": "Providencia",
            "Las Condes": "Las Condes",
            "Nuñoa": "Ñuñoa"
        }
        
        return correcciones.get(nombre, nombre)