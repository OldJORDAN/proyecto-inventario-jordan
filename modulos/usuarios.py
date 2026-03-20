import streamlit as st
import pandas as pd

def mostrar(df_u, guardar_global, df_inv, df_mov, df_mant, df_lug, df_papelera):
    st.title("👥 Gestión de Personal y Control de Licencias")

    # --- 1. BARRA DE LICENCIAS ---
    usuarios_actuales = len(df_u)
    st.write(f"**Uso de Licencias:** {usuarios_actuales} de 50")
    st.progress(min(usuarios_actuales / 50, 1.0))
    st.divider()

    # --- 2. REGISTRO (OFICINA / TALLER) ---
    t1, t2 = st.tabs(["🏢 Oficina", "👨‍🏭 Taller / Obra"])
    with t1:
        with st.form("f_oficina_reg"):
            n = st.text_input("Nombre Completo")
            u = st.text_input("Usuario ID").lower().strip()
            c = st.text_input("Clave", type="password")
            r = st.selectbox("Rol", ["Administrador", "Supervisor", "Logística"])
            if st.form_submit_button("Registrar en Oficina"):
                if n and u:
                    nuevo = pd.DataFrame([{"Nombre":n,"Usuario":u,"Clave":c,"Rol":r,"Tipo_Personal":"Oficina","Estado_Licencia":"Activo"}])
                    df_u = pd.concat([df_u, nuevo], ignore_index=True)
                    guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera); st.rerun()

    with t2:
        with st.form("f_obra_reg"):
            n = st.text_input("Nombre Completo ")
            u = st.text_input("Usuario ID Taller").lower().strip()
            c = st.text_input("Clave ", type="password")
            r = st.selectbox("Especialidad", ["Maestro de Obra", "Soldador", "Cortador", "Amolador", "Pintor"])
            if st.form_submit_button("Registrar en Taller"):
                if n and u:
                    nuevo = pd.DataFrame([{"Nombre":n,"Usuario":u,"Clave":c,"Rol":r,"Tipo_Personal":"Obra","Estado_Licencia":"Activo"}])
                    df_u = pd.concat([df_u, nuevo], ignore_index=True)
                    guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera); st.rerun()

    st.divider()

    # --- 3. PANEL DE CONTROL (SOLO PARA CAMBIAR ESTADO) ---
    st.subheader("🛠️ Panel de Control de Acceso (Solo Desarrollador)")
    if not df_u.empty:
        c1, c2 = st.columns([2, 1])
        with c1:
            u_sel = st.selectbox("Seleccione Usuario para gestionar:", df_u['Usuario'].tolist())
            user_data = df_u[df_u['Usuario'] == u_sel]
            idx = user_data.index[0]
            est_act = user_data.iloc[0]['Estado_Licencia']
        with c2:
            st.write(f"Estado: **{est_act}**")
            if st.button("🚫 Deshabilitar" if est_act == "Activo" else "✅ Habilitar", use_container_width=True):
                df_u.at[idx, 'Estado_Licencia'] = "Inactivo" if est_act == "Activo" else "Activo"
                guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera); st.rerun()

    st.divider()

    # --- 4. LA TABLA QUE TE FALTABA (VISTA GENERAL) ---
    st.subheader("📋 Personal Registrado")
    
    # Botones de filtro
    filtro = st.radio("Filtrar por área:", ["Todos", "Oficina", "Obra"], horizontal=True)
    
    df_vista = df_u.copy()
    if filtro == "Oficina":
        df_vista = df_vista[df_vista['Tipo_Personal'] == 'Oficina']
    elif filtro == "Obra":
        df_vista = df_vista[df_vista['Tipo_Personal'] == 'Obra']

    # Formateo de colores para que se vea belleza
    def color_estado(val):
        color = '#28a745' if val == 'Activo' else '#dc3545'
        return f'color: {color}; font-weight: bold'

    # Mostramos la tabla con Nombre, Usuario, Rol y Área
    st.dataframe(
        df_vista[['Nombre', 'Usuario', 'Rol', 'Tipo_Personal', 'Estado_Licencia']].style.applymap(
            color_estado, subset=['Estado_Licencia']
        ), 
        use_container_width=True
    )
