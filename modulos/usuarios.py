import streamlit as st
import pandas as pd

def mostrar(df_u, guardar_global, df_inv, df_mov, df_mant, df_lug, df_papelera):
    st.title("👥 Gestión de Personal")

    # --- 1. SECCIÓN DE REGISTRO (OFICINA / OBRA) ---
    st.subheader("➕ Registro de Nuevo Personal")
    tab_oficina, tab_obra = st.tabs(["🏢 Registrar en Oficina", "👨‍🏭 Registrar en Taller / Obra"])

    with tab_oficina:
        with st.form("f_oficina"):
            n = st.text_input("Nombre y Apellido")
            u = st.text_input("ID Usuario").lower().strip()
            c = st.text_input("Contraseña (Oficina)", type="password")
            r = st.selectbox("Rol Administrativo", ["Administrador", "Supervisor", "Contador", "Logística"])
            if st.form_submit_button("Guardar en Oficina"):
                if n and u and c:
                    if not df_u.empty and u in df_u['Usuario'].astype(str).values:
                        st.error("❌ El usuario ya existe.")
                    else:
                        nuevo = pd.DataFrame([{
                            "Nombre": n, "Usuario": u, "Clave": c, "Rol": r, 
                            "Tipo_Personal": "Oficina", "Display": f"{n} ({r})"
                        }])
                        df_u = pd.concat([df_u, nuevo], ignore_index=True)
                        guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                        st.success(f"✅ {n} guardado en Oficina.")
                        st.rerun()

    with tab_obra:
        with st.form("f_obra"):
            n = st.text_input("Nombre y Apellido")
            u = st.text_input("ID Usuario Taller").lower().strip()
            c = st.text_input("Contraseña (Obra)", type="password")
            r = st.selectbox("Especialidad", ["Maestro de Obra", "Soldador", "Cortador", "Amolador", "Pintor", "Ayudante"])
            if st.form_submit_button("Guardar en Taller"):
                if n and u and c:
                    if not df_u.empty and u in df_u['Usuario'].astype(str).values:
                        st.error("❌ El usuario ya existe.")
                    else:
                        nuevo = pd.DataFrame([{
                            "Nombre": n, "Usuario": u, "Clave": c, "Rol": r, 
                            "Tipo_Personal": "Obra", "Display": f"{n} ({r})"
                        }])
                        df_u = pd.concat([df_u, nuevo], ignore_index=True)
                        guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                        st.success(f"✅ {n} guardado en Taller.")
                        st.rerun()

    st.divider()

    # --- 2. FILTROS DE VISTA (LO QUE PEDISTE) ---
    st.subheader("📋 Visualización de Personal")
    
    # Creamos tres columnas para los botones de filtro rápido
    filtro = st.radio(
        "Seleccione el grupo que desea visualizar:",
        ["Ver Todos", "Ver Oficina", "Ver Taller / Obra"],
        horizontal=True
    )

    # Lógica de filtrado del DataFrame
    if filtro == "Ver Oficina":
        df_mostrar = df_u[df_u['Tipo_Personal'] == "Oficina"]
    elif filtro == "Ver Taller / Obra":
        df_mostrar = df_u[df_u['Tipo_Personal'] == "Obra"]
    else:
        df_mostrar = df_u

    # Mostrar la tabla filtrada
    if not df_mostrar.empty:
        # Toggle para ver claves si es necesario
        ver_claves = st.toggle("🔑 Mostrar contraseñas (Modo Auditoría)")
        
        columnas = ['Nombre', 'Usuario', 'Rol', 'Tipo_Personal']
        if ver_claves:
            columnas.append('Clave')
            
        st.dataframe(df_mostrar[columnas], use_container_width=True)
        st.caption(f"Mostrando {len(df_mostrar)} registros.")
    else:
        st.info(f"No hay personal registrado en la categoría: {filtro}")

    st.divider()

    # --- 3. PANEL DE ELIMINACIÓN AL FINAL ---
    with st.expander("🗑️ Zona de Baja de Usuarios"):
        if not df_u.empty:
            # Lista de usuarios excluyendo tu cuenta maestra 'jordan'
            u_list = df_u[df_u['Usuario'] != 'jordan']['Usuario'].tolist()
            if u_list:
                sel = st.selectbox("Seleccionar usuario para borrar definitivamente:", u_list)
                confirmar = st.checkbox(f"Confirmo la eliminación permanente de {sel}")
                if st.button("❌ Ejecutar Baja"):
                    if confirmar:
                        df_u = df_u[df_u['Usuario'] != sel]
                        guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                        st.success(f"Usuario {sel} eliminado de la base de datos.")
                        st.rerun()
                    else:
                        st.warning("Debe marcar la casilla de confirmación.")
