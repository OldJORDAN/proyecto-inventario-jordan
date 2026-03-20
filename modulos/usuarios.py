import streamlit as st
import pandas as pd

def mostrar(df_usuarios, guardar_global, df_inv, df_mov, df_mant, df_lug, df_papelera):
    st.title("👥 Gestión de Usuarios y Licencias")

    # --- 1. CONFIGURACIÓN DE SEGURIDAD Y LÍMITES ---
    MAXIMO_PERMITIDO_POR_CODIGO = 60 
    
    try:
        df_config = pd.read_excel("database.xlsx", sheet_name="Configuracion")
        valor_excel = int(df_config.loc[df_config['Parametro'] == 'Limite_Usuarios', 'Valor'].values[0])
        
        if valor_excel > MAXIMO_PERMITIDO_POR_CODIGO:
            limite_licencias = MAXIMO_PERMITIDO_POR_CODIGO
            st.warning("⚠️ Inconsistencia detectada. Se aplica el límite de seguridad de Jordan.")
        else:
            limite_licencias = valor_excel
    except:
        limite_licencias = 5

    usuarios_actuales = len(df_usuarios)

    # --- 2. INTERFAZ VISUAL ---
    st.subheader("📊 Estado del Plan de Licencias")
    col1, col2 = st.columns([3, 1])
    with col1:
        progreso = min(usuarios_actuales / limite_licencias, 1.0)
        st.progress(progreso)
    with col2:
        st.write(f"**{usuarios_actuales} / {limite_licencias}**")

    # --- 3. LÓGICA DEL CANDADO DE REGISTRO ---
    if usuarios_actuales >= limite_licencias:
        st.error(f"🚫 **LÍMITE ALCANZADO:** No puedes registrar más usuarios ({usuarios_actuales}/{limite_licencias}).")
        st.info("💡 Contacta a Jordan Damian para ampliar tu plan de licencias.")
    else:
        st.success(f"✅ Cupo disponible: {limite_licencias - usuarios_actuales} licencias.")
        
        with st.expander("➕ Registrar Nuevo Personal"):
            with st.form("nuevo_usuario_form"):
                nombre_u = st.text_input("Nombre y Apellido")
                id_u = st.text_input("ID de Acceso (Usuario)")
                clave_u = st.text_input("Clave Temporal", type="password")
                rol_u = st.selectbox("Rol", ["Operador", "Supervisor", "Administrador"])
                
                enviar = st.form_submit_button("Confirmar y Guardar Registro")
                
                if enviar:
                    if nombre_u and id_u and clave_u:
                        # ANTI-HACKER: Limpieza de ID
                        id_limpio = "".join(e for e in id_u if e.isalnum()).lower()
                        
                        # VERIFICAR SI YA EXISTE
                        if id_limpio in df_usuarios['Usuario'].astype(str).str.lower().values:
                            st.error(f"❌ El usuario '{id_limpio}' ya existe en el sistema.")
                        else:
                            # CREAR NUEVO REGISTRO
                            nuevo_registro = {
                                "Nombre": nombre_u,
                                "Usuario": id_limpio,
                                "Clave": clave_u,
                                "Rol": rol_u,
                                "Area": "General" # Valor por defecto
                            }
                            
                            # ACTUALIZAR DATAFRAME
                            df_usuarios = pd.concat([df_usuarios, pd.DataFrame([nuevo_registro])], ignore_index=True)
                            
                            # GUARDAR EN EL EXCEL REAL
                            try:
                                guardar_global(df_inv, df_mov, df_usuarios, df_mant, df_lug, df_papelera)
                                st.success(f"🎉 ¡Usuario '{id_limpio}' registrado con éxito!")
                                st.balloons()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error al guardar: {e}")
                    else:
                        st.warning("⚠️ Todos los campos son obligatorios.")

    st.divider()
    
    # --- 4. LISTA DE USUARIOS ---
    st.subheader("📋 Personal con Acceso")
    # Mostramos solo columnas importantes para seguridad
    columnas_ver = [c for c in ['Nombre', 'Usuario', 'Rol'] if c in df_usuarios.columns]
    st.dataframe(df_usuarios[columnas_ver], use_container_width=True)
