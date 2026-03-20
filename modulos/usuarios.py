import streamlit as st
import pandas as pd

def mostrar(df_u, guardar_global, df_inv, df_mov, df_mant, df_lug, df_papelera):
    st.title("👥 Gestión de Personal y Control de Licencias")

    # --- 1. BARRA DE ESTADO DE LICENCIAS ---
    try:
        df_conf = pd.read_excel("database.xlsx", sheet_name="Configuracion")
        limite = int(df_conf.loc[df_conf['Parametro'] == 'Limite_Usuarios', 'Valor'].values[0])
    except:
        limite = 60

    usuarios_actuales = len(df_u)
    st.progress(min(usuarios_actuales / limite, 1.0))
    st.write(f"**Uso de Licencias:** {usuarios_actuales} de {limite}")

    # Aseguramos que la columna 'Estado_Licencia' exista en el DataFrame
    if 'Estado_Licencia' not in df_u.columns:
        df_u['Estado_Licencia'] = 'Activo'

    st.divider()

    # --- 2. REGISTRO DE PERSONAL ---
    tab1, tab2 = st.tabs(["🏢 Oficina", "👨‍🏭 Taller / Obra"])
    
    with tab1:
        with st.form("reg_oficina"):
            n = st.text_input("Nombre")
            u = st.text_input("Usuario").lower().strip()
            c = st.text_input("Clave")
            r = st.selectbox("Rol", ["Administrador", "Supervisor", "Logística"])
            if st.form_submit_button("Registrar en Oficina"):
                if n and u and c:
                    nuevo = pd.DataFrame([{"Nombre": n, "Usuario": u, "Clave": c, "Rol": r, "Tipo_Personal": "Oficina", "Estado_Licencia": "Activo", "Display": f"{n} ({r})"}])
                    df_u = pd.concat([df_u, nuevo], ignore_index=True)
                    guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                    st.success("Usuario Creado")
                    st.rerun()

    with tab2:
        with st.form("reg_obra"):
            n = st.text_input("Nombre")
            u = st.text_input("Usuario Obra").lower().strip()
            c = st.text_input("Clave")
            r = st.selectbox("Especialidad", ["Maestro de Obra", "Soldador", "Cortador", "Amolador", "Pintor"])
            if st.form_submit_button("Registrar en Obra"):
                if n and u and c:
                    nuevo = pd.DataFrame([{"Nombre": n, "Usuario": u, "Clave": c, "Rol": r, "Tipo_Personal": "Obra", "Estado_Licencia": "Activo", "Display": f"{n} ({r})"}])
                    df_u = pd.concat([df_u, nuevo], ignore_index=True)
                    guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                    st.success("Personal de Obra Registrado")
                    st.rerun()

    st.divider()

    # --- 3. PANEL DE CONTROL DE LICENCIAS (SOLO PARA TI) ---
    st.subheader("🛠️ Panel de Control de Acceso (Solo Desarrollador)")
    
    # Solo mostramos usuarios que no sean 'jordan' para no deshabilitarte a ti mismo
    u_gestionables = df_u[df_u['Usuario'] != 'jordan']
    
    if not u_gestionables.empty:
        col_u, col_st, col_bt = st.columns([2, 1, 1])
        
        with col_u:
            user_sel = st.selectbox("Seleccione Usuario para gestionar:", u_gestionables['Usuario'].tolist())
        
        # Obtener estado actual
        estado_actual = df_u.loc[df_u['Usuario'] == user_sel, 'Estado_Licencia'].values[0]
        
        with col_st:
            st.write(f"Estado: **{estado_actual}**")
        
        with col_bt:
            label_btn = "🚫 Deshabilitar" if estado_actual == "Activo" else "✅ Habilitar"
            if st.button(label_btn):
                nuevo_estado = "Inactivo" if estado_actual == "Activo" else "Activo"
                df_u.loc[df_u['Usuario'] == user_sel, 'Estado_Licencia'] = nuevo_estado
                guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                st.toast(f"Usuario {user_sel} marcado como {nuevo_estado}")
                st.rerun()
    
    st.divider()
    
    # --- 4. TABLA DE VISUALIZACIÓN ---
    filtro = st.radio("Mostrar:", ["Todos", "Oficina", "Obra"], horizontal=True)
    df_v = df_u if filtro == "Todos" else df_u[df_u['Tipo_Personal'] == filtro.replace("Ver ", "")]
    
    # Pintamos la tabla
    def color_estado(val):
        color = 'red' if val == 'Inactivo' else 'green'
        return f'color: {color}; font-weight: bold'

    st.dataframe(df_v[['Nombre', 'Usuario', 'Rol', 'Estado_Licencia']].style.applymap(color_estado, subset=['Estado_Licencia']), use_container_width=True)
