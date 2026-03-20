import streamlit as st
import pandas as pd

def mostrar(df_u, guardar_global, df_inv, df_mov, df_mant, df_lug, df_papelera):
    st.title("👥 Gestión de Personal y Control de Licencias")

    # --- 1. BARRA DE LICENCIAS ---
    # Limpieza de datos por seguridad
    df_u['Usuario'] = df_u['Usuario'].astype(str).str.strip().str.lower()
    
    # Filtramos para el conteo (No contamos a 'jordan' que eres tú)
    df_reales = df_u[~df_u['Usuario'].str.contains('jordan', case=False, na=False)].copy()
    
    u_cont = len(df_reales)
    st.write(f"**Uso de Licencias:** {u_cont} de 50")
    st.progress(min(u_cont / 50, 1.0))
    st.divider()

    # --- 2. REGISTRO DE PERSONAL (OFICINA / OBRA) ---
    tab_reg1, tab_reg2 = st.tabs(["🏢 Oficina", "👨‍🏭 Taller / Obra"])
    
    with tab_reg1:
        with st.form("form_registro_oficina"):
            n = st.text_input("Nombre Completo")
            u = st.text_input("Usuario (Nick)").lower().strip()
            c = st.text_input("Clave de Acceso", type="password")
            r = st.selectbox("Rol del Usuario", ["Administrador", "Supervisor", "Logística"])
            if st.form_submit_button("🚀 Registrar en Oficina"):
                if n and u and c:
                    if u in df_u['Usuario'].values:
                        st.error(f"❌ El usuario '{u}' ya existe. Prueba con otro.")
                    else:
                        nuevo = pd.DataFrame([{"Nombre":n,"Usuario":u,"Clave":c,"Rol":r,"Tipo_Personal":"Oficina","Estado_Licencia":"Activo"}])
                        df_u = pd.concat([df_u, nuevo], ignore_index=True)
                        guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                        st.success(f"✅ Usuario {u} creado con éxito.")
                        st.rerun()
                else:
                    st.warning("Completa todos los campos.")

    with tab_reg2:
        with st.form("form_registro_obra"):
            n = st.text_input("Nombre Completo ")
            u = st.text_input("Usuario Taller").lower().strip()
            c = st.text_input("Clave Taller", type="password")
            r = st.selectbox("Especialidad", ["Maestro de Obra", "Soldador", "Cortador", "Amolador", "Pintor"])
            if st.form_submit_button("🛠️ Registrar en Taller"):
                if n and u and c:
                    if u in df_u['Usuario'].values:
                        st.error(f"❌ El usuario '{u}' ya existe.")
                    else:
                        nuevo = pd.DataFrame([{"Nombre":n,"Usuario":u,"Clave":c,"Rol":r,"Tipo_Personal":"Obra","Estado_Licencia":"Activo"}])
                        df_u = pd.concat([df_u, nuevo], ignore_index=True)
                        guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                        st.success(f"✅ Usuario {u} creado.")
                        st.rerun()

    st.divider()

    # --- 3. PANEL DE CONTROL (GESTIÓN DIRECTA) ---
    st.subheader("🛠️ Panel de Control de Acceso")
    if not df_reales.empty:
        c1, c2, c3 = st.columns([2, 1, 1])
        
        with c1:
            u_sel = st.selectbox("Seleccione Usuario para gestionar:", df_reales['Usuario'].tolist(), key="sel_user_v4")
            # Extraer datos del seleccionado
            user_info = df_u[df_u['Usuario'] == u_sel]
            if not user_info.empty:
                idx = user_info.index[0]
                est_act = df_u.at[idx, 'Estado_Licencia']
                st.write(f"Estado Actual: **{est_act}**")
            else:
                st.rerun()

        with c2:
            st.write("Acción")
            bt_txt = "🚫 Deshabilitar" if est_act == "Activo" else "✅ Habilitar"
            if st.button(bt_txt, use_container_width=True):
                df_u.at[idx, 'Estado_Licencia'] = "Inactivo" if est_act == "Activo" else "Activo"
                guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                st.rerun()

        with c3:
            st.write("Seguridad")
            if st.checkbox("Confirmar borrar", key="check_del_v4"):
                if st.button("🗑️ Eliminar Usuario", type="primary", use_container_width=True):
                    df_u = df_u.drop(idx).reset_index(drop=True)
                    guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                    st.rerun()
    else:
        st.info("💡 No hay personal registrado para gestionar.")

    st.divider()

    # --- 4. LISTA DE PERSONAL (TABLA FIJA) ---
    st.subheader("📋 Personal Registrado")
    
    # Filtro visual rápido
    f_vista = st.radio("Filtrar Tabla:", ["Todos", "Oficina", "Obra"], horizontal=True, key="rad_v4")
    
    df_v = df_reales.copy()
    if f_vista == "Oficina": df_v = df_v[df_v['Tipo_Personal'] == 'Oficina']
    elif f_vista == "Obra": df_v = df_v[df_v['Tipo_Personal'] == 'Obra']

    if not df_v.empty:
        df_v['Estado_Licencia'] = df_v['Estado_Licencia'].replace('Inactivo', 'Deshabilitado')
        
        # Estilo de colores
        def aplicar_color(val):
            color = '#28a745' if val == 'Activo' else '#dc3545'
            return f'color: {color}; font-weight: bold'

        st.dataframe(
            df_v[['Nombre', 'Usuario', 'Rol', 'Tipo_Personal', 'Estado_Licencia']].style.applymap(
                aplicar_color, subset=['Estado_Licencia']
            ), 
            use_container_width=True
        )
    else:
        st.warning("⚠️ No se encontraron registros en esta categoría.")
