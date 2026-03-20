import streamlit as st
import pandas as pd

def mostrar(df_u, guardar_global, df_inv, df_mov, df_mant, df_lug, df_papelera):
    st.title("👥 Gestión de Usuarios y Licencias")

    # --- 1. LÍMITE DE LICENCIAS (Sigue igual) ---
    try:
        df_conf = pd.read_excel("database.xlsx", sheet_name="Configuracion")
        limite = int(df_conf.loc[df_conf['Parametro'] == 'Limite_Usuarios', 'Valor'].values[0])
    except:
        limite = 60

    usuarios_actuales = len(df_u)

    # --- 2. INTERFAZ DE ESTADO ---
    st.subheader("📊 Estado de Licencias")
    col_p, col_t = st.columns([3, 1])
    with col_p:
        st.progress(min(usuarios_actuales / limite, 1.0))
    with col_t:
        st.write(f"**{usuarios_actuales} / {limite}**")

    # --- 3. SECCIÓN DE REGISTRO (OFICINA / OBRA) Y ELIMINACIÓN ---
    col_reg, col_del = st.columns(2)

    with col_reg:
        with st.expander("➕ Registrar Nuevo Personal"):
            if usuarios_actuales >= limite:
                st.error("🚫 Límite alcanzado.")
            else:
                with st.form("nuevo_u"):
                    n = st.text_input("Nombre y Apellido")
                    u = st.text_input("ID de Acceso").lower().strip()
                    c = st.text_input("Clave", type="password")
                    r = st.selectbox("Rol", ["Operador", "Supervisor", "Administrador", "Maestro de Obra"])
                    # --- AQUÍ ESTÁ TU DIVISIÓN DE ÁREAS ---
                    a = st.selectbox("Área de Trabajo", ["Oficina", "Obra", "Logística", "Externo"])
                    
                    if st.form_submit_button("Guardar Registro"):
                        if n and u and c:
                            if u in df_u['Usuario'].astype(str).values:
                                st.error("Este usuario ya existe.")
                            else:
                                # Respetamos todas tus columnas originales
                                nuevo = {"Nombre": n, "Usuario": u, "Clave": c, "Rol": r, "Area": a}
                                df_u = pd.concat([df_u, pd.DataFrame([nuevo])], ignore_index=True)
                                guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                                st.success(f"¡{n} registrado en {a}!")
                                st.rerun()
                        else:
                            st.warning("Completa todos los datos.")

    with col_del:
        with st.expander("🗑️ Eliminar Personal"):
            # Filtramos para que no te borres tú mismo
            lista_usuarios = df_u[df_u['Usuario'] != 'jordan']['Usuario'].tolist()
            
            if not lista_usuarios:
                st.info("No hay otros usuarios para gestionar.")
            else:
                u_sel = st.selectbox("Usuario a eliminar:", lista_usuarios)
                seguro = st.checkbox(f"Confirmar eliminación de {u_sel}")
                
                if st.button("❌ Eliminar Permanentemente"):
                    if seguro:
                        df_u = df_u[df_u['Usuario'] != u_sel]
                        guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                        st.success(f"Usuario {u_sel} eliminado.")
                        st.rerun()
                    else:
                        st.warning("Marca la casilla de confirmación.")

    st.divider()
    
    # --- 4. TABLA DE CONTROL CON TUS COLUMNAS ---
    st.subheader("📋 Lista de Personal Registrado")
    
    # Selector para ver por área
    filtro_area = st.multiselect("Filtrar por Área:", ["Oficina", "Obra", "Logística", "Externo"], default=["Oficina", "Obra"])
    
    df_filtrado = df_u[df_u['Area'].isin(filtro_area)] if filtro_area else df_u

    if st.toggle("Ver Claves (Modo Admin)"):
        st.dataframe(df_filtrado[['Nombre', 'Usuario', 'Clave', 'Rol', 'Area']], use_container_width=True)
    else:
        st.dataframe(df_filtrado[['Nombre', 'Usuario', 'Rol', 'Area']], use_container_width=True)
