import streamlit as st
import pandas as pd
import bcrypt
from modulos import seguridad, inventario, movimientos, mantenimiento, empresas, usuarios, historial

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Jordan Admin Pro", layout="wide", page_icon="🛠️")

# --- 2. CARGA DE DATOS (CON LIMPIEZA EXTREMA) ---
def cargar_datos(pestaña):
    try:
        df = pd.read_excel("database.xlsx", sheet_name=pestaña, dtype=str)
        if pestaña == "Usuarios" and not df.empty:
            df.columns = df.columns.str.strip()
            # Limpiamos espacios y pasamos a minúsculas para que no falle el login
            df['Usuario'] = df['Usuario'].astype(str).str.strip().str.lower()
            df['Clave'] = df['Clave'].astype(str).str.strip()
            df['Rol'] = df['Rol'].astype(str).str.strip() # Limpiamos el Rol
            if 'Estado_Licencia' not in df.columns: df['Estado_Licencia'] = 'Activo'
            df['Estado_Licencia'] = df['Estado_Licencia'].fillna('Activo')
        return df
    except:
        return pd.DataFrame()

# --- 3. LOGIN CON BCRYPT ---
if 'conectado' not in st.session_state: st.session_state['conectado'] = False

if not st.session_state['conectado']:
    st.title("🔐 Acceso Jordan Admin Pro")
    u_in = st.text_input("Usuario").strip().lower() # Siempre en minúsculas
    p_in = st.text_input("Contraseña", type="password")
    
    if st.button("🚀 Ingresar"):
        df_u = cargar_datos("Usuarios")
        if not df_u.empty:
            # Buscamos al usuario sin importar mayúsculas
            row = df_u[df_u['Usuario'] == u_in]
            
            if not row.empty:
                hash_excel = str(row.iloc[0]['Clave'])
                estado = str(row.iloc[0]['Estado_Licencia'])
                
                if estado != "Activo":
                    st.error("🚫 LICENCIA DESHABILITADA")
                else:
                    # PROBAMOS BCRYPT
                    try:
                        match = bcrypt.checkpw(p_in.encode('utf-8'), hash_excel.encode('utf-8'))
                    except:
                        match = (p_in == hash_excel) # Fallback si no es un hash
                    
                    if match:
                        st.session_state.update({
                            'conectado': True, 
                            'user': u_in, 
                            'nombre': row.iloc[0]['Nombre'], 
                            'rol': row.iloc[0]['Rol']
                        })
                        st.rerun()
                    else: st.error("❌ Contraseña incorrecta")
            else: st.error(f"❌ El usuario '{u_in}' no existe en el Excel")
        else: st.error("❌ Base de datos vacía o no encontrada")

# --- 4. PANEL PRINCIPAL ---
else:
    # CARGA DE TODO
    df_inv = cargar_datos("Inventario"); df_mov = cargar_datos("Movimientos")
    df_u = cargar_datos("Usuarios"); df_mant = cargar_datos("Mantenimiento")
    df_lug = cargar_datos("Lugares"); df_papelera = cargar_datos("Papelera")

    st.sidebar.title(f"👤 {st.session_state['nombre']}")
    st.sidebar.write(f"Rol: **{st.session_state['rol']}**")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['conectado'] = False
        st.rerun()

    # --- LÓGICA DE PERMISOS (REVISA QUE TUS ROLES EN EXCEL SEAN IGUALES A ESTOS) ---
    rol = st.session_state['rol']
    
    # Aquí está el truco: usamos "in" para evitar errores de espacios
    es_admin = any(x in rol for x in ["Desarrollador", "Administrador"])
    es_mando = any(x in rol for x in ["Desarrollador", "Administrador", "Supervisor", "Maestro de Obra"])
    
    lista_tabs = ["📦 Inventario", "🔄 Movimientos"]
    if es_mando: lista_tabs += ["🛠️ Mantenimiento", "🏢 Empresas"]
    if es_admin: lista_tabs += ["👤 Usuarios", "📜 Historial"]

    tabs = st.tabs(lista_tabs)
    
    # MOSTRAR CONTENIDO
    with tabs[0]: inventario.mostrar(df_inv, None, df_mov, df_u, df_mant, df_lug, df_papelera)
    with tabs[1]: movimientos.mostrar(df_inv, df_mov, df_lug, st.session_state['user'], None, df_u, df_mant, df_papelera)
    
    try:
        if es_mando:
            with tabs[2]: mantenimiento.mostrar(df_mant, df_inv, None, df_mov, df_u, df_lug, df_papelera)
            with tabs[3]: empresas.mostrar(df_lug, None, df_inv, df_mov, df_u, df_mant, df_papelera)
        if es_admin:
            with tabs[4]: usuarios.mostrar(df_u, None, df_inv, df_mov, df_mant, df_lug, df_papelera)
            with tabs[5]: historial.mostrar(df_mov, None, df_inv, df_u, df_mant, df_lug, df_papelera)
    except: pass
