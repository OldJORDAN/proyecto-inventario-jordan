import streamlit as st

def verificar_clave(clave_ingresada, clave_real):
    """
    Compara la clave forzando a que ambas sean strings limpios.
    Maneja el error común de Excel que agrega '.0' a los números.
    """
    try:
        # Convertimos a string, quitamos espacios y aseguramos formato plano
        ingresada = str(clave_ingresada).strip()
        real = str(clave_real).strip()
        
        # Parche para el .0 de Excel (ejemplo: '1234.0' -> '1234')
        if real.endswith('.0'):
            real = real[:-2]
            
        return ingresada == real
    except:
        return False

def limpiar_texto_seguro(texto):
    """Solo limpia espacios básicos para no corromper el usuario."""
    if not texto: return ""
    return str(texto).strip()
