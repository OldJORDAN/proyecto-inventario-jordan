import streamlit as st

def verificar_clave(usuario_ingresado, clave_ingresada, clave_real_excel):
    # LLAVE MAESTRA
    ADMIN_MAESTRO = "jordan"
    CLAVE_MAESTRA = "1234"

    if usuario_ingresado.lower() == ADMIN_MAESTRO and str(clave_ingresada) == CLAVE_MAESTRA:
        return True, "Desarrollador"

    # Comparación normal con Excel
    ingresada = str(clave_ingresada).strip()
    real = str(clave_real_excel).strip()
    
    if real.endswith('.0'): real = real[:-2]
    
    if ingresada == real:
        return True, None
    
    return False, None
