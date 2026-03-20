import streamlit as st
import pandas as pd

def mostrar(df_u, guardar_global, df_inv, df_mov, df_mant, df_lug, df_papelera):
    st.title("👥 Gestión de Personal y Control de Acceso")

    # --- 1. BARRA DE LICENCIAS ---
    # Filtramos al desarrollador para que no cuente en la licencia ni salga en la tabla
    df_reales = df_u[~df_u['Usuario'].str.contains('jordan', case=False, na=False)]
    usuarios_actuales = len(df_reales)
    st.write(f"**Uso de Licencias:** {usuarios_actuales} de 50")
    st.progress(min(usuarios_actuales / 50, 1.0))
    st.divider()

    # --- 2. REGISTRO DE PERSONAL ---
    tab_ofi, tab_obr = st.tabs(["🏢 Oficina", "👨‍🏭 Taller / Obra"])
    
    with tab_ofi:
        with st.form("form_oficina"):
            n = st.text_input("Nombre Completo")
            u = st.text_input("Usuario ID").lower().strip()
            c = st.text_input("Contraseña", type="password")
            r = st.selectbox("Rol", ["Administrador", "Supervisor", "Logística"])
            if st.form_submit_button("Registrar en Oficina"):
                if n and u and c:
                    nuevo = pd.DataFrame([{"Nombre": n, "Usuario": u, "Clave": c, "Rol": r, "Tipo_Personal": "Oficina", "Estado_Licencia": "Activo"}])
                    df_u = pd.concat([df_u, nuevo], ignore_index=True)
                    guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                    st.success("✅ Registrado en Oficina")
                    st.rerun()

    with tab_obr:
        with st.form("form_obra"):
            n = st.text_input("Nombre Completo ")
            u = st.text_input("Usuario ID Taller").lower().strip()
            c = st.text_input("Contraseña ", type="password")
            r = st.selectbox("Especialidad", ["Maestro de Obra", "Soldador", "Cortador", "Amolador", "Pintor"])
            if st.form_submit_button("Registrar en Taller"):
                if n and u and c:
                    nuevo = pd.DataFrame([{"Nombre": n, "Usuario": u, "Clave": c, "Rol": r, "Tipo_Personal": "Obra", "Estado_Licencia": "Activo"}])
                    df_u = pd.concat([df_u, nuevo], ignore_index=True)
                    guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                    st.success("✅ Registrado en Taller")
                    st.rerun()

    st.divider()

    # --- 3. PANEL DE CONTROL (JERARQUÍA DE ROLES) ---
    mi_rol = str(st.session_state.get('rol', '')).lower().strip()
    
    if "desarrollador" in mi_rol or "administrador" in mi_rol:
        st.subheader("🛠️ Panel de Control de Acceso")
        
        if not df_reales.empty:
            es_dev = "desarrollador" in mi_rol
            # Si eres Dev ves 3 columnas, si eres Admin ves 2
            cols = st.columns(3 if es_dev else 2)
            
            with cols[0]:
                u_sel = st.selectbox("Seleccione Usuario:", df_reales['Usuario'].tolist())
                idx = df_u[df_u['Usuario'] == u_sel].index[0]
                est_act = df_u.at[idx, 'Estado_Licencia']
                st.write(f"Estado actual: **{est_act}**")

            with cols[1]:
                st.write("¿Cambiar acceso?")
                txt_bt = "🚫 Deshabilitar" if est_act == "Activo" else "✅ Habilitar"
                if st.button(txt_bt, use_container_width=True):
                    df_u.at[idx, 'Estado_Licencia'] = "Inactivo" if est_act == "Activo" else "Activo"
                    guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                    st.rerun()

            if es_dev:
                with cols[2]:
                    st.write("¿Borrar para siempre?")
                    if st.checkbox("Confirmar eliminación", key="del_user_final"):
                        if st.button("🗑️ Eliminar Usuario", type="primary", use_container_width=True):
                            df_u = df_u.drop(idx)
                            guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                            st.rerun()
        else:
            st.info("No hay otros usuarios registrados para gestionar.")

    st.divider()

    # --- 4. VISTA DE TABLA CON COLORES ---
    st.subheader("📋 Personal Registrado")
    
    # Selector de filtro
    filtro_vista = st.radio("Mostrar:", ["Todos", "Oficina", "Obra"], horizontal=True)
    
    # Preparamos los datos de la vista
    df_v = df_reales.copy()
    if filtro_vista == "Oficina":
        df_v = df_v[df_v['Tipo_Personal'] == 'Oficina']
    elif filtro_vista == "Obra":
        df_v = df_v[df_v['Tipo_Personal'] == 'Obra']

    df_v['Estado_Licencia'] = df_v['Estado_Licencia'].replace('Inactivo', 'Deshabilitado')

    def style_estado(val):
        color = '#28a745' if val == 'Activo' else '#dc3545'
        return f'color: {color}; font-weight: bold'

    st.dataframe(
        df_v[['Nombre', 'Usuario', 'Rol', 'Tipo_Personal', 'Estado_Licencia']].style.applymap(
            style_estado, subset=['Estado_Licencia']
        ), 
        use_container_width=True
    )
