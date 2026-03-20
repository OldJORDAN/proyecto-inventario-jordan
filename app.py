import streamlit as st
import pandas as pd
from modulos.seguridad import verificar_clave
from modulos import inventario, movimientos, mantenimiento, empresas, usuarios, historial

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Jordan Admin Pro", layout="wide", page_icon="🛠️")

# --- 2. DISEÑO ADAPTATIVO ---
def aplicar_diseno_jordan():
    st.markdown("""
        <style>
        h1 { color: #0078D4 !important; font-weight: 800; }
        .stTabs [data-baseweb="tab-list"] { gap: 8px; }
        .stTabs [data-baseweb="tab"] {
            padding: 10px 20px;
            font-weight: 600;
            border-radius: 5px 5px 0px 0px;
        }
        .stTabs [aria-selected="true"] {
            background-color: #0078D4 !important;
            color: white !important;
        }
        .stButton>button {
            border-radius: 10px;
            border: 1px solid #0078D4;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #0078D4 !important;
            color: white !important;
        }
        [data-testid="stForm"] {
            border: 1px solid rgba(128, 128, 128, 0.3);
            border-radius: 10px;
            padding: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

# --- 3. FUNCIONES DE BASE DE DATOS ---
def cargar_datos(pestaña):
    try:
        df = pd.read_excel("database.xlsx", sheet_name=pestaña)
        return df
    except Exception as e:
        columnas = {
            "Usuarios": ["Nombre", "Usuario", "Clave", "Rol", "Area"],
            "Papelera": ["Fecha_Eliminacion", "Admin_Que_Borro", "ID_Original", "Herramienta", "Marca", "Motivo"],
            "Inventario": ["ID", "Herramienta", "Marca", "Stock", "Lugar"],
            "Movimientos": ["Id_Historial", "Fecha", "Usuario_Admin", "ID", "Herramienta", "Marca", "Operario_Receptor", "Lugar", "Accion", "Cantidad"],
            "Mantenimiento": ["ID", "Herramienta", "Tipo de Mantenimiento", "Fecha de Ingreso", "Días Estimados", "Técnico Responsable", "Estado"],
            "Lugares": ["Empresa", "Ubicacion", "Responsable"],
            "Configuracion": ["Parametro", "Valor"]
        }
        return pd.DataFrame(columns=columnas.get(pestaña, []))

def guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera):
    with pd.ExcelWriter("database.xlsx", engine="openpyxl") as writer:
        df_inv.to_excel(writer, sheet_name="Inventario", index=False)
        df_mov.to_excel(writer, sheet_name="Movimientos", index=False)
        df_u.to_excel(writer, sheet_name="Usuarios", index=False)
        df_mant.to_excel(writer, sheet_name="Mantenimiento", index=False)
        df_lug.to_excel(writer, sheet_name="Lugares", index=False)
        df_papelera.to_excel(writer, sheet_name='Papelera', index=False)

# --- 4. SISTEMA DE SESIÓN Y SEGURIDAD ---
if 'conectado' not in st.session_state:
    st.session_state['conectado'] = False
if 'rol' not in st.session_state:
    st.session_state['rol'] = None
if 'intentos' not in st.session_state:
    st.session_state['intentos'] = 0

aplicar_diseno_jordan()

if not st.session_state['conectado']:
    st.title("🔐 Acceso Jordan Admin Pro")
    
    # --- CAPA DE BLOQUEO POR INTENTOS ---
    if st.session_state['intentos'] >= 3:
        st.error("🚫 **ACCESO BLOQUEADO:** Has fallado 3 veces. El sistema se ha cerrado por seguridad. Contacta a Jordan Damian.")
    else:
        u_input = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        
        if st.button("Ingresar Sistema"):
            # ANTI-HACKER: Limpieza de caracteres raros
            u = "".join(e for e in u_input if e.isalnum())
            
            df_u = cargar_datos("Usuarios")
            if not df_u.empty:
                user_row = df_u[df_u['Usuario'].astype(str) == u]
                if not user_row.empty:
                    if verificar_clave(p, str(user_row.iloc[0]['Clave'])):
                        st.session_state.update({
                            'conectado': True, 
                            'user': u, 
                            'nombre': user_row.iloc[0]['Nombre'],
                            'rol': user_row.iloc[0]['Rol'],
                            'intentos': 0 # Reset al entrar
                        })
                        st.rerun()
                    else: 
                        st.session_state['intentos'] += 1
                        st.error(f"❌ Contraseña incorrecta. Intento {st.session_state['intentos']}/3")
                else: 
                    st.session_state['intentos'] += 1
                    st.error(f"❌ Usuario no encontrado. Intento {st.session_state['intentos']}/3")

else:
    # Carga de datos
    df_inv = cargar_datos("Inventario")
    df_mov = cargar_datos("Movimientos")
    df_u = cargar_datos("Usuarios")
    df_mant = cargar_datos("Mantenimiento")
    df_lug = cargar_datos("Lugares")
    df_papelera = cargar_datos("Papelera")

    # Sidebar
    st.sidebar.title(f"👤 {st.session_state['nombre']}")
    st.sidebar.write(f"Rol: {st.session_state['rol']}")
    
    # --- MOSTRAR ESTADO DE LICENCIAS EN EL SIDEBAR ---
    try:
        df_conf = cargar_datos("Configuracion")
        limite = int(df_conf.loc[df_conf['Parametro'] == 'Limite_Usuarios', 'Valor'].values[0])
        st.sidebar.divider()
        st.sidebar.caption(f"📊 Licencias: {len(df_u)} / {limite}")
        st.sidebar.progress(min(len(df_u)/limite, 1.0))
    except:
        pass

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['conectado'] = False
        st.rerun()

    es_admin = st.session_state['rol'] in ["Desarrollador", "Supervisor"]
    
    # Tabs
    lista_tabs = ["📊 Inventario", "🔄 Movimientos", "🛠️ Mantenimiento", "🏢 Empresas"]
    if es_admin: lista_tabs += ["👤 Usuarios", "📜 Historial"]
    
    tabs = st.tabs(lista_tabs)

    # --- LLAMADA A MÓDULOS ---
    with tabs[0]: 
        inventario.mostrar(df_inv, guardar_global, df_mov, df_u, df_mant, df_lug, df_papelera)
    
    with tabs[1]: 
        movimientos.mostrar(df_inv, df_mov, df_lug, st.session_state['user'], guardar_global, df_u, df_mant, df_papelera)
    
    with tabs[2]: 
        mantenimiento.mostrar(df_mant, df_inv, guardar_global, df_mov, df_u, df_lug, df_papelera)
    
    with tabs[3]: 
        empresas.mostrar(df_lug, guardar_global, df_inv, df_mov, df_u, df_mant, df_papelera)
    
    if es_admin:
        with tabs[4]: 
            usuarios.mostrar(df_u, guardar_global, df_inv, df_mov, df_mant, df_lug, df_papelera)
        with tabs[5]: 
            historial.mostrar(df_mov, guardar_global, df_inv, df_u, df_mant, df_lug, df_papelera)
