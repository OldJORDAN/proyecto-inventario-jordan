import streamlit as st
import pandas as pd
from modulos import seguridad, inventario, movimientos, mantenimiento, empresas, usuarios, historial

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Jordan Admin Pro", layout="wide", page_icon="🛠️")

# --- 2. DISEÑO ADAPTATIVO ---
def aplicar_diseno_jordan():
    st.markdown("""
        <style>
        h1 { color: #0078D4 !important; font-weight: 800; }
        .stButton>button { border-radius: 10px; width: 100%; transition: 0.3s; }
        .stButton>button:hover { background-color: #0078D4 !important; color: white !important; }
        .sidebar .sidebar-content { background-color: #f0f2f6; }
        </style>
    """, unsafe_allow_html=True)

# --- 3. FUNCIONES DE BASE DE DATOS ---
def cargar_datos(pestaña):
    try:
        df = pd.read_excel("database.xlsx", sheet_name=pestaña)
        # Limpieza automática de Stock para evitar errores en Movimientos
        if pestaña == "Inventario" and "Stock" in df.columns:
            df['Stock'] = pd.to_numeric(df['Stock'], errors='coerce').fillna(0).astype(int)
        return df
    except:
        return pd.DataFrame()

def guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera):
    try:
        with pd.ExcelWriter("database.xlsx", engine="openpyxl") as writer:
            df_inv.to_excel(writer, sheet_name="Inventario", index=False)
            df_mov.to_excel(writer, sheet_name="Movimientos", index=False)
            df_u.to_excel(writer, sheet_name="Usuarios", index=False)
            df_mant.to_excel(writer, sheet_name="Mantenimiento", index=False)
            df_lug.to_excel(writer, sheet_name="Lugares", index=False)
            df_papelera.to_excel(writer, sheet_name='Papelera', index=False)
    except Exception as e:
        st.error(f"Error al guardar: {e}")

# --- 4. SISTEMA DE SESIÓN Y SEGURIDAD ---
if 'conectado' not in st.session_state: st.session_state['conectado'] = False
if 'intentos' not in st.session_state: st.session_state['intentos'] = 0

aplicar_diseno_jordan()

# --- LÓGICA DE ACCESO (LOGIN) ---
if not st.session_state['conectado']:
    st.title("🔐 Acceso Jordan Admin Pro")
    
    if st.session_state['intentos'] >= 3:
        st.error("🚫 **SISTEMA BLOQUEADO:** Has fallado 3 veces.")
        if st.button("🔄 Resetear Intentos (Solo Jordan)"):
            st.session_state['intentos'] = 0
            st.rerun()
        st.stop()
    
    u_in = st.text_input("Usuario")
    p_in = st.text_input("Contraseña", type="password")
    
    if st.button("🚀 Ingresar al Sistema"):
        u_l = u_in.strip().lower()
        
        # 1. Verificar contra LLAVE MAESTRA
        es_m, rol_m = seguridad.verificar_clave(u_l, p_in, None)
        
        if es_m and rol_m == "Desarrollador":
            st.session_state.update({'conectado': True, 'user': u_l, 'nombre': "Jordan (Master)", 'rol': "Desarrollador", 'intentos': 0})
            st.rerun()
        else:
            # 2. Verificar contra EXCEL
            df_u = cargar_datos("Usuarios")
            if not df_u.empty:
                df_u['Match'] = df_u['Usuario'].astype(str).str.strip().str.lower()
                row = df_u[df_u['Match'] == u_l]
                
                if not row.empty:
                    valido, _ = seguridad.verificar_clave(u_l, p_in, row.iloc[0]['Clave'])
                    if valido:
                        st.session_state.update({
                            'conectado': True, 'user': u_l, 
                            'nombre': row.iloc[0]['Nombre'], 
                            'rol': row.iloc[0]['Rol'], 
                            'intentos': 0
                        })
                        st.rerun()
                    else:
                        st.session_state['intentos'] += 1
                        st.error(f"❌ Clave incorrecta ({st.session_state['intentos']}/3)")
                else:
                    st.session_state['intentos'] += 1
                    st.error("❌ Usuario no registrado.")

# --- 5. PANEL DE CONTROL (USUARIO AUTENTICADO) ---
else:
    # Carga masiva de datos
    df_inv = cargar_datos("Inventario")
    df_mov = cargar_datos("Movimientos")
    df_u = cargar_datos("Usuarios")
    df_mant = cargar_datos("Mantenimiento")
    df_lug = cargar_datos("Lugares")
    df_papelera = cargar_datos("Papelera")

    # Sidebar informativo
    st.sidebar.title(f"👤 {st.session_state['nombre']}")
    st.sidebar.info(f"Rol Actual: **{st.session_state['rol']}**")
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['conectado'] = False
        st.rerun()

    # --- LÓGICA DE PERMISOS ---
    rol = st.session_state['rol']
    
    # Definimos quién ve qué
    es_jefe = rol in ["Desarrollador", "Administrador", "Supervisor"]
    es_maestro = rol in ["Desarrollador", "Administrador", "Supervisor", "Maestro de Obra"]
    
    # Pestañas para Operarios / Soldadores (Básico)
    lista_tabs = ["📦 Inventario", "🔄 Movimientos"]
    
    # Pestañas para Maestros de Obra (Mantenimiento y Empresas)
    if es_maestro:
        lista_tabs += ["🛠️ Mantenimiento", "🏢 Empresas"]
    
    # Pestañas para Jefes (Usuarios)
    if es_jefe:
        lista_tabs += ["👤 Usuarios"]
        
    # Pestaña solo para TI (Historial)
    if rol == "Desarrollador":
        lista_tabs += ["📜 Historial"]

    # Crear los Tabs
    tabs = st.tabs(lista_tabs)

    # Mostrar contenido según la lista creada
    with tabs[0]: 
        inventario.mostrar(df_inv, guardar_global, df_mov, df_u, df_mant, df_lug, df_papelera)
    with tabs[1]: 
        movimientos.mostrar(df_inv, df_mov, df_lug, st.session_state['user'], guardar_global, df_u, df_mant, df_papelera)
    
    # Usamos manejo de errores para evitar que explote si el rol no tiene acceso a las siguientes
    try:
        if es_maestro:
            with tabs[2]: mantenimiento.mostrar(df_mant, df_inv, guardar_global, df_mov, df_u, df_lug, df_papelera)
            with tabs[3]: empresas.mostrar(df_lug, guardar_global, df_inv, df_mov, df_u, df_mant, df_papelera)
        if es_jefe:
            with tabs[4]: usuarios.mostrar(df_u, guardar_global, df_inv, df_mov, df_mant, df_lug, df_papelera)
        if rol == "Desarrollador":
            with tabs[5]: historial.mostrar(df_mov, guardar_global, df_inv, df_u, df_mant, df_lug, df_papelera)
    except IndexError:
        pass
