import streamlit as st
import pandas as pd

def mostrar(df_u, guardar_global, df_inv, df_mov, df_mant, df_lug, df_papelera):
    st.title("👥 Gestión de Personal y Control de Licencias")

    # --- 1. BARRA DE LICENCIAS ---
    # Limpiamos espacios para evitar errores de conteo
    df_u['Usuario'] = df_u['Usuario'].astype(str).str.strip()
    df_reales = df_u[~df_u['Usuario'].str.contains('jordan', case=False, na=False)]
    
    st.write(f"**Uso de Licencias:** {len(df_reales)} de 50")
    st.progress(min(len(df_reales) / 50, 1.0))
    st.divider()

    # --- 2. REGISTRO (CON VALIDACIÓN DE DUPLICADOS) ---
    t1, t2 = st.tabs(["🏢 Oficina", "👨‍🏭 Taller / Obra"])
    
    with t1:
        with st.form("f_ofi_final"):
            n = st.text_input("Nombre Completo")
            u = st.text_input("Usuario (Nick)").lower().strip()
            c = st.text_input("Clave", type="password")
            r = st.selectbox("Rol", ["Administrador", "Supervisor", "Logística"])
            if st.form_submit_button("Registrar en Oficina"):
                if n and u:
                    if u in df_u['Usuario'].str.lower().values:
                        st.error(f"❌ El usuario '{u}' ya existe.")
                    else:
                        nuevo = pd.DataFrame([{"Nombre":n,"Usuario":u,"Clave":c,"Rol":r,"Tipo_Personal":"Oficina","Estado_Licencia":"Activo"}])
                        df_u = pd.concat([df_u, nuevo], ignore_index=True)
                        guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                        st.rerun()

    with t2:
        with st.form("f_obr_final"):
            n = st.text_input("Nombre Completo ")
            u = st.text_input("Usuario Taller").lower().strip()
            c = st.text_input("Clave ", type="password")
            r = st.selectbox("Especialidad", ["Maestro de Obra", "Soldador", "Cortador", "Amolador", "Pintor"])
            if st.form_submit_button("Registrar en Taller"):
                if n and u:
                    if u in df_u['Usuario'].str.lower().values:
                        st.error(f"❌ El usuario '{u}' ya existe.")
                    else:
                        nuevo = pd.DataFrame([{"Nombre":n,"Usuario":u,"Clave":c,"Rol":r,"Tipo_Personal":"Obra","Estado_Licencia":"Activo"}])
                        df_u = pd.concat([df_u, nuevo], ignore_index=True)
                        guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                        st.rerun()

    st.divider()

    # --- 3. PANEL DE CONTROL (CON PARCHE DE BORRADO) ---
    st.subheader("🛠️ Panel de Control")
    if not df_reales.empty:
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            # Lista limpia de usuarios para el selector
            lista_us = df_reales['Usuario'].tolist()
            u_sel = st.selectbox("Usuario para gestionar:", lista_us)
            # Buscamos el índice original
            idx_list = df_u[df_u['Usuario'] == u_sel].index.tolist()
            if idx_list:
                idx = idx_list[0]
                est = df_u.at[idx, 'Estado_Licencia']
            else:
                st.rerun() # Si no lo encuentra, refresca para evitar el error
        
        with c2:
            st.write(f"Estado: **{est}**")
            if st.button("🚫 Deshabilitar" if est=="Activo" else "✅ Habilitar", use_container_width=True):
                df_u.at[idx, 'Estado_Licencia'] = "Inactivo" if est=="Activo" else "Activo"
                guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                st.rerun()

        with c3:
            st.write("Zona de Peligro")
            if st.checkbox("Confirmar borrar", key="check_safe_del"):
                if st.button("🗑️ Eliminar", type="primary", use_container_width=True):
                    # ⚡ PARCHE: Borramos, reseteamos índice y guardamos
                    df_u = df_u.drop(idx).reset_index(drop=True)
                    guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                    st.rerun()

    st.divider()

    # --- 4. TABLA DE PERSONAL (VISTA SEGURA) ---
    st.subheader("📋 Personal Registrado")
    f_v = st.radio("Mostrar:", ["Todos", "Oficina", "Obra"], horizontal=True)
    
    # Recalculamos df_vista para que se actualice tras el borrado
    df_v = df_u[~df_u['Usuario'].str.contains('jordan', case=False, na=False)].copy()
    
    if f_v == "Oficina": df_v = df_v[df_v['Tipo_Personal'] == 'Oficina']
    elif f_v == "Obra": df_v = df_v[df_v['Tipo_Personal'] == 'Obra']

    if not df_v.empty:
        df_v['Estado_Licencia'] = df_v['Estado_Licencia'].replace('Inactivo', 'Deshabilitado')
        st.dataframe(
            df_v[['Nombre', 'Usuario', 'Rol', 'Tipo_Personal', 'Estado_Licencia']].style.applymap(
                lambda x: f'color: {"#28a745" if x == "Activo" else "#dc3545"}; font-weight: bold', 
                subset=['Estado_Licencia']
            ), 
            use_container_width=True
        )
    else:
        st.info("No hay personal registrado en esta categoría.")
