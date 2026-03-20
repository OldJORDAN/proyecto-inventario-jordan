import streamlit as st
import pandas as pd
from modulos.seguridad import encriptar_clave

def mostrar(df_u, guardar_func, df_inv, df_mov, df_mant, df_lug, df_papelera):
    st.header("👤 Gestión de Usuarios y Personal")

    # Detectar nombre de la columna (para evitar el error anterior)
    posibles_nombres = ['Area', 'Tipo_Personal', 'Tipo']
    col_area = next((c for c in posibles_nombres if c in df_u.columns), 'Area')

    # --- SECCIÓN 1: REGISTRO SEPARADO ---
    st.subheader("➕ Registro de Nuevo Personal")
    tab_reg_oficina, tab_reg_obra = st.tabs(["🏢 Registrar para Oficina", "🏗️ Registrar para Obra"])

    with tab_reg_oficina:
        with st.form("form_oficina"):
            col1, col2 = st.columns(2)
            with col1:
                nom = st.text_input("Nombre Real")
                usu = st.text_input("Usuario")
            with col2:
                cla = st.text_input("Contraseña", type="password")
                rol = st.selectbox("Rol Oficina", ["Desarrollador", "Supervisor", "Secretaria", "Contador"])
            
            if st.form_submit_button("Registrar en Oficina"):
                if usu and cla:
                    nuevo = {"Nombre": nom, "Usuario": usu, "Clave": encriptar_clave(cla), "Rol": rol, col_area: "Oficina"}
                    df_u = pd.concat([df_u, pd.DataFrame([nuevo])], ignore_index=True)
                    guardar_func(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                    st.success("Personal de Oficina guardado")
                    st.rerun()

    with tab_reg_obra:
        with st.form("form_obra"):
            col1, col2 = st.columns(2)
            with col1:
                nom = st.text_input("Nombre del Trabajador")
                usu = st.text_input("Código/ID Usuario")
            with col2:
                cla = st.text_input("Contraseña Acceso", type="password")
                rol = st.selectbox("Cargo en Obra", ["Operador", "Residente", "Maestro de Obra", "Ayudante"])
            
            if st.form_submit_button("Registrar en Obra"):
                if usu and cla:
                    nuevo = {"Nombre": nom, "Usuario": usu, "Clave": encriptar_clave(cla), "Rol": rol, col_area: "Obra"}
                    df_u = pd.concat([df_u, pd.DataFrame([nuevo])], ignore_index=True)
                    guardar_func(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                    st.success("Trabajador de Obra guardado")
                    st.rerun()

    st.divider()

    # --- SECCIÓN 2: LISTADO SEPARADO ---
    st.subheader("📋 Listado de Personal Activo")
    tab_ver_oficina, tab_ver_obra = st.tabs(["👥 Personal de Oficina", "👷 Personal de Obra"])

    with tab_ver_oficina:
        # Filtramos solo los de Oficina
        df_oficina = df_u[df_u[col_area] == "Oficina"]
        if not df_oficina.empty:
            for i, row in df_oficina.iterrows():
                c1, c2, c3, c4 = st.columns([2, 2, 2, 0.5])
                c1.write(f"**{row['Nombre']}**")
                c2.write(f"@{row['Usuario']}")
                c3.write(f"📂 {row['Rol']}")
                if c4.button("🗑️", key=f"del_of_{i}"):
                    df_u = df_u.drop(i)
                    guardar_func(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                    st.rerun()
        else:
            st.info("No hay personal de oficina registrado.")

    with tab_ver_obra:
        # Filtramos solo los de Obra
        df_obra = df_u[df_u[col_area] == "Obra"]
        if not df_obra.empty:
            for i, row in df_obra.iterrows():
                c1, c2, c3, c4 = st.columns([2, 2, 2, 0.5])
                c1.write(f"**{row['Nombre']}**")
                c2.write(f"@{row['Usuario']}")
                c3.write(f"🔨 {row['Rol']}")
                if c4.button("🗑️", key=f"del_ob_{i}"):
                    df_u = df_u.drop(i)
                    guardar_func(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                    st.rerun()
        else:
            st.info("No hay trabajadores de obra registrados.")