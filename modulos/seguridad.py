import streamlit as st

def verificar_clave(clave_ingresada, clave_real):
    """
    Compara la clave ingresada contra la del Excel.
    Forzamos a que ambas sean texto y quitamos espacios.
    """
    try:
        # Convertimos a string y quitamos espacios invisibles
        ingresada = str(clave_ingresada).strip()
        real = str(clave_real).strip()
        
        # Si en Excel el 1234 se guardó como "1234.0", esto lo limpia
        if real.endswith('.0'):
            real = real[:-2]
            
        return ingresada == real
    except:
        return False

def limpiar_texto_seguro(texto):
    """
    Solo quita espacios a los lados para no dañar el usuario real.
    """
    if not texto:
        return ""
    return str(texto).strip()
