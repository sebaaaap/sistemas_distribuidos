import random
import numpy as np

def generar_intervalo():
  
    #Distribución Poisson 
     #return max(0.1, np.random.poisson(lam=1.5))  # Se asegura que no sea menor a 0.1 segundos

    #Distribución Uniforme 
    return random.uniform(0.5, 3.0)
