# Trabajo semestral :p

---

## 📋 Requisitos
- Python 3.8+
- Docker

---

## 🚄 Para probar rapido
1. **Clonar el repositorio**:
   ```bash

   git clone https://github.com/sebaaaap/sistemas_distribuidos.git
   cd sistemas_distribuidos/entrega_1/servicios
   ```
2. **Construir y levantar servicios**:

    ```bash
    docker compose up --build
    ```
3. **Probar almacenamiento**:
    - Retorna id
    ```bash
    curl -X POST http://localhost:8000/eventos/ -H "Content-Type: application/json" -d '{"tipo": "prueba_atlas", "ubicacion": {"lat": -33.45, "lng": -70.65}}'
    ```
    ```bash
    curl http://localhost:8000/eventos/<NUEVO_ID>
    ```
3. **Probar cache**:
    - colocar id anterior, el q retorna el post
    ```bash
    curl http://localhost:8000/eventos/<NUEVO_ID>
    ```

## 🛠️ Para meter mano 

1. **Crear un entorno virtual (recomendado)**:
   ```bash
   python -m venv venv        # Crea entorno, puede ser igual con: python3 -m venv venv
   source venv/bin/activate    # Activar (Linux/Mac)
   venv\Scripts\activate      # Activar (Windows)
   cd venv
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

4. **Instalar dependencias de cada servicio(almacenaminto/cache)**:
   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ Ejecución

1. calmao

```bash

```