import streamlit as st
import pandas as pd
import bcrypt
import time
from modulos import seguridad, inventario, movimientos, mantenimiento, empresas, usuarios, historial

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Jordan Admin Pro", layout="wide", page_icon="🛠️")

# --- 2. CARGA DE DATOS CON CACHÉ ---
@st.cache_data(ttl=600)
def cargar_datos(pestaña):
    try:
        df = pd.read_excel("database.xlsx", sheet_name=pestaña, dtype=str)
        if pestaña == "Usuarios" and not df.empty:
            df.columns = df.columns.str.strip()
            # Limpieza básica
            df['Usuario'] = df['Usuario'].astype(str).str.strip().str.lower()
            df['Nombre'] = df['Nombre'].astype(str).str.strip()
            df['Rol'] = df['Rol'].astype(str).str.strip()
            df['Ubicacion'] = df.get('Ubicacion', '').astype(str).str.strip()
            df['Correo'] = df.get('Correo', '').astype(str).str.strip()
            if 'Estado_Licencia' not in df.columns: df['Estado_Licencia'] = 'Activo'
        return df
    except: return pd.DataFrame()

# --- 3. GUARDADO GLOBAL ---
def guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera):
    try:
        with pd.ExcelWriter("database.xlsx", engine="openpyxl") as writer:
            df_inv.to_excel(writer, sheet_name="Inventario", index=False)
            df_mov.to_excel(writer, sheet_name="Movimientos", index=False)
            df_u.to_excel(writer, sheet_name="Usuarios", index=False)
            df_mant.to_excel(writer, sheet_name="Mantenimiento", index=False)
            df_lug.to_excel(writer, sheet_name="Lugares", index=False)
            df_papelera.to_excel(writer, sheet_name='Papelera', index=False)
        st.cache_data.clear()
        st.sidebar.success("💾 Base Actualizada")
    except Exception as e: st.error(f"❌ Error al guardar: {e}")

# --- 4. FUNCIÓN PARA EL DIÁLOGO DE EDICIÓN DE PERFIL (CENTRAL) ---
# Usamos experimental_dialog para que sea una ventana emergente central
@st.experimental_dialog("📝 Editar Mi Perfil")
def mostrar_modal_perfil(u_idx, df_u):
    st.write("Complete sus datos personales:")
    c1, c2 = st.columns(2)
    with c1:
        u_nom = st.text_input("Nombre Completo", df_u.at[u_idx, 'Nombre'])
        u_ubi = st.text_input("Ubicación (Dirección)", df_u.at[u_idx, 'Ubicacion'])
    with c2:
        u_cor = st.text_input("Correo Electrónico", df_u.at[u_idx, 'Correo'])
        u_fot = st.file_uploader("Actualizar foto de perfil (JPG/PNG)", type=['jpg','png','jpeg'])

    st.write("---")
    if st.button("💾 Guardar Cambios en Perfil", use_container_width=True):
        if not u_nom:
            st.error("Por favor, ingrese su nombre completo.")
        else:
            # Actualizamos el DataFrame
            df_u.at[u_idx, 'Nombre'] = u_nom
            df_u.at[u_idx, 'Ubicacion'] = u_ubi
            df_u.at[u_idx, 'Correo'] = u_cor
            # Nota: El guardado de la foto requiere una lógica extra de servidor/cloudinary.
            # Por ahora actualizamos los textos.
            
            guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
            st.session_state['nombre'] = u_nom # Actualizamos el nombre en sesión
            st.success("✅ Datos actualizados. La página se recargará.")
            time.sleep(1.5)
            st.rerun()

# --- 5. LÓGICA DE ACCESO (LOGIN) ---
if 'conectado' not in st.session_state: st.session_state['conectado'] = False

if not st.session_state['conectado']:
    st.title("🔐 Acceso Jordan Admin Pro")
    u_in = st.text_input("Usuario").strip()
    p_in = st.text_input("Contraseña", type="password")
    if st.button("🚀 Ingresar"):
        df_u_login = cargar_datos("Usuarios")
        if not df_u_login.empty:
            u_match = u_in.lower().strip()
            row = df_u_login[df_u_login['Usuario'] == u_match]
            if not row.empty:
                clave_ex = str(row.iloc[0]['Clave']).strip()
                valido = False
                if clave_ex.startswith('$2b$'):
                    try:
                        if bcrypt.checkpw(p_in.encode(), clave_ex.encode()): valido = True
                    except: pass
                if not valido and p_in == clave_ex: valido = True
                if valido:
                    st.session_state.update({'conectado': True, 'user': u_match, 'nombre': row.iloc[0]['Nombre'], 'rol': row.iloc[0]['Rol']})
                    st.cache_data.clear(); st.rerun()
                else: st.error("❌ Clave incorrecta")
            else: st.error("❌ Usuario no existe")

# --- 6. PANEL PRINCIPAL (AQUÍ ESTÁ LA NUEVA SIDEBAR) ---
else:
    df_inv = cargar_datos("Inventario"); df_mov = cargar_datos("Movimientos")
    df_u = cargar_datos("Usuarios"); df_mant = cargar_datos("Mantenimiento")
    df_lug = cargar_datos("Lugares"); df_papelera = cargar_datos("Papelera")

    with st.sidebar:
        st.title(f"👤 {st.session_state['nombre']}")
        # Lógica para mostrar la foto de perfil si existe (simulado con icono por defecto)
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80) 
        st.info(f"Rol: {st.session_state['rol']}")
        
        # --- LOS BOTONES DE LA SIDEBAR ---
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📝 Mi Perfil", use_container_width=True):
                # Buscamos el índice exacto de tu usuario en el DataFrame
                user_row = df_u[df_u['Usuario'] == st.session_state['user']]
                if not user_row.empty:
                    u_idx = user_row.index[0]
                    # Llamamos a la función de diálogo central
                    mostrar_modal_perfil(u_idx, df_u)
        with col2:
            if st.button("🚪 Salir", use_container_width=True):
                st.session_state['conectado'] = False
                st.cache_data.clear(); st.rerun()
        st.write("---")

    rol = st.session_state['rol']
    es_admin = any(x in rol for x in ["Desarrollador", "Administrador"])
    es_mando = any(x in rol for x in ["Desarrollador", "Administrador", "Supervisor", "Maestro de Obra"])
    tabs_n = ["📦 Inventario", "🔄 Movimientos"]
    if es_mando: tabs_n += ["🛠️ Mantenimiento", "🏢 Empresas"]
    if es_admin: tabs_n += ["👤 Usuarios", "📜 Historial"]
    tabs = st.tabs(tabs_n)
    with tabs[0]: inventario.mostrar(df_inv, guardar_global, df_mov, df_u, df_mant, df_lug, df_papelera)
    with tabs[1]: movimientos.mostrar(df_inv, df_mov, df_lug, st.session_state['user'], guardar_global, df_u, df_mant, df_papelera)
    try:
        if es_mando:
            with tabs[2]: mantenimiento.mostrar(df_mant, df_inv, guardar_global, df_mov, df_u, df_lug, df_papelera)
            with tabs[3]: empresas.mostrar(df_lug, guardar_global, df_inv, df_mov, df_u, df_mant, df_papelera)
        if es_admin:
            with tabs[4]: usuarios.mostrar(df_u, guardar_global, df_inv, df_mov, df_mant, df_lug, df_papelera)
            with tabs[5]: historial.mostrar(df_mov, guardar_global, df_inv, df_u, df_mant, df_lug, df_papelera)
    except: pass
