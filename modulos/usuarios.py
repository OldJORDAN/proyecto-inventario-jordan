import streamlit as st
import pandas as pd

def mostrar(df_u, guardar_global, df_inv, df_mov, df_mant, df_lug, df_papelera):
    st.title("👥 Gestión de Personal")

    # Tabs para separar Oficina de Obra
    tab_oficina, tab_obra = st.tabs(["🏢 Oficina", "👨‍🏭 Taller / Obra"])

    with tab_oficina:
        with st.form("f_oficina"):
            n = st.text_input("Nombre")
            u = st.text_input("Usuario (ID)").lower().strip()
            c = st.text_input("Clave")
            r = st.selectbox("Rol", ["Administrador", "Supervisor", "Logística"])
            if st.form_submit_button("Registrar en Oficina"):
                if n and u and c:
                    nuevo = pd.DataFrame([{"Nombre": n, "Usuario": u, "Clave": c, "Rol": r, "Tipo_Personal": "Oficina", "Display": f"{n} ({r})"}])
                    df_u = pd.concat([df_u, nuevo], ignore_index=True)
                    # AQUÍ SE SINCRONIZA CON EL EXCEL
                    guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                    st.success("Registrado correctamente")
                    st.rerun()

    with tab_obra:
        with st.form("f_obra"):
            n = st.text_input("Nombre")
            u = st.text_input("Usuario / ID Obra").lower().strip()
            c = st.text_input("Clave")
            r = st.selectbox("Especialidad", ["Maestro de Obra", "Soldador", "Cortador", "Amolador", "Pintor"])
            if st.form_submit_button("Registrar en Obra"):
                if n and u and c:
                    nuevo = pd.DataFrame([{"Nombre": n, "Usuario": u, "Clave": c, "Rol": r, "Tipo_Personal": "Obra", "Display": f"{n} ({r})"}])
                    df_u = pd.concat([df_u, nuevo], ignore_index=True)
                    # AQUÍ SE SINCRONIZA CON EL EXCEL
                    guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                    st.success("Registrado en Taller")
                    st.rerun()

    st.divider()
    st.subheader("📋 Usuarios en Base de Datos")
    st.dataframe(df_u[['Nombre', 'Usuario', 'Rol', 'Tipo_Personal']], use_container_width=True)

    # Panel de eliminación al final
    with st.expander("🗑️ Eliminar Usuario"):
        u_list = df_u[df_u['Usuario'] != 'jordan']['Usuario'].tolist()
        sel = st.selectbox("Seleccionar para borrar", u_list)
        if st.button("❌ Borrar Definitivamente"):
            df_u = df_u[df_u['Usuario'] != sel]
            guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
            st.rerun()
