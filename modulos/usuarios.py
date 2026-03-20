import streamlit as st
import pandas as pd

def mostrar(df_u, guardar_global, df_inv, df_mov, df_mant, df_lug, df_papelera):
    st.title("👥 Gestión de Usuarios y Licencias")

    # --- 1. ESTADO DE LICENCIAS ---
    try:
        df_conf = pd.read_excel("database.xlsx", sheet_name="Configuracion")
        limite = int(df_conf.loc[df_conf['Parametro'] == 'Limite_Usuarios', 'Valor'].values[0])
    except:
        limite = 60

    usuarios_actuales = len(df_u)
    st.write(f"**Capacidad del Sistema:** {usuarios_actuales} de {limite} usuarios registrados.")
    st.progress(min(usuarios_actuales / limite, 1.0))

    st.divider()

    # --- 2. REGISTRO POR ÁREAS (OFICINA / OBRA) ---
    st.subheader("➕ Registro de Nuevo Personal")
    tab_oficina, tab_obra = st.tabs(["🏢 Personal de Oficina", "👨‍🏭 Personal de Taller / Obra"])

    # --- REGISTRO OFICINA ---
    with tab_oficina:
        with st.form("form_oficina"):
            n = st.text_input("Nombre Completo (Oficina)")
            u = st.text_input("Usuario / ID").lower().strip()
            c = st.text_input("Contraseña", type="password")
            # ELIMINADO 'Desarrollador' de aquí, solo tú lo tienes por código
            r = st.selectbox("Rol Oficina", ["Administrador", "Supervisor", "Contador", "Logística"])
            
            if st.form_submit_button("Guardar en Oficina"):
                if n and u and c:
                    if u in df_u['Usuario'].astype(str).values:
                        st.error("El usuario ya existe.")
                    else:
                        nuevo = {"Nombre": n, "Usuario": u, "Clave": c, "Rol": r, "Tipo_Personal": "Oficina", "Display": f"{n} ({r})"}
                        df_u = pd.concat([df_u, pd.DataFrame([nuevo])], ignore_index=True)
                        guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                        st.success(f"✅ {n} agregado como {r}")
                        st.rerun()

    # --- REGISTRO OBRA (CON TUS ROLES REALES) ---
    with tab_obra:
        with st.form("form_obra"):
            n = st.text_input("Nombre Completo (Taller/Obra)")
            u = st.text_input("Usuario / ID Obra").lower().strip()
            c = st.text_input("Contraseña", type="password")
            # ROLES ACTUALIZADOS SEGÚN TU PEDIDO
            r = st.selectbox("Especialidad / Rol", [
                "Maestro de Obra", 
                "Soldador", 
                "Cortador", 
                "Amolador", 
                "Pintor",
                "Ayudante Técnico"
            ])
            
            if st.form_submit_button("Guardar en Obra"):
                if n and u and c:
                    if u in df_u['Usuario'].astype(str).values:
                        st.error("El usuario ya existe.")
                    else:
                        nuevo = {"Nombre": n, "Usuario": u, "Clave": c, "Rol": r, "Tipo_Personal": "Obra", "Display": f"{n} ({r})"}
                        df_u = pd.concat([df_u, pd.DataFrame([nuevo])], ignore_index=True)
                        guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                        st.success(f"✅ {n} agregado como {r}")
                        st.rerun()

    st.divider()

    # --- 3. TABLA DE USUARIOS ---
    st.subheader("📋 Personal Registrado")
    if st.toggle("Ver Claves (Modo Admin)"):
        st.dataframe(df_u[['Nombre', 'Usuario', 'Clave', 'Rol', 'Tipo_Personal']], use_container_width=True)
    else:
        st.dataframe(df_u[['Nombre', 'Usuario', 'Rol', 'Tipo_Personal', 'Display']], use_container_width=True)

    st.divider()

    # --- 4. PANEL DE ELIMINACIÓN AL FINAL ---
    st.subheader("🗑️ Zona de Baja de Usuarios")
    with st.expander("⚠️ Abrir Panel de Eliminación"):
        # Aseguramos que 'jordan' NUNCA aparezca para ser borrado
        usuarios_list = df_u[df_u['Usuario'] != 'jordan']['Usuario'].tolist()
        if usuarios_list:
            u_del = st.selectbox("Seleccione usuario para eliminar:", usuarios_list)
            confirmar = st.checkbox(f"Estoy seguro de eliminar a {u_del}")
            if st.button("❌ Eliminar Permanentemente"):
                if confirmar:
                    df_u = df_u[df_u['Usuario'] != u_del]
                    guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                    st.success(f"Usuario {u_del} eliminado.")
                    st.rerun()
                else:
                    st.warning("Debes confirmar la casilla para eliminar.")
        else:
            st.info("No hay otros usuarios registrados.")
