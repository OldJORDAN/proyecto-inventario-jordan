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
        .stButton>button { border-radius: 10px; width: 100%; transition: 0.3s; font-weight: bold; }
        .stButton>button:hover { background-color: #0078D4 !important; color: white !important; }
        [data-testid="stSidebar"] { background-color: #f8f9fa; border-right: 1px solid #e0e0e0; }
        </style>
    """, unsafe_allow_html=True)

# --- 3. CARGA DE DATOS BLINDADA ---
def cargar_datos(pestaña):
    try:
        # Forzamos lectura como texto para evitar errores de formato en Claves y Usuarios
        df = pd.read_excel("database.xlsx", sheet_name=pestaña, dtype=str)
        
        # Normalización de seguridad para la pestaña Usuarios
        if pestaña == "Usuarios" and not df.empty:
            df['Usuario'] = df['Usuario'].str.strip().str.lower()
            if 'Estado_Licencia' not in df.columns:
                df['Estado_Licencia'] = 'Activo'
            
        # Normalización de Stock para que funcionen los cálculos matemáticos
        if pestaña == "Inventario" and "Stock" in df.columns:
            df['Stock'] = pd.to_numeric(df['Stock'], errors='coerce').fillna(0).astype(int)
            
        return df
    except:
        return pd.DataFrame()

# --- 4. FUNCIÓN DE GUARDADO GLOBAL (Escritura en Disco) ---
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
        st.error(f"❌ Error al guardar en Excel: {e}")

# --- 5. LÓGICA DE INICIO DE SESIÓN ---
if 'conectado' not in st.session_state: 
    st.session_state['conectado'] = False

aplicar_diseno_jordan()

if not st.session_state['conectado']:
    st.title("🔐 Acceso Jordan Admin Pro")
    u_in = st.text_input("Usuario")
    p_in = st.text_input("Contraseña", type="password")
    
    if st.button("🚀 Ingresar al Sistema"):
        u_l = u_in.strip().lower()
        
        # PRIORIDAD 1: Llave Maestra (Tú como Desarrollador)
        es_m, rol_m = seguridad.verificar_clave(u_l, p_in, None)
        if es_m and rol_m == "Desarrollador":
            st.session_state.update({'conectado': True, 'user': u_l, 'nombre': "Jordan (Master)", 'rol': "Desarrollador"})
            st.rerun()
        
        # PRIORIDAD 2: Usuarios del Excel
        else:
            df_u_login = cargar_datos("Usuarios")
            if not df_u_login.empty:
                row = df_u_login[df_u_login['Usuario'] == u_l]
                
                if not row.empty:
                    # VALIDACIÓN DE ESTADO DE LICENCIA
                    estado_lic = str(row.iloc[0].get('Estado_Licencia', 'Activo'))
                    
                    if estado_lic == "Inactivo":
                        st.error("🚫 **LICENCIA DESHABILITADA:** Contacte al Desarrollador para activar su acceso.")
                    else:
                        clave_excel = str(row.iloc[0]['Clave'])
                        valido, _ = seguridad.verificar_clave(u_l, p_in, clave_excel)
                        
                        if valido:
                            st.session_state.update({
                                'conectado': True, 
                                'user': u_l, 
                                'nombre': row.iloc[0]['Nombre'], 
                                'rol': row.iloc[0]['Rol']
                            })
                            st.rerun()
                        else:
                            st.error("❌ Contraseña incorrecta")
                else:
                    st.error("❌ Usuario no registrado")
            else:
                st.error("❌ Error al conectar con la base de datos")

# --- 6. PANEL PRINCIPAL (USUARIO CONECTADO) ---
else:
    # Carga de todos los datos necesarios
    df_inv = cargar_datos("Inventario")
    df_mov = cargar_datos("Movimientos")
    df_u = cargar_datos("Usuarios")
    df_mant = cargar_datos("Mantenimiento")
    df_lug = cargar_datos("Lugares")
    df_papelera = cargar_datos("Papelera")

    # Sidebar con info del usuario
    st.sidebar.title(f"👤 {st.session_state['nombre']}")
    st.sidebar.info(f"Rol: **{st.session_state['rol']}**")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['conectado'] = False
        st.rerun()

    # --- DEFINICIÓN DE PERMISOS POR ROL ---
    rol = st.session_state['rol']
    
    es_poder_total = rol in ["Desarrollador", "Administrador"]
    es_mando_medio = rol in ["Desarrollador", "Administrador", "Supervisor", "Maestro de Obra"]
    
    # Pestañas básicas para todos (Soldador, Cortador, Amolador, Pintor, Ayudante)
    lista_tabs = ["📦 Inventario", "🔄 Movimientos"]
    
    if es_mando_medio:
        lista_tabs += ["🛠️ Mantenimiento", "🏢 Empresas"]
    
    if es_poder_total:
        lista_tabs += ["👤 Usuarios", "📜 Historial"]

    # Crear la interfaz de pestañas
    tabs = st.tabs(lista_tabs)

    # Contenido de las pestañas
    with tabs[0]: 
        inventario.mostrar(df_inv, guardar_global, df_mov, df_u, df_mant, df_lug, df_papelera)
    with tabs[1]: 
        movimientos.mostrar(df_inv, df_mov, df_lug, st.session_state['user'], guardar_global, df_u, df_mant, df_papelera)
    
    # Control de errores por si el rol no tiene acceso a las pestañas superiores
    try:
        if es_mando_medio:
            with tabs[2]: mantenimiento.mostrar(df_mant, df_inv, guardar_global, df_mov, df_u, df_lug, df_papelera)
            with tabs[3]: empresas.mostrar(df_lug, guardar_global, df_inv, df_mov, df_u, df_mant, df_papelera)
        if es_poder_total:
            with tabs[4]: usuarios.mostrar(df_u, guardar_global, df_inv, df_mov, df_mant, df_lug, df_papelera)
            with tabs[5]: historial.mostrar(df_mov, guardar_global, df_inv, df_u, df_mant, df_lug, df_papelera)
    except IndexError:
        pass
