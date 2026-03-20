import streamlit as st
import pandas as pd

def mostrar(df_u, guardar_global, df_inv, df_mov, df_mant, df_lug, df_papelera):
    st.title("👥 Gestión de Personal y Control de Acceso")

    # --- 1. BARRA DE ESTADO DE LICENCIAS ---
    try:
        df_conf = pd.read_excel("database.xlsx", sheet_name="Configuracion")
        limite = int(df_conf.loc[df_conf['Parametro'] == 'Limite_Usuarios', 'Valor'].values[0])
    except:
        limite = 50 # Valor por defecto

    usuarios_actuales = len(df_u)
    st.write(f"**Uso de Licencias:** {usuarios_actuales} de {limite}")
    st.progress(min(usuarios_actuales / limite, 1.0))

    st.divider()

    # --- 2. REGISTRO DE PERSONAL (OFICINA / OBRA) ---
    st.subheader("➕ Registro de Nuevo Personal")
    tab_ofi, tab_obr = st.tabs(["🏢 Oficina", "👨‍🏭 Taller / Obra"])
    
    with tab_ofi:
        with st.form("form_oficina"):
            n = st.text_input("Nombre Completo")
            u = st.text_input("Usuario ID").lower().strip()
            c = st.text_input("Contraseña", type="password")
            r = st.selectbox("Rol", ["Administrador", "Supervisor", "Logística"])
            if st.form_submit_button("Registrar en Oficina"):
                if n and u and c:
                    nuevo = pd.DataFrame([{"Nombre": n, "Usuario": u, "Clave": c, "Rol": r, "Tipo_Personal": "Oficina", "Estado_Licencia": "Activo", "Display": f"{n} ({r})"}])
                    df_u = pd.concat([df_u, nuevo], ignore_index=True)
                    guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                    st.success("✅ Registrado en Oficina")
                    st.rerun()

    with tab_obr:
        with st.form("form_obra"):
            n = st.text_input("Nombre Completo")
            u = st.text_input("Usuario ID Taller").lower().strip()
            c = st.text_input("Contraseña", type="password")
            r = st.selectbox("Especialidad", ["Maestro de Obra", "Soldador", "Cortador", "Amolador", "Pintor"])
            if st.form_submit_button("Registrar en Taller"):
                if n and u and c:
                    nuevo = pd.DataFrame([{"Nombre": n, "Usuario": u, "Clave": c, "Rol": r, "Tipo_Personal": "Obra", "Estado_Licencia": "Activo", "Display": f"{n} ({r})"}])
                    df_u = pd.concat([df_u, nuevo], ignore_index=True)
                    guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                    st.success("✅ Registrado en Taller")
                    st.rerun()

    st.divider()

    # --- 3. PANEL DE CONTROL TOTAL (SOLO PARA DESARROLLADOR) ---
    if st.session_state['rol'] == "Desarrollador":
        st.subheader("🛠️ Panel de Control de Acceso (Solo Desarrollador)")
        
        # Lista de usuarios excluyéndote a ti
        u_gest = df_u[df_u['Usuario'] != 'jordan']
        
        if not u_gest.empty:
            col_sel, col_acc = st.columns([2, 2])
            
            with col_sel:
                u_sel = st.selectbox("Seleccione Usuario:", u_gest['Usuario'].tolist())
                # Obtener datos actuales
                idx = df_u[df_u['Usuario'] == u_sel].index[0]
                estado_act = df_u.at[idx, 'Estado_Licencia']
                nombre_act = df_u.at[idx, 'Nombre']
                
                st.write(f"Estado Actual: **{estado_act}**")

            with col_acc:
                st.write("**Acciones Disponibles:**")
                # Botón 1: Deshabilitar/Habilitar
                txt_des = "🚫 Deshabilitar Licencia" if estado_act == "Activo" else "✅ Habilitar Licencia"
                if st.button(txt_des, use_container_width=True):
                    df_u.at[idx, 'Estado_Licencia'] = "Inactivo" if estado_act == "Activo" else "Activo"
                    guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                    st.toast(f"Licencia de {u_sel} actualizada.")
                    st.rerun()
                
                # Botón 2: Eliminar (¡NUEVO!)
                st.write("---")
                with st.expander("🗑️ Zona de Peligro: Eliminar Usuario"):
                    st.warning(f"¿Está seguro de borrar permanentemente a **{nombre_act}**?")
                    check_seguro = st.checkbox(f"Sí, soy Jordan y quiero borrar a {u_sel}")
                    if st.button("❌ Eliminar Permanentemente", type="primary", use_container_width=True):
                        if check_seguro:
                            df_u = df_u[df_u['Usuario'] != u_sel]
                            guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                            st.success(f"Usuario {u_sel} eliminado.")
                            st.rerun()
                        else:
                            st.error("Debe confirmar la casilla para eliminar.")
        else:
            st.info("No hay otros usuarios registrados para gestionar.")
        
        st.divider()

    # --- 4. VISTA DE TABLA ---
    st.subheader("📋 Personal Registrado")
    st.dataframe(df_u[['Nombre', 'Usuario', 'Rol', 'Tipo_Personal', 'Estado_Licencia']], use_container_width=True)
