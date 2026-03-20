import streamlit as st
import pandas as pd
import bcrypt
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
            df['Usuario'] = df['Usuario'].astype(str).str.strip()
            if 'Estado_Licencia' not in df.columns: df['Estado_Licencia'] = 'Activo'
            df['Estado_Licencia'] = df['Estado_Licencia'].fillna('Activo')
        
        if pestaña == "Inventario" and not df.empty:
            if 'Stock' in df.columns:
                df['Stock'] = pd.to_numeric(df['Stock'], errors='coerce').fillna(0).astype(int)
        
        if pestaña == "Movimientos" and not df.empty:
            if 'Cantidad' in df.columns:
                df['Cantidad'] = pd.to_numeric(df['Cantidad'], errors='coerce').fillna(0)
            
        return df
    except:
        return pd.DataFrame()

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
        st.sidebar.success("💾 ¡Sincronizado!")
    except Exception as e:
        st.error(f"❌ Error: {e}")

# --- 4. LOGIN INTELIGENTE ---
if 'conectado' not in st.session_state: st.session_state['conectado'] = False

if not st.session_state['conectado']:
    st.title("🔐 Acceso Jordan Admin Pro")
    u_in = st.text_input("Usuario").strip()
    p_in = st.text_input("Contraseña", type="password")
    
    if st.button("🚀 Ingresar"):
        df_u_login = cargar_datos("Usuarios")
        if not df_u_login.empty:
            u_buscado = u_in.lower().strip()
            df_u_login['Usuario_Match'] = df_u_login['Usuario'].astype(str).str.lower().str.strip()
            row = df_u_login[df_u_login['Usuario_Match'] == u_buscado]
            
            if not row.empty:
                clave_ex = str(row.iloc[0]['Clave']).strip()
                if str(row.iloc[0].get('Estado_Licencia', 'Activo')) != "Activo":
                    st.error("🚫 LICENCIA DESHABILITADA")
                else:
                    valido = False
                    if clave_ex.startswith('$2b$'):
                        try:
                            if bcrypt.checkpw(p_in.encode(), clave_ex.encode()): valido = True
                        except: pass
                    if not valido and p_in == clave_ex: valido = True
                    
                    if valido:
                        st.session_state.update({'conectado': True, 'user': u_buscado, 'nombre': row.iloc[0]['Nombre'], 'rol': row.iloc[0]['Rol']})
                        st.cache_data.clear()
                        st.rerun()
                    else: st.error("❌ Clave incorrecta")
            else: st.error("❌ Usuario no existe")

# --- 5. PANEL PRINCIPAL ---
else:
    df_inv = cargar_datos("Inventario"); df_mov = cargar_datos("Movimientos")
    df_u = cargar_datos("Usuarios"); df_mant = cargar_datos("Mantenimiento")
    df_lug = cargar_datos("Lugares"); df_papelera = cargar_datos("Papelera")

    with st.sidebar:
        st.title(f"👤 {st.session_state['nombre']}")
        st.info(f"Rol: {st.session_state['rol']}")
        if st.button("🚪 Cerrar Sesión"):
            st.session_state['conectado'] = False
            st.cache_data.clear()
            st.rerun()

    rol = st.session_state['rol']
    es_admin = any(x in rol for x in ["Desarrollador", "Administrador"])
    es_mando = any(x in rol for x in ["Desarrollador", "Administrador", "Supervisor", "Maestro de Obra"])
    
    tabs_nombres = ["📦 Inventario", "🔄 Movimientos"]
    if es_mando: tabs_nombres += ["🛠️ Mantenimiento", "🏢 Empresas"]
    if es_admin: tabs_nombres += ["👤 Usuarios", "📜 Historial"]

    tabs = st.tabs(tabs_nombres)
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
