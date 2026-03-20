import streamlit as st
import pandas as pd

def mostrar(df_u, guardar_global, df_inv, df_mov, df_mant, df_lug, df_papelera):
    st.title("👥 Gestión de Personal y Control de Licencias")

    # --- 1. BARRA DE LICENCIAS (CONTEO TOTAL) ---
    usuarios_actuales = len(df_u)
    st.write(f"**Uso de Licencias:** {usuarios_actuales} de 50")
    st.progress(min(usuarios_actuales / 50, 1.0))
    st.divider()

    # --- 2. REGISTRO DE PERSONAL (OFICINA / TALLER) ---
    tab_ofi, tab_obr = st.tabs(["🏢 Oficina", "👨‍🏭 Taller / Obra"])
    
    with tab_ofi:
        with st.form("form_oficina"):
            n = st.text_input("Nombre Completo")
            u = st.text_input("Usuario ID").lower().strip()
            c = st.text_input("Clave", type="password")
            r = st.selectbox("Rol", ["Administrador", "Supervisor", "Logística"])
            if st.form_submit_button("Registrar en Oficina"):
                if n and u and c:
                    nuevo = pd.DataFrame([{"Nombre": n, "Usuario": u, "Clave": c, "Rol": r, "Tipo_Personal": "Oficina", "Estado_Licencia": "Activo"}])
                    df_u = pd.concat([df_u, nuevo], ignore_index=True)
                    guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                    st.rerun()

    with tab_obr:
        with st.form("form_obra"):
            n = st.text_input("Nombre Completo ")
            u = st.text_input("Usuario ID Taller").lower().strip()
            c = st.text_input("Clave ", type="password")
            r = st.selectbox("Especialidad", ["Maestro de Obra", "Soldador", "Cortador", "Amolador", "Pintor"])
            if st.form_submit_button("Registrar en Taller"):
                if n and u and c:
                    nuevo = pd.DataFrame([{"Nombre": n, "Usuario": u, "Clave": c, "Rol": r, "Tipo_Personal": "Obra", "Estado_Licencia": "Activo"}])
                    df_u = pd.concat([df_u, nuevo], ignore_index=True)
                    guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                    st.rerun()

    st.divider()

    # --- 3. PANEL DE CONTROL (SEGÚN TU FOTO) ---
    st.subheader("🛠️ Panel de Control de Acceso (Solo Desarrollador)")
    
    mi_rol = str(st.session_state.get('rol', '')).lower().strip()
    
    if not df_u.empty:
        # Layout de 3 columnas para que quepa el selector, el estado y el botón
        c1, c2, c3 = st.columns([2, 1, 1])
        
        with c1:
            # Aquí salen TODOS los usuarios, incluido tú
            u_sel = st.selectbox("Seleccione Usuario para gestionar:", df_u['Usuario'].tolist(), key="sel_gest")
            idx = df_u[df_u['Usuario'] == u_sel].index[0]
            est_act = df_u.at[idx, 'Estado_Licencia']
        
        with c2:
            st.write(f"Estado: **{est_act}**")
            
        with c3:
            # Botón de Deshabilitar
            txt_bt = "🚫 Deshabilitar" if est_act == "Activo" else "✅ Habilitar"
            if st.button(txt_bt, use_container_width=True):
                df_u.at[idx, 'Estado_Licencia'] = "Inactivo" if est_act == "Activo" else "Activo"
                guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                st.rerun()
                
    st.divider()

    # --- 4. TABLA DE PERSONAL REGISTRADO (CON FILTROS) ---
    st.write("**Mostrar:**")
    filtro_v = st.radio("", ["Todos", "Oficina", "Obra"], horizontal=True, label_visibility="collapsed")
    
    df_v = df_u.copy()
    if filtro_v == "Oficina":
        df_v = df_v[df_v['Tipo_Personal'] == 'Oficina']
    elif filtro_v == "Obra":
        df_v = df_v[df_v['Tipo_Personal'] == 'Obra']

    # Aplicamos estilo de colores
    def style_estado(val):
        color = '#28a745' if val == 'Activo' else '#dc3545'
        return f'color: {color}; font-weight: bold'

    st.dataframe(
        df_v[['Nombre', 'Usuario', 'Rol', 'Estado_Licencia']].style.applymap(
            style_estado, subset=['Estado_Licencia']
        ), use_container_width=True
    )
