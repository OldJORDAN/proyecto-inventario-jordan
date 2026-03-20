import streamlit as st
import pandas as pd

def mostrar(df_u, guardar_global, df_inv, df_mov, df_mant, df_lug, df_papelera):
    st.title("👥 Gestión de Personal y Control de Licencias")

    # --- 1. BARRA DE LICENCIAS ---
    st.write(f"**Uso de Licencias:** {len(df_u)} de 50")
    st.progress(min(len(df_u) / 50, 1.0))
    st.divider()

    # --- 2. REGISTRO ---
    t1, t2 = st.tabs(["🏢 Oficina", "👨‍🏭 Taller / Obra"])
    with t1:
        with st.form("f_ofi"):
            n = st.text_input("Nombre Completo"); u = st.text_input("ID").lower().strip(); c = st.text_input("Clave", type="password")
            if st.form_submit_button("Registrar Oficina"):
                if n and u:
                    nuevo = pd.DataFrame([{"Nombre":n,"Usuario":u,"Clave":c,"Rol":"Administrador","Tipo_Personal":"Oficina","Estado_Licencia":"Activo"}])
                    df_u = pd.concat([df_u, nuevo], ignore_index=True); guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera); st.rerun()

    with t2:
        with st.form("f_obr"):
            n = st.text_input("Nombre Completo "); u = st.text_input("ID Taller").lower().strip(); c = st.text_input("Clave ", type="password")
            if st.form_submit_button("Registrar Taller"):
                if n and u:
                    nuevo = pd.DataFrame([{"Nombre":n,"Usuario":u,"Clave":c,"Rol":"Operativo","Tipo_Personal":"Obra","Estado_Licencia":"Activo"}])
                    df_u = pd.concat([df_u, nuevo], ignore_index=True); guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera); st.rerun()

    st.divider()

    # --- 3. PANEL DE CONTROL ---
    st.subheader("🛠️ Panel de Control")
    if not df_u.empty:
        c1, c2 = st.columns([2, 1])
        with c1:
            u_sel = st.selectbox("Usuario:", df_u['Usuario'].tolist())
            idx = df_u[df_u['Usuario'] == u_sel].index[0]; est = df_u.at[idx, 'Estado_Licencia']
        with c2:
            st.write(f"Estado: {est}")
            if st.button("🚫 Deshabilitar" if est=="Activo" else "✅ Habilitar"):
                df_u.at[idx, 'Estado_Licencia'] = "Inactivo" if est=="Activo" else "Activo"
                guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera); st.rerun()

    st.divider()

    # --- 4. TABLA DE PERSONAL (VUELVE A VERSE TODO) ---
    st.subheader("📋 Personal Registrado")
    filtro = st.radio("Mostrar:", ["Todos", "Oficina", "Obra"], horizontal=True)
    df_v = df_u.copy()
    if filtro == "Oficina": df_v = df_v[df_v['Tipo_Personal'] == 'Oficina']
    elif filtro == "Obra": df_v = df_v[df_v['Tipo_Personal'] == 'Obra']

    def style_e(v):
        color = '#28a745' if v == 'Activo' else '#dc3545'
        return f'color: {color}; font-weight: bold'

    st.dataframe(df_v[['Nombre', 'Usuario', 'Rol', 'Tipo_Personal', 'Estado_Licencia']].style.applymap(style_e, subset=['Estado_Licencia']), use_container_width=True)
