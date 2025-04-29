import random
import numpy as np

def generar_intervalo():
  
    #Distribución Poisson 
     return max(0.1, np.random.poisson(lam=1.5))  # Se asegura que no sea menor a 0.1 segundos

    #Distribución Uniforme 
    # return random.uniform(0.5, 3.0)
def generar_id_zipf(lista_ids, s=2.0):
    """
    Devuelve un ID de `lista_ids` siguiendo la distribución de Zipf.
    `s` controla el sesgo (mayores valores = más sesgo).
    """
    n = len(lista_ids)
    while True:
        idx = np.random.zipf(s) - 1  # zipf genera valores ≥1
        if idx < n:
            return lista_ids[idx]