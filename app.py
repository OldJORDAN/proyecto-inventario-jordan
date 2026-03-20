import streamlit as st
import pandas as pd
import bcrypt
from modulos import seguridad, inventario, movimientos, mantenimiento, empresas, usuarios, historial

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Jordan Admin Pro", layout="wide", page_icon="🛠️")

# --- 2. CARGA DE DATOS (CON PARCHE MATEMÁTICO) ---
def cargar_datos(pestaña):
    try:
        # Leemos todo como texto para seguridad del login
        df = pd.read_excel("database.xlsx", sheet_name=pestaña, dtype=str)
        
        if pestaña == "Usuarios" and not df.empty:
            df.columns = df.columns.str.strip()
            df['Usuario'] = df['Usuario'].astype(str).str.strip().str.lower()
            df['Clave'] = df['Clave'].astype(str).str.strip()
            df['Rol'] = df['Rol'].astype(str).str.strip()
            if 'Estado_Licencia' not in df.columns: df['Estado_Licencia'] = 'Activo'
            df['Estado_Licencia'] = df['Estado_Licencia'].fillna('Activo')
        
        # --- ESTO ES LO QUE ARREGLA EL ERROR ROJO ---
        if pestaña == "Inventario" and not df.empty:
            if 'Stock' in df.columns:
                # Convertimos a número para que la pestaña Movimientos no explote
                df['Stock'] = pd.to_numeric(df['Stock'], errors='coerce').fillna(0).astype(int)
        
        if pestaña == "Movimientos" and not df.empty:
            if 'Cantidad' in df.columns:
                df['Cantidad'] = pd.to_numeric(df['Cantidad'], errors='coerce').fillna(0)
            
        return df
    except Exception as e:
        return pd.DataFrame()

# --- 3. LÓGICA DE LOGIN ---
if 'conectado' not in st.session_state: st.session_state['conectado'] = False

if not st.session_state['conectado']:
    st.title("🔐 Acceso Jordan Admin Pro")
    u_in = st.text_input("Usuario").strip().lower()
    p_in = st.text_input("Contraseña", type="password")
    
    if st.button("🚀 Ingresar"):
        df_u = cargar_datos("Usuarios")
        if not df_u.empty:
            row = df_u[df_u['Usuario'] == u_in]
            if not row.empty:
                hash_excel = str(row.iloc[0]['Clave'])
                estado = str(row.iloc[0]['Estado_Licencia'])
                
                if estado != "Activo":
                    st.error("🚫 LICENCIA DESHABILITADA")
                else:
                    try:
                        # Intento con Bcrypt (Tus claves encriptadas)
                        if bcrypt.checkpw(p_in.encode('utf-8'), hash_excel.encode('utf-8')):
                            match = True
                        else: match = False
                    except:
                        # Fallback por si la clave no está encriptada
                        match = (p_in == hash_excel)
                    
                    if match:
                        st.session_state.update({
                            'conectado': True, 'user': u_in, 
                            'nombre': row.iloc[0]['Nombre'], 'rol': row.iloc[0]['Rol']
                        })
                        st.rerun()
                    else: st.error("❌ Contraseña incorrecta")
            else: st.error(f"❌ Usuario '{u_in}' no encontrado")

# --- 4. PANEL PRINCIPAL ---
else:
    # Recargamos los datos ya limpios y con números reales
    df_inv = cargar_datos("Inventario")
    df_mov = cargar_datos("Movimientos")
    df_u = cargar_datos("Usuarios")
    df_mant = cargar_datos("Mantenimiento")
    df_lug = cargar_datos("Lugares")
    df_papelera = cargar_datos("Papelera")

    st.sidebar.title(f"👤 {st.session_state['nombre']}")
    st.sidebar.info(f"Rol: **{st.session_state['rol']}**")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['conectado'] = False
        st.rerun()

    # PERMISOS
    rol = st.session_state['rol']
    es_admin = any(x in rol for x in ["Desarrollador", "Administrador"])
    es_mando = any(x in rol for x in ["Desarrollador", "Administrador", "Supervisor", "Maestro de Obra"])
    
    lista_tabs = ["📦 Inventario", "🔄 Movimientos"]
    if es_mando: lista_tabs += ["🛠️ Mantenimiento", "🏢 Empresas"]
    if es_admin: lista_tabs += ["👤 Usuarios", "📜 Historial"]

    tabs = st.tabs(lista_tabs)
    
    # Aquí pasamos los DataFrames que ya tienen el Stock como número
    with tabs[0]: 
        inventario.mostrar(df_inv, None, df_mov, df_u, df_mant, df_lug, df_papelera)
    with tabs[1]: 
        movimientos.mostrar(df_inv, df_mov, df_lug, st.session_state['user'], None, df_u, df_mant, df_papelera)
    
    try:
        if es_mando:
            with tabs[2]: mantenimiento.mostrar(df_mant, df_inv, None, df_mov, df_u, df_lug, df_papelera)
            with tabs[3]: empresas.mostrar(df_lug, None, df_inv, df_mov, df_u, df_mant, df_papelera)
        if es_admin:
            with tabs[4]: usuarios.mostrar(df_u, None, df_inv, df_mov, df_mant, df_lug, df_papelera)
            with tabs[5]: historial.mostrar(df_mov, None, df_inv, df_u, df_mant, df_lug, df_papelera)
    except IndexError:
        pass
