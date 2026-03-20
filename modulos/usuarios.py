import streamlit as st
import pandas as pd

def mostrar(df_u, guardar_global, df_inv, df_mov, df_mant, df_lug, df_papelera):
    st.title("👥 Gestión de Usuarios y Licencias")

    try:
        df_conf = pd.read_excel("database.xlsx", sheet_name="Configuracion")
        limite = int(df_conf.loc[df_conf['Parametro'] == 'Limite_Usuarios', 'Valor'].values[0])
    except:
        limite = 60

    usuarios_actuales = len(df_u)

    st.subheader("📊 Estado de Licencias")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.progress(min(usuarios_actuales / limite, 1.0))
    with col2:
        st.write(f"**{usuarios_actuales} / {limite}**")

    if usuarios_actuales >= limite:
        st.error(f"🚫 Límite de {limite} usuarios alcanzado.")
    else:
        with st.expander("➕ Registrar Nuevo Usuario"):
            with st.form("reg_u"):
                n = st.text_input("Nombre")
                u = st.text_input("Usuario")
                c = st.text_input("Clave", type="password")
                r = st.selectbox("Rol", ["Operador", "Supervisor", "Administrador"])
                if st.form_submit_button("Guardar"):
                    if n and u and c:
                        nuevo = {"Nombre": n, "Usuario": u.lower().strip(), "Clave": c, "Rol": r, "Area": "General"}
                        df_u = pd.concat([df_u, pd.DataFrame([nuevo])], ignore_index=True)
                        guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                        st.success("Usuario guardado")
                        st.rerun()
    
    st.divider()
    st.dataframe(df_u[['Nombre', 'Usuario', 'Rol']], use_container_width=True)
