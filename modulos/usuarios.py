import streamlit as st
import pandas as pd

def mostrar(df_u, guardar_global, df_inv, df_mov, df_mant, df_lug, df_papelera):
    st.title("👥 Gestión de Personal y Control de Licencias")

    # --- 1. BARRA DE LICENCIAS (CONTEO REAL) ---
    df_u['Usuario'] = df_u['Usuario'].astype(str).str.strip()
    # No te contamos a ti (jordan) para la licencia
    df_reales = df_u[~df_u['Usuario'].str.contains('jordan', case=False, na=False)].copy()
    
    u_cont = len(df_reales)
    st.write(f"**Uso de Licencias:** {u_cont} de 50")
    st.progress(min(u_cont / 50, 1.0))
    st.divider()

    # --- 2. REGISTRO DE PERSONAL (OFICINA / OBRA) ---
    tab_o1, tab_o2 = st.tabs(["🏢 Oficina", "👨‍🏭 Taller / Obra"])
    
    with tab_o1:
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
                        st.success(f"✅ {u} registrado")
                        st.rerun()

    with tab_o2:
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
                        st.success(f"✅ {u} registrado")
                        st.rerun()

    st.divider()

    # --- 3. PANEL DE CONTROL (PARA GESTIONAR A LOS DEMÁS) ---
    st.subheader("🛠️ Panel de Control")
    # SALVAVIDAS: Solo mostramos el panel si hay alguien a quien gestionar
    if not df_reales.empty:
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            u_sel = st.selectbox("Usuario para gestionar:", df_reales['Usuario'].tolist())
            user_data = df_u[df_u['Usuario'] == u_sel]
            if not user_data.empty:
                idx = user_data.index[0]
                est = df_u.at[idx, 'Estado_Licencia']
                st.write(f"Estado: **{est}**")
            else: st.rerun()
        
        with c2:
            st.write("Acceso")
            if st.button("🚫 Deshabilitar" if est=="Activo" else "✅ Habilitar", use_container_width=True):
                df_u.at[idx, 'Estado_Licencia'] = "Inactivo" if est=="Activo" else "Activo"
                guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                st.rerun()

        with c3:
            st.write("Zona de Peligro")
            if st.checkbox("Confirmar borrar", key="safe_del_pacth_v2"):
                if st.button("🗑️ Eliminar Usuario", type="primary", use_container_width=True):
                    df_u = df_u.drop(idx).reset_index(drop=True)
                    guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                    st.rerun()
    else:
        # Esto es lo que sale en tu captura (porque borraste a todos)
        st.info("No hay personal para gestionar en este momento. Registra a alguien arriba.")

    st.divider()

    # --- 4. LA PESTAÑA (EXPANDIDA POR DEFECTO Y SIEMPRE VISIBLE) ---
    # PARCHE: Esta línea ahora está fuera de cualquier condición, siempre se dibuja.
    with st.expander("📋 Ver Lista de Personal Registrado", expanded=True):
        if not df_reales.empty:
            f_v = st.radio("Filtrar vista:", ["Todos", "Oficina", "Obra"], horizontal=True)
            
            # Recalculamos df_v con los datos más frescos
            df_vista_f = df_reales.copy()
            if f_v == "Oficina": df_vista_f = df_vista_f[df_vista_f['Tipo_Personal'] == 'Oficina']
            elif f_v == "Obra": df_vista_f = df_vista_f[df_vista_f['Tipo_Personal'] == 'Obra']

            if not df_vista_f.empty:
                df_vista_f['Estado_Licencia'] = df_vista_f['Estado_Licencia'].replace('Inactivo', 'Deshabilitado')
                st.dataframe(
                    df_vista_f[['Nombre', 'Usuario', 'Rol', 'Tipo_Personal', 'Estado_Licencia']].style.applymap(
                        lambda x: f'color: {"#28a745" if x == "Activo" else "#dc3545"}; font-weight: bold', 
                        subset=['Estado_Licencia']
                    ), 
                    use_container_width=True
                )
            else:
                st.warning("⚠️ No hay registros para mostrar en esta categoría.")
        else:
            # Si no hay usuarios reales, sale este aviso DENTRO de la pestaña
            st.info("💡 La lista de personal está vacía. Registra usuarios para que aparezcan aquí.")
