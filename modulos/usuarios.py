import streamlit as st
import pandas as pd

def mostrar(df_usuarios, guardar_global, df_inv, df_mov, df_mant, df_lug, df_papelera):
    st.title("👥 Gestión de Usuarios y Licencias")

    # --- CONFIGURACIÓN DE SEGURIDAD DE JORDAN ---
    # Este es tu "seguro" interno. Aunque cambien el Excel, 
    # el sistema NO pasará de este número sin que TÚ cambies el código.
    MAXIMO_PERMITIDO_POR_CODIGO = 60 
    
    try:
        df_config = pd.read_excel("database.xlsx", sheet_name="Configuracion")
        valor_excel = int(df_config.loc[df_config['Parametro'] == 'Limite_Usuarios', 'Valor'].values[0])
        
        # SI EL EXCEL DICE MÁS DE LO PERMITIDO, SE QUEDA EN EL MÁXIMO DE JORDAN
        if valor_excel > MAXIMO_PERMITIDO_POR_CODIGO:
            limite_licencias = MAXIMO_PERMITIDO_POR_CODIGO
            st.warning("⚠️ Se detectó una inconsistencia en las licencias. Contacte al desarrollador.")
        else:
            limite_licencias = valor_excel
            
    except Exception:
        # Si borran la hoja o el Excel falla, el sistema se bloquea en 5 por seguridad
        limite_licencias = 5

    usuarios_actuales = len(df_usuarios)

    # --- INTERFAZ VISUAL ---
    st.subheader("📊 Estado del Plan de Licencias")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        progreso = min(usuarios_actuales / limite_licencias, 1.0)
        st.progress(progreso)
    with col2:
        st.write(f"**{usuarios_actuales} / {limite_licencias}**")

    # --- LÓGICA DEL CANDADO ---
    if usuarios_actuales >= limite_licencias:
        st.error(f"🚫 **LÍMITE ALCANZADO:** Has llegado al máximo de {limite_licencias} usuarios. Contacta a Jordan Damian para ampliar tu plan.")
        st.info("💡 Consejo: Elimina usuarios antiguos o solicita una extensión de licencia.")
    else:
        st.success(f"✅ Cupo disponible: {limite_licencias - usuarios_actuales} licencias.")
        
        with st.expander("➕ Registrar Nuevo Personal"):
            with st.form("nuevo_usuario_form"):
                nombre_u = st.text_input("Nombre y Apellido")
                id_u = st.text_input("ID de Acceso (Usuario)")
                clave_u = st.text_input("Clave Temporal", type="password")
                rol_u = st.selectbox("Rol", ["Operador", "Supervisor", "Administrador"])
                
                enviar = st.form_submit_button("Guardar Registro")
                if enviar:
                    if nombre_u and id_u and clave_u:
                        # Aquí llamas a tu función que guarda en el Excel
                        st.info("Guardando en base de datos...")
                    else:
                        st.warning("Todos los campos son obligatorios.")

    st.divider()
    
    # --- LISTA DE USUARIOS ---
    st.subheader("📋 Personal con Acceso")
    st.dataframe(df_usuarios[['Usuario', 'Rol']], use_container_width=True)
