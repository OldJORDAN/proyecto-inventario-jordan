import streamlit as st
import pandas as pd

def mostrar(df_usuarios, guardar_callback, df_inv, df_mov, df_mant, df_lug, df_papelera):
    st.title("👥 Gestión de Usuarios y Licencias")

    # --- 1. CARGAR LÍMITE DESDE EXCEL ---
    try:
        df_config = pd.read_excel("database.xlsx", sheet_name="Configuracion")
        # Buscamos el valor donde el parámetro sea 'Limite_Usuarios'
        limite_licencias = int(df_config.loc[df_config['Parametro'] == 'Limite_Usuarios', 'Valor'].values[0])
    except Exception:
        limite_licencias = 10  # Por si acaso el Excel falla, le damos 10

    usuarios_actuales = len(df_usuarios)

    # --- 2. BARRA DE ESTADO PROFESIONAL ---
    st.subheader("📊 Estado del Plan Actual")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        progreso = min(usuarios_actuales / limite_licencias, 1.0)
        st.progress(progreso)
    with col2:
        st.write(f"**{usuarios_actuales} / {limite_licencias}**")

    # Alerta si ya no hay cupos
    if usuarios_actuales >= limite_licencias:
        st.error(f"🚫 **Límite de {limite_licencias} licencias alcanzado.** No es posible registrar más personal. Contacta a Jordan Damian para ampliar tu plan de soporte.")
    else:
        st.success(f"✅ Tienes cupo disponible para {limite_licencias - usuarios_actuales} usuarios más.")

    st.divider()

    # --- 3. FORMULARIO DE REGISTRO (SOLO SI HAY CUPO) ---
    if usuarios_actuales < limite_licencias:
        with st.expander("➕ Registrar Nuevo Usuario"):
            with st.form("form_nuevo_usuario"):
                nombre = st.text_input("Nombre Completo")
                user = st.text_input("ID de Usuario (Login)")
                clave = st.text_input("Contraseña Temporaria", type="password")
                rol = st.selectbox("Rol del Sistema", ["Operador", "Supervisor", "Administrador"])
                
                if st.form_submit_button("Confirmar Registro"):
                    if nombre and user and clave:
                        # Aquí iría tu lógica de guardado normal
                        # (Suponiendo que tienes una función para encriptar y guardar)
                        st.info("Procesando registro...")
                        # NOTA: Aquí debes llamar a tu función de guardado habitual
                    else:
                        st.warning("Por favor llena todos los campos.")
    
    # --- 4. LISTA DE USUARIOS ACTIVOS ---
    st.subheader("📋 Usuarios en el Sistema")
    st.dataframe(df_usuarios[['Usuario', 'Rol']], use_container_width=True)
