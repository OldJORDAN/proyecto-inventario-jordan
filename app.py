import streamlit as st
import pandas as pd
from modulos import seguridad, inventario, movimientos, mantenimiento, empresas, usuarios, historial

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Jordan Admin Pro", layout="wide", page_icon="🛠️")

# --- 2. DISEÑO ADAPTATIVO (SIN FORZAR COLORES DE FONDO) ---
def aplicar_diseno_jordan():
    st.markdown("""
        <style>
        /* Títulos que siempre se vean bien */
        h1, h2, h3 { color: #0078D4 !important; font-weight: 800; }
        
        /* Estilo de botones para que resalten en cualquier tema */
        .stButton>button { 
            border-radius: 10px; 
            width: 100%; 
            transition: 0.3s;
            font-weight: bold;
            border: 1px solid #0078D4;
        }
        
        /* Mejorar la visualización de las tablas para que no se vean 'pegadas' */
        .stDataFrame { 
            border-radius: 10px; 
            padding: 5px;
        }

        /* Ajuste para los Tabs (Pestañas) */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

# --- 3. CARGA DE DATOS ---
def cargar_datos(pestaña):
    try:
        df = pd.read_excel("database.xlsx", sheet_name=pestaña, dtype=str)
        if pestaña == "Usuarios" and not df.empty:
            df['Usuario'] = df['Usuario'].str.strip().str.lower()
            if 'Estado_Licencia' not in df.columns: df['Estado_Licencia'] = 'Activo'
        if pestaña == "Inventario" and "Stock" in df.columns:
            df['Stock'] = pd.to_numeric(df['Stock'], errors='coerce').fillna(0).astype(int)
        if pestaña == "Movimientos" and "Cantidad" in df.columns:
            df['Cantidad'] = pd.to_numeric(df['Cantidad'], errors='coerce').fillna(0)
        return df
    except:
        return pd.DataFrame()

# --- 4. GUARDADO GLOBAL ---
def guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera):
    try:
        with pd.ExcelWriter("database.xlsx", engine="openpyxl") as writer:
            df_inv.to_excel(writer, sheet_name="Inventario", index=False)
            df_mov.to_excel(writer, sheet_name="Movimientos", index=False)
            df_u.to_excel(writer, sheet_name="Usuarios", index=False)
            df_mant.to_excel(writer, sheet_name="Mantenimiento", index=False)
            df_lug.to_excel(writer, sheet_name="Lugares", index=False)
            df_papelera.to_excel(writer, sheet_name='Papelera', index=False)
        st.sidebar.success("💾 Base Sincronizada")
    except Exception as e:
        st.error(f"❌ Error al guardar: {e}")

# --- 5. LOGUEO ---
if 'conectado' not in st.session_state: st.session_state['conectado'] = False

aplicar_diseno_jordan()

if not st.session_state['conectado']:
    st.title("🔐 Acceso Jordan Admin Pro")
    u_in = st.text_input("Usuario")
    p_in = st.text_input("Contraseña", type="password")
    if st.button("🚀 Ingresar"):
        u_l = u_in.strip().lower()
        es_m, rol_m = seguridad.verificar_clave(u_l, p_in, None)
        if es_m and rol_m == "Desarrollador":
            st.session_state.update({'conectado': True, 'user': u_l, 'nombre': "Jordan (Master)", 'rol': "Desarrollador"})
            st.rerun()
        else:
            df_u_login = cargar_datos("Usuarios")
            if not df_u_login.empty:
                row = df_u_login[df_u_login['Usuario'] == u_l]
                if not row.empty:
                    if str(row.iloc[0].get('Estado_Licencia', 'Activo')) == "Inactivo":
                        st.error("🚫 LICENCIA DESHABILITADA")
                    elif seguridad.verificar_clave(u_l, p_in, str(row.iloc[0]['Clave']))[0]:
                        st.session_state.update({'conectado': True, 'user': u_l, 'nombre': row.iloc[0]['Nombre'], 'rol': row.iloc[0]['Rol']})
                        st.rerun()
                    else: st.error("❌ Contraseña incorrecta")
                else: st.error("❌ Usuario no registrado")

else:
    # PANEL PRINCIPAL
    df_inv = cargar_datos("Inventario")
    df_mov = cargar_datos("Movimientos")
    df_u = cargar_datos("Usuarios")
    df_mant = cargar_datos("Mantenimiento")
    df_lug = cargar_datos("Lugares")
    df_papelera = cargar_datos("Papelera")

    st.sidebar.title(f"👤 {st.session_state['nombre']}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['conectado'] = False
        st.rerun()

    rol = st.session_state['rol']
    es_poder_total = rol in ["Desarrollador", "Administrador"]
    es_mando_medio = rol in ["Desarrollador", "Administrador", "Supervisor", "Maestro de Obra"]
    
    lista_tabs = ["📦 Inventario", "🔄 Movimientos"]
    if es_mando_medio: lista_tabs += ["🛠️ Mantenimiento", "🏢 Empresas"]
    if es_poder_total: lista_tabs += ["👤 Usuarios", "📜 Historial"]

    tabs = st.tabs(lista_tabs)

    with tabs[0]: inventario.mostrar(df_inv, guardar_global, df_mov, df_u, df_mant, df_lug, df_papelera)
    with tabs[1]: movimientos.mostrar(df_inv, df_mov, df_lug, st.session_state['user'], guardar_global, df_u, df_mant, df_papelera)
    
    try:
        if es_mando_medio:
            with tabs[2]: mantenimiento.mostrar(df_mant, df_inv, guardar_global, df_mov, df_u, df_lug, df_papelera)
            with tabs[3]: empresas.mostrar(df_lug, guardar_global, df_inv, df_mov, df_u, df_mant, df_papelera)
        if es_poder_total:
            with tabs[4]: usuarios.mostrar(df_u, guardar_global, df_inv, df_mov, df_mant, df_lug, df_papelera)
            with tabs[5]: historial.mostrar(df_mov, guardar_global, df_inv, df_u, df_mant, df_lug, df_papelera)
    except: pass
