import streamlit as st
import pandas as pd

def mostrar(df_u, guardar_global, df_inv, df_mov, df_mant, df_lug, df_papelera):
    st.title("👥 Gestión de Personal y Control de Licencias")

    # --- 1. BARRA DE LICENCIAS ---
    # No te contamos a ti (jordan) en el uso de licencias
    df_reales = df_u[~df_u['Usuario'].str.contains('jordan', case=False, na=False)]
    st.write(f"**Uso de Licencias:** {len(df_reales)} de 50")
    st.progress(min(len(df_reales) / 50, 1.0))
    st.divider()

    # --- 2. REGISTRO (OFICINA / TALLER) ---
    t1, t2 = st.tabs(["🏢 Oficina", "👨‍🏭 Taller / Obra"])
    with t1:
        with st.form("f_ofi_final"):
            n = st.text_input("Nombre Completo"); u = st.text_input("ID").lower().strip(); c = st.text_input("Clave", type="password")
            if st.form_submit_button("Registrar Oficina"):
                if n and u:
                    nuevo = pd.DataFrame([{"Nombre":n,"Usuario":u,"Clave":c,"Rol":"Administrador","Tipo_Personal":"Oficina","Estado_Licencia":"Activo"}])
                    df_u = pd.concat([df_u, nuevo], ignore_index=True); guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera); st.rerun()

    with t2:
        with st.form("f_obr_final"):
            n = st.text_input("Nombre Completo "); u = st.text_input("ID Taller").lower().strip(); c = st.text_input("Clave ", type="password")
            if st.form_submit_button("Registrar Taller"):
                if n and u:
                    nuevo = pd.DataFrame([{"Nombre":n,"Usuario":u,"Clave":c,"Rol":"Operativo","Tipo_Personal":"Obra","Estado_Licencia":"Activo"}])
                    df_u = pd.concat([df_u, nuevo], ignore_index=True); guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera); st.rerun()

    st.divider()

    # --- 3. PANEL DE CONTROL (CON BOTÓN ELIMINAR) ---
    st.subheader("🛠️ Panel de Control")
    if not df_reales.empty:
        # Usamos 3 columnas: una para el select, otra para deshabilitar y otra para eliminar
        c1, c2, c3 = st.columns([2, 1, 1])
        
        with c1:
            u_sel = st.selectbox("Usuario para gestionar:", df_reales['Usuario'].tolist())
            idx = df_u[df_u['Usuario'] == u_sel].index[0]
            est = df_u.at[idx, 'Estado_Licencia']
            st.write(f"Estado: **{est}**")

        with c2:
            st.write("Acceso")
            if st.button("🚫 Deshabilitar" if est=="Activo" else "✅ Habilitar", use_container_width=True):
                df_u.at[idx, 'Estado_Licencia'] = "Inactivo" if est=="Activo" else "Activo"
                guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera); st.rerun()

        with c3:
            st.write("Zona de Peligro")
            confirmar = st.checkbox("Confirmar borrar", key="check_del")
            if confirmar:
                if st.button("🗑️ Eliminar Usuario", type="primary", use_container_width=True):
                    df_u = df_u.drop(idx)
                    guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                    st.success("Usuario eliminado")
                    st.rerun()
    else:
        st.info("No hay otros usuarios registrados.")

    st.divider()

    # --- 4. TABLA DE PERSONAL ---
    st.subheader("📋 Personal Registrado")
    filtro = st.radio("Mostrar:", ["Todos", "Oficina", "Obra"], horizontal=True)
    df_v = df_reales.copy()
    if filtro == "Oficina": df_v = df_v[df_v['Tipo_Personal'] == 'Oficina']
    elif filtro == "Obra": df_v = df_v[df_v['Tipo_Personal'] == 'Obra']

    def style_e(v):
        color = '#28a745' if v == 'Activo' else '#dc3545'
        return f'color: {color}; font-weight: bold'

    st.dataframe(df_v[['Nombre', 'Usuario', 'Rol', 'Tipo_Personal', 'Estado_Licencia']].style.applymap(style_e, subset=['Estado_Licencia']), use_container_width=True)
