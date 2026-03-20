import streamlit as st
import pandas as pd

def mostrar(df_u, guardar_global, df_inv, df_mov, df_mant, df_lug, df_papelera):
    st.title("👥 Gestión de Personal y Control de Acceso")

    # --- 1. BARRA DE LICENCIAS ---
    # Contamos a todos menos a ti (jordan) para el uso de licencias
    df_reales = df_u[~df_u['Usuario'].str.contains('jordan', case=False, na=False)]
    st.write(f"**Uso de Licencias:** {len(df_reales)} de 50")
    st.progress(min(len(df_reales) / 50, 1.0))
    st.divider()

    # --- 2. REGISTRO (OFICINA / OBRA) ---
    t1, t2 = st.tabs(["🏢 Oficina", "👨‍🏭 Taller / Obra"])
    with t1:
        with st.form("form_oficina"):
            n = st.text_input("Nombre Completo")
            u = st.text_input("Usuario ID").lower().strip()
            c = st.text_input("Contraseña", type="password")
            r = st.selectbox("Rol", ["Administrador", "Supervisor", "Logística"])
            if st.form_submit_button("Registrar en Oficina"):
                if n and u:
                    nuevo = pd.DataFrame([{"Nombre":n,"Usuario":u,"Clave":c,"Rol":r,"Tipo_Personal":"Oficina","Estado_Licencia":"Activo"}])
                    df_u = pd.concat([df_u, nuevo], ignore_index=True)
                    guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                    st.rerun()

    with t2:
        with st.form("form_obra"):
            n = st.text_input("Nombre Completo ")
            u = st.text_input("Usuario ID Taller").lower().strip()
            c = st.text_input("Contraseña ", type="password")
            r = st.selectbox("Especialidad", ["Maestro de Obra", "Soldador", "Cortador", "Amolador", "Pintor"])
            if st.form_submit_button("Registrar en Taller"):
                if n and u:
                    nuevo = pd.DataFrame([{"Nombre":n,"Usuario":u,"Clave":c,"Rol":r,"Tipo_Personal":"Obra","Estado_Licencia":"Activo"}])
                    df_u = pd.concat([df_u, nuevo], ignore_index=True)
                    guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                    st.rerun()

    st.divider()

    # --- 3. PANEL DE CONTROL (CON JERARQUÍA) ---
    mi_rol = str(st.session_state.get('rol', '')).lower().strip()
    
    if "desarrollador" in mi_rol or "administrador" in mi_rol:
        st.subheader("🛠️ Panel de Control de Acceso")
        if not df_reales.empty:
            es_dev = "desarrollador" in mi_rol
            # Si eres Desarrollador ves 3 columnas, si eres Admin ves 2 (sin Eliminar)
            cols = st.columns(3 if es_dev else 2)
            
            with cols[0]:
                u_sel = st.selectbox("Seleccione Usuario:", df_reales['Usuario'].tolist())
                idx = df_u[df_u['Usuario'] == u_sel].index[0]
                est = df_u.at[idx, 'Estado_Licencia']
                st.write(f"Estado actual: **{est}**")

            with cols[1]:
                st.write("¿Cambiar acceso?")
                txt_bt = "🚫 Deshabilitar" if est == "Activo" else "✅ Habilitar"
                if st.button(txt_bt, use_container_width=True):
                    df_u.at[idx, 'Estado_Licencia'] = "Inactivo" if est == "Activo" else "Activo"
                    guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                    st.rerun()

            if es_dev:
                with cols[2]:
                    st.write("¿Borrar para siempre?")
                    if st.checkbox("Confirmar eliminación", key="del_check_user"):
                        if st.button("🗑️ Eliminar Usuario", type="primary", use_container_width=True):
                            df_u = df_u.drop(idx)
                            guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                            st.rerun()
    st.divider()

    # --- 4. TABLA DE PERSONAL (LO QUE QUERÍAS QUE REGRESE) ---
    st.subheader("📋 Personal Registrado")
    # Filtro rápido
    filtro = st.radio("Mostrar:", ["Todos", "Oficina", "Obra"], horizontal=True)
    
    df_v = df_reales.copy() # Tú no apareces en la tabla
    if filtro == "Oficina":
        df_v = df_v[df_v['Tipo_Personal'] == 'Oficina']
    elif filtro == "Obra":
        df_v = df_v[df_v['Tipo_Personal'] == 'Obra']

    df_v['Estado_Licencia'] = df_v['Estado_Licencia'].replace('Inactivo', 'Deshabilitado')
    
    def style_estado(val):
        color = '#28a745' if val == 'Activo' else '#dc3545'
        return f'color: {color}; font-weight: bold'

    st.dataframe(
        df_v[['Nombre', 'Usuario', 'Rol', 'Tipo_Personal', 'Estado_Licencia']].style.applymap(
            style_estado, subset=['Estado_Licencia']
        ), use_container_width=True
    )
