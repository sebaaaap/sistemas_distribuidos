# Trabajo semestral 🗿


## 📋 Requisitos
- Python 3.8+
- Docker
- Solicitar crendenciales 🥵

## 🚄 Para probar 
1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/sebaaaap/sistemas_distribuidos.git
   ```
2. **Importante estar en el directororio del compose.yml**:
    ```bash
    cd sistemas_distribuidos/entrega_1/servicios
    ```
3. **Crear .env y colocar sus credenciales**
   ```python
   MONGO_USER=
   MONGO_PASSWORD= 
   MONGO_CLUSTER=
   MONGO_DB=       
   MONGO_COLLECTION=
   ```
4. **Levantar servicios**
   ```bash
   docker compose up --build
   ```
5. **Importante**
   - Ir a "generador_trafico/app/estadisticas" para ver estadisticas

   - En la rama "scraper_LM" esta la busqueda de eventos a travès de la API


## 🛠️ Para meter mano 

1. **Ajustar la cantidad de eventos a scrapear(10eventos Default)**:
 - Ir al .yml, ubicar el servicio "scraper" y cambiar valor:
```docker-compose.yml
environment:  
    - MAX_EVENTOS=10  # N° de eventos que deseas scrapear
```
2. **Ajustar politica de remosion(LRU-LFU)**:
 - Ir al .yml, ubicar el servicio "redis" y cambiar valor "lru" por "lfu":
```docker-compose.yml
command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru # allkeys-lfu
```
3. **Ajustar TTL(30min default)**:
 - Ir al .yml, ubicar el servicio "cache" y cambiar valor (1800 -> 30min, 3600 -> 1hra):
```docker-compose.yml
environment:
    - TTL_CACHE=1800
```

4. **Ajustar tiempo del genereador de trafico(1min default)**:
 - Ir al .yml, ubicar el servicio "generador" y cambiar valor:
```docker-compose.yml
command: >
      sh -c "python main.py --duracion 1" 
```



## ▶️ En ejecución
0. **Probar almacenamiento**:
    - Esto retorna el id del evento
    ```bash
    curl -X POST http://localhost:8000/eventos/ -H "Content-Type: application/json" -d '{"id": "alert-123","uuid": "f35d4177-ca17-4644-a20f-e3425d651178","country": "CI","city": "Malloco","street": "Los Aromos","location": {"x": -70.876047, "y": -33.614422},"type": "ROAD_CLOSED","subtype": "ROAD_CLOSED_EVENT","speed": 0,"roadType": 1,"inscale": false,"confidence": 0,"reliability": 6,"pubMillis": 1744739082000
    ```
    - agregale el id mi xan
    ```bash
    curl http://localhost:8000/eventos/<NUEVO_ID>
    ```
3. **Probar cache**:
    - colocar id anterior, fijarse en 'source'
    ```bash
    curl http://localhost:8001/eventos/<NUEVO_ID>
    ```