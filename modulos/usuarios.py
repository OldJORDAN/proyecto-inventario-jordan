import streamlit as st
import pandas as pd

def mostrar(df_u, guardar_global, df_inv, df_mov, df_mant, df_lug, df_papelera):
    st.title("👥 Gestión de Usuarios y Licencias")

    # --- 1. LÍMITE DE LICENCIAS ---
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

    # --- 3. SECCIÓN DE REGISTRO Y ELIMINACIÓN ---
    col_reg, col_del = st.columns(2)

    with col_reg:
        with st.expander("➕ Registrar Nuevo Personal"):
            if usuarios_actuales >= limite:
                st.error("🚫 Límite alcanzado.")
            else:
                with st.form("nuevo_u"):
                    n = st.text_input("Nombre Completo")
                    u = st.text_input("Usuario (ID)").lower().strip()
                    c = st.text_input("Clave", type="password")
                    r = st.selectbox("Rol", ["Operador", "Supervisor", "Administrador", "Maestro de Obra", "Desarrollador"])
                    # --- USAMOS TU COLUMNA: Tipo_Personal ---
                    tp = st.selectbox("Tipo de Personal", ["Oficina", "Obra", "Externo"])
                    
                    if st.form_submit_button("Guardar Registro"):
                        if n and u and c:
                            if not df_u.empty and u in df_u['Usuario'].astype(str).values:
                                st.error("Este usuario ya existe.")
                            else:
                                # Creamos el Display como lo tienes en tu Excel
                                display_val = f"{n} ({r})"
                                
                                nuevo = {
                                    "Nombre": n, 
                                    "Usuario": u, 
                                    "Clave": c, 
                                    "Rol": r, 
                                    "Tipo_Personal": tp,
                                    "Display": display_val
                                }
                                
                                df_u = pd.concat([df_u, pd.DataFrame([nuevo])], ignore_index=True)
                                guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                                st.success(f"¡{n} registrado!")
                                st.rerun()
                        else:
                            st.warning("Completa todos los datos.")

    with col_del:
        with st.expander("🗑️ Eliminar Personal"):
            if not df_u.empty:
                # Evitamos borrar al admin maestro
                lista_usuarios = df_u[df_u['Usuario'] != 'jordan']['Usuario'].tolist()
                if lista_usuarios:
                    u_sel = st.selectbox("Usuario a eliminar:", lista_usuarios)
                    seguro = st.checkbox(f"Confirmar eliminación de {u_sel}")
                    if st.button("❌ Eliminar Permanentemente"):
                        if seguro:
                            df_u = df_u[df_u['Usuario'] != u_sel]
                            guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                            st.success(f"Usuario {u_sel} eliminado.")
                            st.rerun()
                else:
                    st.info("No hay otros usuarios.")
            else:
                st.info("Tabla vacía.")

    st.divider()
    
    # --- 4. TABLA DE CONTROL (AJUSTADA A TU EXCEL) ---
    st.subheader("📋 Lista de Personal Registrado")
    
    # Verificamos qué columnas existen realmente en tu Excel de la foto
    columnas_disponibles = df_u.columns.tolist()
    
    # Columnas que queremos mostrar (las tuyas)
    columnas_base = [c for c in ['Nombre', 'Usuario', 'Rol', 'Tipo_Personal', 'Display'] if c in columnas_disponibles]
    
    # Filtro dinámico por Tipo_Personal
    if 'Tipo_Personal' in columnas_disponibles:
        tipos = df_u['Tipo_Personal'].unique().tolist()
        filtro_tp = st.multiselect("Filtrar por Tipo de Personal:", tipos, default=tipos)
        df_filtrado = df_u[df_u['Tipo_Personal'].isin(filtro_tp)] if filtro_tp else df_u
    else:
        df_filtrado = df_u

    if st.toggle("Ver Claves (Modo Admin)"):
        columnas_admin = [c for c in ['Nombre', 'Usuario', 'Clave', 'Rol', 'Tipo_Personal'] if c in columnas_disponibles]
        st.dataframe(df_filtrado[columnas_admin], use_container_width=True)
    else:
        st.dataframe(df_filtrado[columnas_base], use_container_width=True)
