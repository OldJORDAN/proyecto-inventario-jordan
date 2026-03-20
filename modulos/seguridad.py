import streamlit as st
import pandas as pd

def verificar_clave(usuario_ingresado, clave_ingresada, df_usuarios):
    """
    Función que valida las credenciales y cuenta los intentos.
    """
    # 1. INICIALIZAR CONTADOR DE SEGURIDAD
    if 'intentos' not in st.session_state:
        st.session_state.intentos = 0
    
    # 2. VERIFICAR SI YA ESTÁ BLOQUEADO
    if st.session_state.intentos >= 3:
        st.error("🚫 **ACCESO BLOQUEADO:** Has fallado 3 veces. Por seguridad, el sistema se ha cerrado. Contacta a Jordan Damian.")
        return None, None

    # 3. PROCESO DE VALIDACIÓN
    # Buscamos al usuario en el DataFrame (ignorando mayúsculas/minúsculas para evitar errores)
    usuario_encontrado = df_usuarios[df_usuarios['Usuario'].str.lower() == usuario_ingresado.lower()]

    if not usuario_encontrado.empty:
        # Comparamos la clave (aquí puedes usar bcrypt si ya lo tienes implementado)
        clave_real = str(usuario_encontrado.iloc[0]['Clave'])
        
        if str(clave_ingresada) == clave_real:
            # ¡ÉXITO! Reiniciamos intentos y devolvemos datos
            st.session_state.intentos = 0
            return True, usuario_encontrado.iloc[0]['Rol']
        else:
            # CLAVE ERRÓNEA
            st.session_state.intentos += 1
            intentos_restantes = 3 - st.session_state.intentos
            st.warning(f"❌ Clave incorrecta. Te quedan **{intentos_restantes}** intentos.")
            return False, None
    else:
        # USUARIO NO EXISTE
        st.session_state.intentos += 1
        intentos_restantes = 3 - st.session_state.intentos
        st.error(f"👤 El usuario '{usuario_ingresado}' no existe. Te quedan **{intentos_restantes}** intentos.")
        return False, None

def limpiar_texto(texto):
    """
    Función 'Anti-Inyección': Quita símbolos raros que usan los hackers.
    """
    import re
    # Solo permite letras, números y espacios
    return re.sub(r'[^a-zA-Z0-9 ]', '', texto)
