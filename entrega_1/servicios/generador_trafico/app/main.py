import requests
import time
import random
from distribuciones import generar_intervalo

CACHE_URL = "http://cache:8001/eventos"  # URL del servicio cache
ALMACENAMIENTO_URL ="http://almacenamiento:8000/eventos/getall_ids"

def generar_trafico():
    # IDs de ejemplo (deberías obtenerlos de tu BD o generar aleatorios)
    lista_ids = requests.get(ALMACENAMIENTO_URL)
    print(lista_ids)
    sample_ids = ["id1", "id2", "id3", "id4", "id5"]
    
    while True:
        id_consulta = random.choice(sample_ids)
        try:
            response = requests.get(f"{CACHE_URL}/{id_consulta}")
            print(f"Consulta ID: {id_consulta} - Fuente: {response.json()['source']}")
        except Exception as e:
            print(f"Error: {e}")
        
        intervalo = generar_intervalo()
        time.sleep(intervalo)

if __name__ == "__main__":
    generar_trafico()