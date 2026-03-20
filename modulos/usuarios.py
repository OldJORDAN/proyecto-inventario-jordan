import streamlit as st
import pandas as pd

def mostrar(df_u, guardar_global, df_inv, df_mov, df_mant, df_lug, df_papelera):
    st.title("👥 Gestión de Personal y Control de Licencias")

    # --- 1. BARRA DE LICENCIAS ---
    df_reales = df_u[~df_u['Usuario'].str.contains('jordan', case=False, na=False)]
    usuarios_actuales = len(df_reales)
    st.write(f"**Uso de Licencias:** {usuarios_actuales} de 50")
    st.progress(min(usuarios_actuales / 50, 1.0))
    st.divider()

    # --- 2. REGISTRO (OFICINA / TALLER) ---
    tab1, tab2 = st.tabs(["🏢 Oficina", "👨‍🏭 Taller / Obra"])
    
    with tab1:
        with st.form("f_ofi_unique"):
            n = st.text_input("Nombre Completo")
            u = st.text_input("Usuario (Nick)").lower().strip() # <-- CAMBIADO DE ID A USUARIO
            c = st.text_input("Clave", type="password")
            r = st.selectbox("Rol", ["Administrador", "Supervisor", "Logística"])
            if st.form_submit_button("Registrar en Oficina"):
                if n and u:
                    # CANDADO: Verificar si el usuario ya existe
                    if u in df_u['Usuario'].astype(str).str.lower().values:
                        st.error(f"❌ El usuario '{u}' ya existe. ¡Usa uno diferente!")
                    else:
                        nuevo = pd.DataFrame([{"Nombre":n,"Usuario":u,"Clave":c,"Rol":r,"Tipo_Personal":"Oficina","Estado_Licencia":"Activo"}])
                        df_u = pd.concat([df_u, nuevo], ignore_index=True)
                        guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                        st.rerun()

    with tab2:
        with st.form("f_obr_unique"):
            n = st.text_input("Nombre Completo ")
            u = st.text_input("Usuario Taller").lower().strip() # <-- CAMBIADO DE ID A USUARIO
            c = st.text_input("Clave ", type="password")
            r = st.selectbox("Especialidad", ["Maestro de Obra", "Soldador", "Cortador", "Amolador", "Pintor"])
            if st.form_submit_button("Registrar en Taller"):
                if n and u:
                    # CANDADO: Verificar si el usuario ya existe
                    if u in df_u['Usuario'].astype(str).str.lower().values:
                        st.error(f"❌ El usuario '{u}' ya existe. ¡Usa uno diferente!")
                    else:
                        nuevo = pd.DataFrame([{"Nombre":n,"Usuario":u,"Clave":c,"Rol":r,"Tipo_Personal":"Obra","Estado_Licencia":"Activo"}])
                        df_u = pd.concat([df_u, nuevo], ignore_index=True)
                        guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                        st.rerun()

    st.divider()

    # --- 3. PANEL DE CONTROL ---
    st.subheader("🛠️ Panel de Control")
    if not df_reales.empty:
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            u_sel = st.selectbox("Usuario para gestionar:", df_reales['Usuario'].tolist())
            idx = df_u[df_u['Usuario'] == u_sel].index[0]
            est = df_u.at[idx, 'Estado_Licencia']
        with c2:
            st.write(f"Estado: **{est}**")
            if st.button("🚫 Deshabilitar" if est=="Activo" else "✅ Habilitar", use_container_width=True):
                df_u.at[idx, 'Estado_Licencia'] = "Inactivo" if est=="Activo" else "Activo"
                guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera); st.rerun()
        with c3:
            st.write("Zona de Peligro")
            if st.checkbox("Confirmar borrar", key="check_safe"):
                if st.button("🗑️ Eliminar", type="primary", use_container_width=True):
                    df_u = df_u.drop(idx)
                    guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                    st.rerun()

    st.divider()

    # --- 4. TABLA DE PERSONAL ---
    st.subheader("📋 Personal Registrado")
    f_v = st.radio("Mostrar:", ["Todos", "Oficina", "Obra"], horizontal=True)
    df_v = df_reales.copy()
    if f_v == "Oficina": df_v = df_v[df_v['Tipo_Personal'] == 'Oficina']
    elif f_v == "Obra": df_v = df_v[df_v['Tipo_Personal'] == 'Obra']

    def style_e(v):
        return f'color: {"#28a745" if v == "Activo" else "#dc3545"}; font-weight: bold'

    st.dataframe(df_v[['Nombre', 'Usuario', 'Rol', 'Tipo_Personal', 'Estado_Licencia']].style.applymap(style_e, subset=['Estado_Licencia']), use_container_width=True)
