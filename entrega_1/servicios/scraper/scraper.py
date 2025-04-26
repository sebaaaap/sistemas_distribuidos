import json
import time
import requests
from datetime import datetime
import os

# Configuración
URL = "https://www.waze.com/live-map/api/georss?top=-33.3&bottom=-33.7&left=-70.95&right=-70.35&env=row&types=alerts,traffic"
INTERVALO_NORMAL = 15  # segundos entre ciclos
PAUSA_EXTRA = 10       # pausa cada 100 eventos nuevos

# Configuración de URLs (selección automática según entorno)
URL_MONGODB = os.getenv('URL_MONGODB', "http://cache:8001/eventos")
MAX_EVENTOS = int(os.getenv('MAX_EVENTOS', 10))  # ✅ Cambiado de 10 a 10.000


# Claves innecesarias
keys_to_remove = [
    "comments", "reportDescription", "nThumbsUp", "reportBy",
    "reportByMunicipalityUser", "reportRating", "reportMood",
    "fromNodeId", "toNodeId", "magvar", "additionalInfo", "wazeData"
]

# Lista de eventos válidos
eventos_totales = []

def remove_keys_from_dict(data, keys_to_remove):
    if isinstance(data, list):
        for item in data:
            remove_keys_from_dict(item, keys_to_remove)
    elif isinstance(data, dict):
        for key in keys_to_remove:
            if key in data:
                del data[key]
        for key in data:
            if isinstance(data[key], (dict, list)):
                remove_keys_from_dict(data[key], keys_to_remove)

def esta_en_region_metropolitana(location):
    if not location:
        return False
    lat = location.get("y")
    lon = location.get("x")
    return (
        lat is not None and lon is not None and
        -33.75 <= lat <= -33.2 and
        -70.95 <= lon <= -70.35
    )

def scrape_waze_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        remove_keys_from_dict(data, keys_to_remove)
        return data
    except Exception as e:
        print(f"❌ Error al obtener datos: {e}")
        return {}

def preparar_evento(evento_waze):
    campos_permitidos = {
        "id", "uuid", "country", "city", "street", "location",
        "type", "subtype", "speed", "roadType", "inscale",
        "confidence", "reliability", "pubMillis"
    }
    return {k: v for k, v in evento_waze.items() if k in campos_permitidos}

def enviar_a_mongodb(evento_waze):
    try:
        evento_limpio = preparar_evento(evento_waze)
        response = requests.post(
            URL_MONGODB,
            json=evento_limpio,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        print(f"✅ Evento {evento_waze.get('uuid')} enviado correctamente")
    except Exception as e:
        print(f"❌ Error al enviar evento: {e}")

def main():
    print(f"[{datetime.now()}] Iniciando scraper para la Región Metropolitana...")
    seen_ids = set()
    acumulador_nuevos = 0

    while len(eventos_totales) < MAX_EVENTOS:
        data = scrape_waze_data(URL)
        nuevos = 0

        for item in data.get("alerts", []) + data.get("jams", []):
            uid = item.get("uuid")
            location = item.get("location")
            if uid and uid not in seen_ids and esta_en_region_metropolitana(location):
                eventos_totales.append(item)
                seen_ids.add(uid)
                nuevos += 1
                acumulador_nuevos += 1

                # Enviar cada evento a MongoDB
                enviar_a_mongodb(item)

                if len(eventos_totales) >= MAX_EVENTOS:
                    break

        print(f"🔄 Ciclo: {len(eventos_totales)} eventos totales (nuevos en este ciclo: {nuevos})")

        if len(eventos_totales) >= MAX_EVENTOS:
            break

        # Pausa condicional
        if acumulador_nuevos >= 100:
            print(f"⏸ Pausa adicional de {PAUSA_EXTRA} segundos (cada 100 nuevos eventos)...")
            time.sleep(PAUSA_EXTRA)
            acumulador_nuevos = 0
        else:
            time.sleep(INTERVALO_NORMAL)

    # Guardar en archivo JSON (opcional, como backup)
    with open("eventos.json", "w", encoding="utf-8") as f:
        json.dump(eventos_totales, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Finalizado. {len(eventos_totales)} eventos procesados.")


if __name__ == "__main__":
    main()
