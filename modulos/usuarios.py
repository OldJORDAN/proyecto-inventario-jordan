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

    # --- 3. SECCIÓN PARA AGREGAR Y ELIMINAR ---
    col_add, col_del = st.columns(2)

    with col_add:
        with st.expander("➕ Registrar Nuevo Usuario"):
            if usuarios_actuales >= limite:
                st.error("🚫 Límite alcanzado. No puedes agregar más.")
            else:
                with st.form("nuevo_u"):
                    n = st.text_input("Nombre Completo")
                    u = st.text_input("ID Usuario").lower().strip()
                    c = st.text_input("Clave", type="password")
                    r = st.selectbox("Rol", ["Operador", "Supervisor", "Administrador"])
                    
                    if st.form_submit_button("Guardar Registro"):
                        if n and u and c:
                            if u in df_u['Usuario'].astype(str).values:
                                st.error("Ese ID de usuario ya existe.")
                            else:
                                nuevo = {"Nombre": n, "Usuario": u, "Clave": c, "Rol": r, "Area": "General"}
                                df_u = pd.concat([df_u, pd.DataFrame([nuevo])], ignore_index=True)
                                guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                                st.success(f"Usuario {u} creado.")
                                st.rerun()
                        else:
                            st.warning("Llena todos los campos.")

    with col_del:
        with st.expander("🗑️ Eliminar Usuario"):
            # No permitimos que te borres a ti mismo (Jordan Master)
            usuarios_borrables = df_u[df_u['Usuario'] != 'jordan']['Usuario'].tolist()
            
            if not usuarios_borrables:
                st.info("No hay otros usuarios para eliminar.")
            else:
                u_para_borrar = st.selectbox("Seleccione usuario a eliminar:", usuarios_borrables)
                confirmar = st.checkbox(f"Confirmo que quiero eliminar a {u_para_borrar}")
                
                if st.button("❌ Ejecutar Eliminación"):
                    if confirmar:
                        df_u = df_u[df_u['Usuario'] != u_para_borrar]
                        guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                        st.success(f"Usuario {u_para_borrar} eliminado correctamente.")
                        st.rerun()
                    else:
                        st.warning("Debes marcar la casilla de confirmación.")

    st.divider()
    
    # --- 4. TABLA DE CONTROL ---
    st.subheader("📋 Lista de Personal")
    # Mostramos la clave solo si eres Jordan Master para que puedas recuperarlas
    if st.toggle("Mostrar credenciales"):
        st.dataframe(df_u[['Nombre', 'Usuario', 'Clave', 'Rol']], use_container_width=True)
    else:
        st.dataframe(df_u[['Nombre', 'Usuario', 'Rol']], use_container_width=True)
