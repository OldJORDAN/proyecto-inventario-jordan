import streamlit as st
import pandas as pd

def mostrar(df_u, guardar_global, df_inv, df_mov, df_mant, df_lug, df_papelera):
    st.title("👥 Gestión de Personal y Control de Acceso")

    # --- 1. BARRA DE LICENCIAS ---
    try:
        df_conf = pd.read_excel("database.xlsx", sheet_name="Configuracion")
        limite = int(df_conf.loc[df_conf['Parametro'] == 'Limite_Usuarios', 'Valor'].values[0])
    except:
        limite = 50

    usuarios_actuales = len(df_u)
    st.write(f"**Uso de Licencias:** {usuarios_actuales} de {limite}")
    st.progress(min(usuarios_actuales / limite, 1.0))

    st.divider()

    # --- 2. REGISTRO DE PERSONAL ---
    tab_ofi, tab_obr = st.tabs(["🏢 Oficina", "👨‍🏭 Taller / Obra"])
    
    with tab_ofi:
        with st.form("form_oficina"):
            n = st.text_input("Nombre Completo")
            u = st.text_input("Usuario ID").lower().strip()
            c = st.text_input("Contraseña", type="password")
            r = st.selectbox("Rol", ["Administrador", "Supervisor", "Logística"])
            if st.form_submit_button("Registrar en Oficina"):
                if n and u and c:
                    nuevo = pd.DataFrame([{"Nombre": n, "Usuario": u, "Clave": c, "Rol": r, "Tipo_Personal": "Oficina", "Estado_Licencia": "Activo", "Display": f"{n} ({r})"}])
                    df_u = pd.concat([df_u, nuevo], ignore_index=True)
                    guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                    st.success("✅ Registrado")
                    st.rerun()

    with tab_obr:
        with st.form("form_obra"):
            n = st.text_input("Nombre Completo")
            u = st.text_input("Usuario ID Taller").lower().strip()
            c = st.text_input("Contraseña", type="password")
            r = st.selectbox("Especialidad", ["Maestro de Obra", "Soldador", "Cortador", "Amolador", "Pintor"])
            if st.form_submit_button("Registrar en Taller"):
                if n and u and c:
                    nuevo = pd.DataFrame([{"Nombre": n, "Usuario": u, "Clave": c, "Rol": r, "Tipo_Personal": "Obra", "Estado_Licencia": "Activo", "Display": f"{n} ({r})"}])
                    df_u = pd.concat([df_u, nuevo], ignore_index=True)
                    guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                    st.success("✅ Registrado")
                    st.rerun()

    st.divider()

    # --- 3. PANEL DE CONTROL (PARA DESARROLLADOR) ---
    mi_rol = str(st.session_state.get('rol', '')).lower().strip()
    
    if "desarrollador" in mi_rol:
        st.subheader("🛠️ Panel de Control de Acceso (Solo Desarrollador)")
        u_gest = df_u[df_u['Usuario'] != 'jordan']
        
        if not u_gest.empty:
            c1, c2, c3 = st.columns(3)
            
            with c1:
                u_sel = st.selectbox("Seleccione Usuario:", u_gest['Usuario'].tolist(), key="admin_gest")
                idx = df_u[df_u['Usuario'] == u_sel].index[0]
                est_act = df_u.at[idx, 'Estado_Licencia']
                st.write(f"Estado actual: **{est_act}**")

            with c2:
                st.write("¿Cambiar acceso?")
                txt_bt = "✅ Habilitar" if est_act == "Inactivo" else "🚫 Deshabilitar"
                if st.button(txt_bt, use_container_width=True):
                    df_u.at[idx, 'Estado_Licencia'] = "Inactivo" if est_act == "Activo" else "Activo"
                    guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                    st.rerun()

            with c3:
                st.write("¿Borrar para siempre?")
                confirma_borrar = st.checkbox("Confirmar eliminación", key="del_chk")
                if st.button("🗑️ Eliminar Usuario", type="primary", use_container_width=True):
                    if confirma_borrar:
                        df_u = df_u[df_u['Usuario'] != u_sel]
                        guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                        st.success("Usuario eliminado")
                        st.rerun()
                    else:
                        st.warning("Marca la casilla")
        st.divider()

    # --- 4. VISTA DE TABLA CON COLORES ---
    st.subheader("📋 Personal Registrado")
    
    # Preparamos vista (Inactivo -> Deshabilitado)
    df_v = df_u[['Nombre', 'Usuario', 'Rol', 'Tipo_Personal', 'Estado_Licencia']].copy()
    df_v['Estado_Licencia'] = df_v['Estado_Licencia'].replace('Inactivo', 'Deshabilitado')

    # Función de color: Verde para Activo, Rojo para Deshabilitado
    def style_estado(val):
        color = '#28a745' if val == 'Activo' else '#dc3545'
        return f'color: {color}; font-weight: bold'

    st.dataframe(df_v.style.applymap(style_estado, subset=['Estado_Licencia']), use_container_width=True)
