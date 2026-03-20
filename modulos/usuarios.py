import streamlit as st
import pandas as pd

def mostrar(df_u, guardar_global, df_inv, df_mov, df_mant, df_lug, df_papelera):
    st.title("👥 Gestión de Personal y Licencias")

    # --- 1. BARRA DE LICENCIAS (TU SEGURO) ---
    try:
        # Intentamos leer el límite desde la configuración del Excel
        df_conf = pd.read_excel("database.xlsx", sheet_name="Configuracion")
        limite = int(df_conf.loc[df_conf['Parametro'] == 'Limite_Usuarios', 'Valor'].values[0])
    except:
        # Si falla el Excel, ponemos 60 por defecto para que no explote
        limite = 60

    usuarios_actuales = len(df_u)
    
    # Diseño de la barra de licencias
    st.subheader("📊 Estado de Licencias Jordan Admin Pro")
    col_bar, col_txt = st.columns([4, 1])
    
    with col_bar:
        # Cambia de color si se acerca al límite (opcional en CSS, aquí estándar)
        porcentaje = min(usuarios_actuales / limite, 1.0)
        st.progress(porcentaje)
    
    with col_txt:
        st.write(f"**{usuarios_actuales} / {limite}**")
        
    if usuarios_actuales >= limite:
        st.error(f"🚫 **LÍMITE ALCANZADO:** No puedes registrar más personal ({limite}/{limite}).")
    else:
        st.info(f"✅ Tienes cupo para **{limite - usuarios_actuales}** licencias adicionales.")

    st.divider()

    # --- 2. REGISTRO DE NUEVO PERSONAL ---
    st.subheader("➕ Registro de Nuevo Personal")
    tab_oficina, tab_obra = st.tabs(["🏢 Registrar en Oficina", "👨‍🏭 Registrar en Taller / Obra"])

    with tab_oficina:
        with st.form("f_oficina"):
            n = st.text_input("Nombre y Apellido")
            u = st.text_input("ID Usuario").lower().strip()
            c = st.text_input("Contraseña", type="password")
            r = st.selectbox("Rol Oficina", ["Administrador", "Supervisor", "Contador", "Logística"])
            if st.form_submit_button("Guardar en Oficina"):
                if usuarios_actuales >= limite:
                    st.error("No hay licencias disponibles.")
                elif n and u and c:
                    nuevo = pd.DataFrame([{"Nombre": n, "Usuario": u, "Clave": c, "Rol": r, "Tipo_Personal": "Oficina", "Display": f"{n} ({r})"}])
                    df_u = pd.concat([df_u, nuevo], ignore_index=True)
                    guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                    st.success("✅ Registrado en Oficina")
                    st.rerun()

    with tab_obra:
        with st.form("f_obra"):
            n = st.text_input("Nombre y Apellido")
            u = st.text_input("ID Usuario Taller").lower().strip()
            c = st.text_input("Contraseña", type="password")
            r = st.selectbox("Especialidad", ["Maestro de Obra", "Soldador", "Cortador", "Amolador", "Pintor", "Ayudante"])
            if st.form_submit_button("Guardar en Taller"):
                if usuarios_actuales >= limite:
                    st.error("No hay licencias disponibles.")
                elif n and u and c:
                    nuevo = pd.DataFrame([{"Nombre": n, "Usuario": u, "Clave": c, "Rol": r, "Tipo_Personal": "Obra", "Display": f"{n} ({r})"}])
                    df_u = pd.concat([df_u, nuevo], ignore_index=True)
                    guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                    st.success("✅ Registrado en Taller")
                    st.rerun()

    st.divider()

    # --- 3. FILTROS DE VISTA ---
    st.subheader("📋 Visualización de Personal")
    filtro = st.radio(
        "Filtrar lista por:",
        ["Ver Todos", "Ver Oficina", "Ver Taller / Obra"],
        horizontal=True
    )

    if filtro == "Ver Oficina":
        df_mostrar = df_u[df_u['Tipo_Personal'] == "Oficina"]
    elif filtro == "Ver Taller / Obra":
        df_mostrar = df_u[df_u['Tipo_Personal'] == "Obra"]
    else:
        df_mostrar = df_u

    if not df_mostrar.empty:
        ver_claves = st.toggle("🔑 Ver contraseñas (Solo Admin)")
        cols = ['Nombre', 'Usuario', 'Rol', 'Tipo_Personal']
        if ver_claves: cols.append('Clave')
        st.dataframe(df_mostrar[cols], use_container_width=True)
    else:
        st.info("No hay personal en esta categoría.")

    st.divider()

    # --- 4. PANEL DE ELIMINACIÓN AL FINAL ---
    with st.expander("🗑️ Zona de Baja de Usuarios"):
        u_list = df_u[df_u['Usuario'] != 'jordan']['Usuario'].tolist()
        if u_list:
            sel = st.selectbox("Usuario a eliminar:", u_list)
            conf = st.checkbox(f"Confirmo que quiero borrar a {sel}")
            if st.button("❌ Ejecutar Baja"):
                if conf:
                    df_u = df_u[df_u['Usuario'] != sel]
                    guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                    st.success(f"Usuario {sel} eliminado.")
                    st.rerun()
