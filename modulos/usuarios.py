import streamlit as st
import pandas as pd

def mostrar(df_u, guardar_global, df_inv, df_mov, df_mant, df_lug, df_papelera):
    st.title("👥 Gestión de Personal y Control de Acceso")

    # 1. CONTADOR (SIN TI)
    df_reales = df_u[~df_u['Usuario'].str.contains('jordan', case=False, na=False)]
    st.write(f"**Uso de Licencias:** {len(df_reales)} de 50")
    st.progress(min(len(df_reales) / 50, 1.0))
    st.divider()

    # 2. REGISTRO
    t1, t2 = st.tabs(["🏢 Oficina", "👨‍🏭 Obra"])
    with t1:
        with st.form("ofi"):
            n = st.text_input("Nombre"); u = st.text_input("ID").lower(); c = st.text_input("Clave", type="password")
            if st.form_submit_button("Registrar Oficina"):
                if n and u:
                    nuevo = pd.DataFrame([{"Nombre":n,"Usuario":u,"Clave":c,"Rol":"Administrador","Tipo_Personal":"Oficina","Estado_Licencia":"Activo"}])
                    df_u = pd.concat([df_u, nuevo], ignore_index=True); guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera); st.rerun()
    with t2:
        with st.form("obr"):
            n = st.text_input("Nombre "); u = st.text_input("ID Obra").lower(); c = st.text_input("Clave ", type="password")
            if st.form_submit_button("Registrar Obra"):
                if n and u:
                    nuevo = pd.DataFrame([{"Nombre":n,"Usuario":u,"Clave":c,"Rol":"Operativo","Tipo_Personal":"Obra","Estado_Licencia":"Activo"}])
                    df_u = pd.concat([df_u, nuevo], ignore_index=True); guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera); st.rerun()

    # 3. PANEL DE CONTROL (JERARQUÍA)
    mi_rol = str(st.session_state.get('rol', '')).lower().strip()
    if "desarrollador" in mi_rol or "administrador" in mi_rol:
        st.subheader("🛠️ Panel de Control")
        if not df_reales.empty:
            es_dev = "desarrollador" in mi_rol
            cols = st.columns(3 if es_dev else 2)
            with cols[0]:
                u_sel = st.selectbox("Usuario:", df_reales['Usuario'].tolist())
                idx = df_u[df_u['Usuario'] == u_sel].index[0]; est = df_u.at[idx, 'Estado_Licencia']
            with cols[1]:
                if st.button("🚫 Deshabilitar" if est=="Activo" else "✅ Habilitar", use_container_width=True):
                    df_u.at[idx, 'Estado_Licencia'] = "Inactivo" if est=="Activo" else "Activo"
                    guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera); st.rerun()
            if es_dev: # SOLO TÚ VES ESTO
                with cols[2]:
                    if st.checkbox("Confirmar borrar", key="del_chk"):
                        if st.button("🗑️ Eliminar", type="primary"):
                            df_u = df_u.drop(idx); guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera); st.rerun()

    # 4. VISTA CON COLORES
    st.subheader("📋 Personal Registrado")
    filtro = st.radio("Filtro:", ["Todos", "Oficina", "Obra"], horizontal=True)
    df_v = df_reales.copy()
    if filtro == "Oficina": df_v = df_v[df_v['Tipo_Personal'] == 'Oficina']
    elif filtro == "Obra": df_v = df_v[df_v['Tipo_Personal'] == 'Obra']
    df_v['Estado_Licencia'] = df_v['Estado_Licencia'].replace('Inactivo', 'Deshabilitado')
    
    st.dataframe(df_v[['Nombre', 'Usuario', 'Rol', 'Tipo_Personal', 'Estado_Licencia']].style.applymap(
        lambda x: f"color: {'#28a745' if x=='Activo' else '#dc3545'}; font-weight: bold", subset=['Estado_Licencia']
    ), use_container_width=True)
