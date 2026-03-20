import streamlit as st
import re

def verificar_clave(clave_ingresada, clave_real):
    """
    Compara la clave que escribe el usuario contra la que está guardada en el Excel.
    Se asegura de que ambas sean tratadas como texto para evitar errores de tipo.
    """
    try:
        # Convertimos ambos a string y quitamos espacios en blanco a los lados
        ingresada = str(clave_ingresada).strip()
        real = str(clave_real).strip()
        
        # Retorna True si son iguales, False si no
        return ingresada == real
    except Exception:
        # Si algo falla en la conversión, por seguridad no deja entrar
        return False

def limpiar_texto_seguro(texto):
    """
    Función Anti-Hacker: 
    Elimina cualquier símbolo que no sea letra o número.
    Evita inyecciones de código o scripts maliciosos.
    """
    if not texto:
        return ""
    
    # Esta expresión regular solo deja pasar letras (a-z, A-Z) y números (0-9)
    # Borra puntos, comas, comillas, paréntesis, etc.
    texto_limpio = re.sub(r'[^a-zA-Z0-9]', '', str(texto))
    
    return texto_limpio.lower() # Lo devolvemos en minúsculas para estandarizar
