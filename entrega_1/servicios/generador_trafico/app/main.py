import requests
import time
import random
from datetime import datetime, timedelta
import json
import argparse
from collections import defaultdict
import os
import glob

# Configuración de URLs (selección automática según entorno)
CACHE_URL = os.getenv('CACHE_URL', "http://cache:8001/eventos")
ALMACENAMIENTO_URL = os.getenv('ALMACENAMIENTO_URL', "http://almacenamiento:8000/eventos/getall_ids")

# Configuración de parámetros
MIN_IDS = int(os.getenv('MIN_IDS', 1))  # Usar 10000 en producción
DURACION_DEFAULT = int(os.getenv('DURACION_MINUTOS', 0))  # 0=infinito

def limpiar_archivos_anteriores():
    """Elimina archivos JSON de estadísticas anteriores"""
    for f in glob.glob('estadisticas_*.json') + glob.glob('metricas_*.json'):
        try:
            os.remove(f)
            print(f"♻️ Eliminado archivo anterior: {f}")
        except Exception as e:
            print(f"⚠️ No se pudo eliminar {f}: {str(e)}")

def parse_args():
    """Analiza los argumentos de línea de comandos con valor por defecto desde variables de entorno"""
    parser = argparse.ArgumentParser(description='Generador de tráfico para pruebas de cache')
    default_duration = int(os.getenv('DURACION_MINUTOS', '15'))  # Valor por defecto 15
    parser.add_argument('--duracion', 
                       type=int, 
                       default=default_duration,
                       help=f'Duración en minutos (default: {default_duration})')
    return parser.parse_args()


def esperar_ids_suficientes():
    """Espera hasta que haya al menos MIN_IDS disponibles"""
    print(f"\n🔍 Buscando al menos {MIN_IDS} ID(s)...")
    while True:
        try:
            response = requests.get(ALMACENAMIENTO_URL, timeout=5)
            if response.status_code == 200:
                data = response.json()
                ids = data.get("ids", [])
                if len(ids) >= MIN_IDS:
                    print(f"✅ IDs suficientes ({len(ids)}/{MIN_IDS}) encontrados")
                    return ids
                print(f"🔄 Esperando IDs... ({len(ids)}/{MIN_IDS})")
            else:
                print(f"⚠️ Error HTTP {response.status_code} al obtener IDs")
        except Exception as e:
            print(f"❌ Error de conexión: {str(e)}")
        time.sleep(5)

def generar_intervalo():
    """Genera un intervalo aleatorio entre consultas (0.1-1.0 segundos)"""
    return random.uniform(0.1, 1.0)

def guardar_metricas(estadisticas, metricas_ids):
    """Guarda todas las métricas en archivos JSON con timestamp"""
    stats_dir = '/app/estadisticas'
    os.makedirs(stats_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Archivo de estadísticas generales
    archivo_estadisticas = f"{stats_dir}/estadisticas_generales_{timestamp}.json"
    with open(archivo_estadisticas, 'w') as f:
        json.dump(estadisticas, f, indent=2)
    print(f"📊 Estadísticas generales guardadas en '{archivo_estadisticas}'")
    
    # Archivo de métricas detalladas por ID
    archivo_metricas = f"{stats_dir}/metricas_ids_{timestamp}.json"

    with open(archivo_metricas, 'w') as f:
     json.dump({
        'ids_mas_consultados': sorted(
            [{
                'id': k, 
                'total': v,
                'cache_hits': metricas_ids['fuentes_por_id'][k]['CACHE'],
                'cache_misses': metricas_ids['fuentes_por_id'][k]['BACKEND'],
                'primer_uso': metricas_ids['timestamp_primer_uso'].get(k),
                'ultimo_uso': metricas_ids['timestamp_ultimo_uso'].get(k),
                'ratio_cache': metricas_ids['fuentes_por_id'][k]['CACHE'] / v if v > 0 else 0
            } for k, v in metricas_ids['conteo_por_id'].items()],
            key=lambda x: x['total'], reverse=True),
        'resumen': {
            'total_ids_unicos': len(metricas_ids['conteo_por_id']),
            'promedio_consultas_por_id': (
                estadisticas['total_consultas'] / len(metricas_ids['conteo_por_id']) 
                if metricas_ids['conteo_por_id'] else 0
            ),
            'tiempo_ejecucion_minutos': estadisticas['config']['duracion_minutos'],
            'cache_hit_global': (
                estadisticas['cache_hits'] / estadisticas['total_consultas'] 
                if estadisticas['total_consultas'] > 0 else 0
            )
        }
    }, f, indent=2)
    
    print(f"📈 Métricas por ID guardadas en '{archivo_metricas}'")
          
def mostrar_resumen(estadisticas, metricas_ids):
    """Muestra un resumen completo de las estadísticas"""
    print("\n" + "="*50)
    print("📊 RESUMEN FINAL DE ESTADÍSTICAS".center(50))
    print("="*50)
    
    print(f"\n⏱ Duración configurada: {estadisticas['config']['duracion_minutos']} minutos")
    print(f"🆔 IDs mínimos requeridos: {estadisticas['config']['min_ids']}")
    print(f"🔢 Total consultas: {estadisticas['total_consultas']}")
    
    if estadisticas['total_consultas'] > 0:
        print(f"\n💾 Cache hits: {estadisticas['cache_hits']} ({estadisticas['cache_hits']/estadisticas['total_consultas']:.2%})")
        print(f"❌ Cache misses: {estadisticas['cache_misses']} ({estadisticas['cache_misses']/estadisticas['total_consultas']:.2%})")
    
    print(f"\n🔍 IDs únicos consultados: {len(metricas_ids['conteo_por_id'])}")
    if metricas_ids['conteo_por_id']:
        id_mas, count_mas = max(metricas_ids['conteo_por_id'].items(), key=lambda x: x[1])
        id_menos, count_menos = min(metricas_ids['conteo_por_id'].items(), key=lambda x: x[1])
        print(f"\n🏆 ID más consultado: {id_mas} (veces: {count_mas})")
        print(f"🔻 ID menos consultado: {id_menos} (veces: {count_menos})")
        print(f"📊 Promedio consultas/ID: {estadisticas['total_consultas']/len(metricas_ids['conteo_por_id']):.2f}")

def generar_trafico(duracion_minutos=DURACION_DEFAULT):
    """Ejecuta el generador de tráfico con el tiempo especificado"""
    limpiar_archivos_anteriores()
    
    # Inicializar estructuras de datos
    estadisticas = {
        'total_consultas': 0,
        'cache_hits': 0,
        'cache_misses': 0,
        'config': {
            'duracion_minutos': duracion_minutos,
            'min_ids': MIN_IDS,
            'cache_url': CACHE_URL,
            'almacenamiento_url': ALMACENAMIENTO_URL
        }
    }
    
    metricas_ids = {
        'conteo_por_id': defaultdict(int),
        'fuentes_por_id': defaultdict(lambda: {'CACHE': 0, 'BACKEND': 0}),
        'timestamp_primer_uso': {},
        'timestamp_ultimo_uso': {}
    }
    
    # Configurar tiempo de ejecución
    hora_fin = datetime.now() + timedelta(minutes=duracion_minutos) if duracion_minutos > 0 else None
    sample_ids = esperar_ids_suficientes()
    
    print(f"\n🚀 Iniciando generador ({duracion_minutos} min) | IDs disponibles: {len(sample_ids)}")
    print(f"⏰ Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if hora_fin:
        print(f"⏳ Fin estimado: {hora_fin.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        while not hora_fin or datetime.now() < hora_fin:
            id_consulta = random.choice(sample_ids)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            try:
                # Consultar al servicio de cache
                response = requests.get(f"{CACHE_URL}/{id_consulta}", timeout=3)
                respuesta = response.json()
                
                # Determinar fuente y actualizar estadísticas
                fuente = respuesta.get('message', '').lower()
                tipo = 'CACHE' if 'cache' in fuente else 'BACKEND'
                estadisticas['total_consultas'] += 1
                estadisticas['cache_hits' if tipo == 'CACHE' else 'cache_misses'] += 1
                
                # Actualizar métricas por ID
                metricas_ids['conteo_por_id'][id_consulta] += 1
                metricas_ids['fuentes_por_id'][id_consulta][tipo] += 1
                if id_consulta not in metricas_ids['timestamp_primer_uso']:
                    metricas_ids['timestamp_primer_uso'][id_consulta] = timestamp
                metricas_ids['timestamp_ultimo_uso'][id_consulta] = timestamp
                
                # Mostrar progreso
                if hora_fin:
                    tiempo_restante = (hora_fin - datetime.now()).total_seconds() / 60
                    print(f"[{timestamp}] ID: {id_consulta} | Fuente: {tipo} | Restante: {tiempo_restante:.1f} min")
                else:
                    print(f"[{timestamp}] ID: {id_consulta} | Fuente: {tipo}")
                
                # Reporte periódico
                if estadisticas['total_consultas'] % 100 == 0:
                    print(f"\n📈 Consultas: {estadisticas['total_consultas']} | "
                          f"Cache: {estadisticas['cache_hits']} ({estadisticas['cache_hits']/estadisticas['total_consultas']:.1%}) | "
                          f"IDs únicos: {len(metricas_ids['conteo_por_id'])}")
                
            except Exception as e:
                print(f"[{timestamp}] ❌ Error con ID {id_consulta}: {str(e)}")
            
            time.sleep(generar_intervalo())
            
    except KeyboardInterrupt:
        print("\n🛑 Detención manual solicitada")
    finally:
        guardar_metricas(estadisticas, metricas_ids)
        mostrar_resumen(estadisticas, metricas_ids)

if __name__ == "__main__":
    args = parse_args()
    generar_trafico(duracion_minutos=args.duracion)