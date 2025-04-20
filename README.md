# Trabajo semestral 🗿


## 📋 Requisitos
- Python 3.8+
- Docker

## 🚄 Para probar rapido
1. **Clonar el repositorio**:
   ```bash

   git clone https://github.com/sebaaaap/sistemas_distribuidos.git
   ```
2. **Construir y levantar servicios**:
   - importante estar en el directororio del compose.yml
    ```bash
    cd sistemas_distribuidos/entrega_1/servicios

    docker compose up --build
    ```
3. **Probar almacenamiento**:
    - Esto retorna el id del evento
    ```bash
    curl -X POST http://localhost:8000/eventos/-H "Content-Type: application/json"-d '{
    "id": "alert-123",
    "uuid": "f35d4177-ca17-4644-a20f-e3425d651178",
    "country": "CI",
    "city": "Malloco",
    "street": "Los Aromos",
    "location": {"x": -70.876047, "y": -33.614422},
    "type": "ROAD_CLOSED",
    "subtype": "ROAD_CLOSED_EVENT",
    "speed": 0,
    "roadType": 1,
    "inscale": false,
    "confidence": 0,
    "reliability": 6,
    "pubMillis": 1744739082000
    }'
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
--
## 🛠️ Para meter mano 

1. **Crear un entorno virtual (recomendado)**:
   ```bash
   python -m venv venv        # Crea entorno, puede ser igual con: python3 -m venv venv
   source venv/bin/activate    # Activar (Linux/Mac)
   venv\Scripts\activate      # Activar (Windows)
   ```
2. **Entrar al entorno**:
   ```bash
    cd venv
   ```
3. **Clonar el repositorio**:
   ```bash

   git clone https://github.com/sebaaaap/sistemas_distribuidos.git
   cd sistemas_distribuidos
   ```

<!-- 4. **Instalar dependencias de cada servicio(almacenaminto/cache)**:
   ```bash
   pip install -r requirements.txt
   ``` -->

## ▶️ Ejecución

1. calmao

```bash

```