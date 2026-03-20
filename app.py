import streamlit as st
import pandas as pd
import bcrypt
import time
from modulos import seguridad, inventario, movimientos, mantenimiento, empresas, usuarios, historial

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Jordan Admin Pro", layout="wide", page_icon="🛠️")

# --- 2. CARGA DE DATOS (CON PROTECCIÓN DE LECTURA) ---
def cargar_datos(pestaña):
    # Quitamos el @st.cache_data aquí para que siempre lea lo más fresco sin errores de limpieza
    try:
        # Forzamos la lectura fresca del archivo
        df = pd.read_excel("database.xlsx", sheet_name=pestaña, dtype=str)
        
        if pestaña == "Usuarios" and not df.empty:
            df.columns = df.columns.str.strip()
            df['Usuario'] = df['Usuario'].astype(str).str.strip().str.lower()
            if 'Estado_Licencia' not in df.columns: df['Estado_Licencia'] = 'Activo'
            
        return df
    except Exception as e:
        # Si falla (porque el excel está ocupado), reintentamos un segundo después
        time.sleep(0.5)
        try:
            return pd.read_excel("database.xlsx", sheet_name=pestaña, dtype=str)
        except:
            return pd.DataFrame()

# --- 3. GUARDADO GLOBAL (OPTIMIZADO) ---
def guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera):
    try:
        with pd.ExcelWriter("database.xlsx", engine="openpyxl") as writer:
            df_inv.to_excel(writer, sheet_name="Inventario", index=False)
            df_mov.to_excel(writer, sheet_name="Movimientos", index=False)
            df_u.to_excel(writer, sheet_name="Usuarios", index=False)
            df_mant.to_excel(writer, sheet_name="Mantenimiento", index=False)
            df_lug.to_excel(writer, sheet_name="Lugares", index=False)
            df_papelera.to_excel(writer, sheet_name='Papelera', index=False)
        
        # IMPORTANTE: No limpiamos todo el cache, solo dejamos que Streamlit siga
        st.sidebar.success("💾 ¡Cambios Guardados!")
    except Exception as e:
        st.error(f"❌ Error Crítico: {e}")

# --- 4. LOGIN ---
if 'conectado' not in st.session_state: st.session_state['conectado'] = False

if not st.session_state['conectado']:
    st.title("🔐 Acceso Jordan Admin Pro")
    u_in = st.text_input("Usuario").strip().lower()
    p_in = st.text_input("Contraseña", type="password")
    if st.button("🚀 Ingresar"):
        df_u_login = cargar_datos("Usuarios")
        if not df_u_login.empty:
            row = df_u_login[df_u_login['Usuario'] == u_in]
            if not row.empty:
                clave_ex = str(row.iloc[0]['Clave']).strip()
                valido = False
                if clave_ex.startswith('$2b$'):
                    try:
                        if bcrypt.checkpw(p_in.encode(), clave_ex.encode()): valido = True
                    except: pass
                if not valido and p_in == clave_ex: valido = True
                
                if valido:
                    st.session_state.update({'conectado': True, 'user': u_in, 'nombre': row.iloc[0]['Nombre'], 'rol': row.iloc[0]['Rol']})
                    st.rerun()
                else: st.error("❌ Clave incorrecta")
            else: st.error("❌ Usuario no existe")

# --- 5. PANEL PRINCIPAL ---
else:
    # Cargamos datos directamente
    df_inv = cargar_datos("Inventario"); df_mov = cargar_datos("Movimientos")
    df_u = cargar_datos("Usuarios"); df_mant = cargar_datos("Mantenimiento")
    df_lug = cargar_datos("Lugares"); df_papelera = cargar_datos("Papelera")

    with st.sidebar:
        st.title(f"👤 {st.session_state['nombre']}")
        st.info(f"Rol: {st.session_state['rol']}")
        if st.button("🚪 Cerrar Sesión"):
            st.session_state['conectado'] = False
            st.rerun()

    rol = st.session_state['rol']
    es_admin = any(x in rol for x in ["Desarrollador", "Administrador"])
    es_mando = any(x in rol for x in ["Desarrollador", "Administrador", "Supervisor", "Maestro de Obra"])
    
    tabs_n = ["📦 Inventario", "🔄 Movimientos"]
    if es_mando: tabs_n += ["🛠️ Mantenimiento", "🏢 Empresas"]
    if es_admin: tabs_n += ["👤 Usuarios", "📜 Historial"]
    
    tabs = st.tabs(tabs_n)
    with tabs[0]: inventario.mostrar(df_inv, guardar_global, df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
    with tabs[1]: movimientos.mostrar(df_inv, df_mov, df_lug, st.session_state['user'], guardar_global, df_u, df_mant, df_papelera)
    
    try:
        if es_mando:
            with tabs[2]: mantenimiento.mostrar(df_mant, df_inv, guardar_global, df_mov, df_u, df_lug, df_papelera)
            with tabs[3]: empresas.mostrar(df_lug, guardar_global, df_inv, df_mov, df_u, df_mant, df_papelera)
        if es_admin:
            with tabs[4]: usuarios.mostrar(df_u, guardar_global, df_inv, df_mov, df_mant, df_lug, df_papelera)
            with tabs[5]: historial.mostrar(df_mov, guardar_global, df_inv, df_u, df_mant, df_lug, df_papelera)
    except: pass
