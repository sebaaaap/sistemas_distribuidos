from playwright.sync_api import sync_playwright
import json
import time
import os
import random
import requests

MAX_EVENTOS = 50000
PIXEL_MOVIMIENTO = 100

URL_ALMACENAMIENTO = os.getenv("URL_ALMACENAMIENTO", "http://localhost:8000/eventos")

eventos_acumulados = []
uuids_vistos = set()

def enviar_evento(evento):
    try:
        response = requests.post(URL_ALMACENAMIENTO, json=evento)
        response.raise_for_status()
        print(f"Evento {evento.get('uuid')} enviado.")
    except Exception as e:
        print(f"Error al enviar evento {evento.get('uuid')}: {e}")
        print(evento)

def procesar_eventos(data):    
    global eventos_acumulados, uuids_vistos

    alerts = data.get("alerts", [])

    nuevos = 0
    for evento in alerts:
        uuid = evento.get("uuid")
        if uuid and uuid not in uuids_vistos:
            eventos_acumulados.append(evento)
            uuids_vistos.add(uuid)
            nuevos += 1
            enviar_evento(evento)
    return nuevos

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        def handle_response(response):
            if "georss" in response.url and response.status == 200:
                try:
                    data = response.json()
                    nuevos = procesar_eventos(data)
                    print(f"Capturados {nuevos} nuevos eventos. Total: {len(eventos_acumulados)}")
                except Exception as e:
                    print(f"Error procesando respuesta: {e}")

        page.on("response", handle_response)

        print("Abriendo Waze Live Map...")
        page.goto("https://www.waze.com/es-419/live-map/")

        try:
            page.wait_for_selector("//button[contains(text(), 'Entendido')]", timeout=15000)
            page.locator("//button[contains(text(), 'Entendido')]").click()
            print("Ventana emergente cerrada.")
        except Exception as e:
            print(f"No se detectó ventana emergente: {e}")

        print("Página actual:", page.url)
        try:
            title = page.title()
            print("Título de la página:", title)
        except Exception as e:
            print("No se pudo obtener el título:", e)

        try:
            screenshot_path = "waze_screenshot.png"
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"Screenshot tomada y guardada como {screenshot_path}")
        except Exception as e:
            print(f"Error al tomar screenshot: {e}")

        time.sleep(10)

        center_x, center_y = 600, 300

        while len(eventos_acumulados) < MAX_EVENTOS:
            movimientos = [
                ("derecha", center_x, center_y, center_x - PIXEL_MOVIMIENTO, center_y),
                ("abajo", center_x, center_y, center_x, center_y + PIXEL_MOVIMIENTO),
                ("izquierda", center_x, center_y, center_x + PIXEL_MOVIMIENTO, center_y),
                ("arriba", center_x, center_y, center_x, center_y - PIXEL_MOVIMIENTO),
            ]

            for direccion, x1, y1, x2, y2 in movimientos:
                if len(eventos_acumulados) >= MAX_EVENTOS:
                    break

                print(f"Moviendo mapa hacia {direccion}...")
                page.mouse.move(x1, y1)
                page.mouse.down()
                page.mouse.move(x2, y2, steps=10)
                page.mouse.up()

                espera = random.uniform(5, 12)
                print(f"Esperando {espera:.2f} segundos antes del siguiente movimiento...")
                time.sleep(espera)

        with open("eventos_acumulados.json", "w", encoding="utf-8") as f:
            json.dump({"alerts": eventos_acumulados}, f, indent=2, ensure_ascii=False)

        print(f"Proceso terminado. Se guardaron {len(eventos_acumulados)} eventos.")
        browser.close()

if __name__ == "__main__":
    main()
