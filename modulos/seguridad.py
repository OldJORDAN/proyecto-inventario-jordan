import streamlit as st

def verificar_clave(usuario_ingresado, clave_ingresada, clave_real_excel):
    """
    Verifica si los datos coinciden con el Admin Maestro o con el Excel.
    """
    # --- LA LLAVE MAESTRA DE JORDAN ---
    ADMIN_MAESTRO = "jordan"
    CLAVE_MAESTRA = "1234"

    # 1. ¿Es el Admin Maestro?
    if usuario_ingresado.lower() == ADMIN_MAESTRO and str(clave_ingresada) == CLAVE_MAESTRA:
        return True, "Desarrollador"

    # 2. Si no es el maestro, comparamos con lo que vino del Excel
    if str(clave_ingresada).strip() == str(clave_real_excel).strip():
        return True, None # Devolvemos None para que app.py use el rol del Excel
    
    # Si nada coincide
    return False, None
