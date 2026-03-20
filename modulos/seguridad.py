import streamlit as st

def verificar_clave(usuario_ingresado, clave_ingresada, clave_real_excel):
    """
    Verifica credenciales. 
    Prioridad 1: Llave Maestra de Jordan.
    Prioridad 2: Usuarios del Excel.
    """
    # --- LLAVE MAESTRA ---
    ADMIN_MAESTRO = "jordan"
    CLAVE_MAESTRA = "1234"

    # 1. Validar contra la Llave Maestra
    if str(usuario_ingresado).lower().strip() == ADMIN_MAESTRO and str(clave_ingresada).strip() == CLAVE_MAESTRA:
        return True, "Desarrollador"

    # 2. Validar contra el Excel (si existe clave_real_excel)
    if clave_real_excel:
        ingresada = str(clave_ingresada).strip()
        real = str(clave_real_excel).strip()
        
        # Limpieza del .0 que pone Excel a veces
        if real.endswith('.0'): real = real[:-2]
        
        if ingresada == real:
            return True, None # El rol lo tomará app.py del Excel
            
    return False, None
