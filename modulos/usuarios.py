import streamlit as st
import pandas as pd

def mostrar(df_u, guardar_global, df_inv, df_mov, df_mant, df_lug, df_papelera):
    st.title("👥 Gestión de Personal y Control de Acceso")

    # --- 1. BARRA DE LICENCIAS (SIN CONTAR AL DESARROLLADOR) ---
    # Filtramos al usuario 'jordan' para el conteo
    df_personal_real = df_u[~df_u['Usuario'].str.contains('jordan', case=False, na=False)]
    usuarios_actuales = len(df_personal_real)
    
    st.write(f"**Uso de Licencias:** {usuarios_actuales} de 50")
    st.progress(min(usuarios_actuales / 50, 1.0))
    st.divider()

    # --- 2. REGISTRO (OFICINA / TALLER) ---
    st.subheader("➕ Registro de Nuevo Personal")
    t1, t2 = st.tabs(["🏢 Oficina", "👨‍🏭 Taller / Obra"])
    with t1:
        with st.form("f_ofi"):
            n = st.text_input("Nombre Completo")
            u = st.text_input("Usuario ID").lower().strip()
            c = st.text_input("Contraseña ", type="password")
            r = st.selectbox("Rol", ["Administrador", "Supervisor", "Logística"])
            if st.form_submit_button("Registrar en Oficina"):
                if n and u:
                    nuevo = pd.DataFrame([{"Nombre":n,"Usuario":u,"Clave":c,"Rol":r,"Tipo_Personal":"Oficina","Estado_Licencia":"Activo"}])
                    df_u = pd.concat([df_u, nuevo], ignore_index=True)
                    guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                    st.rerun()

    with t2:
        with st.form("f_obr"):
            n = st.text_input("Nombre Completo ")
            u = st.text_input("ID Taller").lower().strip()
            c = st.text_input("Contraseña  ", type="password")
            r = st.selectbox("Especialidad", ["Maestro de Obra", "Soldador", "Cortador", "Amolador", "Pintor"])
            if st.form_submit_button("Registrar en Taller"):
                if n and u:
                    nuevo = pd.DataFrame([{"Nombre":n,"Usuario":u,"Clave":c,"Rol":r,"Tipo_Personal":"Obra","Estado_Licencia":"Activo"}])
                    df_u = pd.concat([df_u, nuevo], ignore_index=True)
                    guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                    st.rerun()

    st.divider()

    # --- 3. PANEL DE CONTROL (SOLO PARA EL DESARROLLADOR) ---
    mi_rol = str(st.session_state.get('rol', '')).lower().strip()
    if "desarrollador" in mi_rol:
        st.subheader("🛠️ Panel de Control de Acceso")
        
        # Usamos df_personal_real para que no te puedas seleccionar a ti mismo
        if not df_personal_real.empty:
            c1, c2, c3 = st.columns(3)
            with c1:
                u_sel = st.selectbox("Seleccione Usuario:", df_personal_real['Usuario'].tolist())
                idx = df_u[df_u['Usuario'] == u_sel].index[0]
                est = df_u.at[idx, 'Estado_Licencia']
                st.write(f"Estado: **{est}**")
            with c2:
                st.write("¿Cambiar acceso?")
                txt_bt = "🚫 Deshabilitar" if est == "Activo" else "✅ Habilitar"
                if st.button(txt_bt, use_container_width=True):
                    df_u.at[idx, 'Estado_Licencia'] = "Inactivo" if est == "Activo" else "Activo"
                    guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                    st.rerun()
            with c3:
                st.write("¿Borrar cuenta?")
                if st.checkbox("Confirmar borrar", key="del_u_check"):
                    if st.button("🗑️ Eliminar", type="primary", use_container_width=True):
                        df_u = df_u.drop(idx)
                        guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                        st.rerun()
        else:
            st.info("No hay otros usuarios para gestionar.")

    st.divider()

    # --- 4. FILTROS Y VISTA (TODOS / OFICINA / OBRA) ---
    st.subheader("📋 Personal Registrado")
    filtro = st.radio("Mostrar:", ["Todos", "Oficina", "Obra"], horizontal=True)
    
    # IMPORTANTE: Aquí también usamos df_personal_real para que TÚ no salgas en la tabla
    df_v = df_personal_real.copy()
    
    if filtro == "Oficina":
        df_v = df_v[df_v['Tipo_Personal'] == 'Oficina']
    elif filtro == "Obra":
        df_v = df_v[df_v['Tipo_Personal'] == 'Obra']

    df_v['Estado_Licencia_Vista'] = df_v['Estado_Licencia'].replace('Inactivo', 'Deshabilitado')
    
    def style_estado(val):
        color = '#28a745' if val == 'Activo' else '#dc3545'
        return f'color: {color}; font-weight: bold'

    st.dataframe(
        df_v[['Nombre', 'Usuario', 'Rol', 'Tipo_Personal', 'Estado_Licencia_Vista']].style.applymap(
            style_estado, subset=['Estado_Licencia_Vista']
        ), 
        use_container_width=True
    )
