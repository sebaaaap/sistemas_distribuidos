import random
import numpy as np

def generar_intervalo():
    # Ejemplo con dos distribuciones (Poisson y Uniforme)
    distribucion = random.choice(["poisson", "uniform"])
    
    if distribucion == "poisson":
        return np.random.poisson(lam=1.5)  # Lambda ajustable
    else:
        return random.uniform(0.5, 3.0)    # Rango ajustable