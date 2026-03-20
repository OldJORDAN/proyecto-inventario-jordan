import streamlit as st
import pandas as pd
import bcrypt
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
        </style>
    """, unsafe_allow_html=True)

# --- 3. CARGA DE DATOS SEGURA ---
def cargar_datos(pestaña):
    try:
        df = pd.read_excel("database.xlsx", sheet_name=pestaña, dtype=str)
        if pestaña == "Usuarios" and not df.empty:
            df.columns = df.columns.str.strip()
            df['Usuario'] = df['Usuario'].str.strip().str.lower()
            if 'Estado_Licencia' not in df.columns: df['Estado_Licencia'] = 'Activo'
            df['Estado_Licencia'] = df['Estado_Licencia'].fillna('Activo')
            
        if pestaña == "Inventario" and "Stock" in df.columns:
            df['Stock'] = pd.to_numeric(df['Stock'], errors='coerce').fillna(0).astype(int)
            
        if pestaña == "Movimientos" and "Cantidad" in df.columns:
            df['Cantidad'] = pd.to_numeric(df['Cantidad'], errors='coerce').fillna(0)
            
        return df
    except:
        return pd.DataFrame()

# --- 4. FUNCIÓN DE GUARDADO GLOBAL ---
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

# --- 5. LÓGICA DE LOGIN (BCRYPT + LLAVE MAESTRA) ---
if 'conectado' not in st.session_state: st.session_state['conectado'] = False

aplicar_diseno_jordan()

if not st.session_state['conectado']:
    st.title("🔐 Acceso Jordan Admin Pro")
    u_in = st.text_input("Usuario").strip().lower()
    p_in = st.text_input("Contraseña", type="password")
    
    if st.button("🚀 Ingresar"):
        # Primero: Chequear contra el Excel
        df_u_login = cargar_datos("Usuarios")
        if not df_u_login.empty:
            row = df_u_login[df_u_login['Usuario'] == u_in]
            if not row.empty:
                hash_excel = str(row.iloc[0]['Clave']).strip()
                estado = str(row.iloc[0].get('Estado_Licencia', 'Activo'))
                
                if estado != "Activo":
                    st.error("🚫 LICENCIA DESHABILITADA")
                else:
                    try:
                        # VALIDACIÓN BCRYPT
                        if bcrypt.checkpw(p_in.encode('utf-8'), hash_excel.encode('utf-8')):
                            st.session_state.update({
                                'conectado': True, 'user': u_in, 
                                'nombre': row.iloc[0]['Nombre'], 'rol': row.iloc[0]['Rol']
                            })
                            st.rerun()
                        else: st.error("❌ Contraseña incorrecta")
                    except:
                        # Por si la clave en el Excel no está hasheada (Texto plano)
                        if p_in == hash_excel:
                            st.session_state.update({
                                'conectado': True, 'user': u_in, 
                                'nombre': row.iloc[0]['Nombre'], 'rol': row.iloc[0]['Rol']
                            })
                            st.rerun()
                        else: st.error("❌ Formato de clave inválido o incorrecta")
            else: st.error("❌ Usuario no registrado")
        else: st.error("❌ Error de conexión con la base de datos")

# --- 6. PANEL PRINCIPAL (AQUÍ ESTÁ LO QUE NO VEÍAS) ---
else:
    # CARGA MASIVA DE DATOS
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

    # PERMISOS
    rol = st.session_state['rol']
    es_admin = rol in ["Desarrollador", "Administrador"]
    es_mando = rol in ["Desarrollador", "Administrador", "Supervisor", "Maestro de Obra"]
    
    # LISTA DE PESTAÑAS SEGÚN EL ROL
    lista_tabs = ["📦 Inventario", "🔄 Movimientos"]
    if es_mando: lista_tabs += ["🛠️ Mantenimiento", "🏢 Empresas"]
    if es_admin: lista_tabs += ["👤 Usuarios", "📜 Historial"]

    # DIBUJAR PESTAÑAS
    tabs = st.tabs(lista_tabs)

    # MOSTRAR CONTENIDO (Asegurando que el orden coincida con lista_tabs)
    with tabs[0]: 
        inventario.mostrar(df_inv, guardar_global, df_mov, df_u, df_mant, df_lug, df_papelera)
    with tabs[1]: 
        movimientos.mostrar(df_inv, df_mov, df_lug, st.session_state['user'], guardar_global, df_u, df_mant, df_papelera)
    
    try:
        if es_mando:
            with tabs[2]: mantenimiento.mostrar(df_mant, df_inv, guardar_global, df_mov, df_u, df_lug, df_papelera)
            with tabs[3]: empresas.mostrar(df_lug, guardar_global, df_inv, df_mov, df_u, df_mant, df_papelera)
        if es_admin:
            with tabs[4]: usuarios.mostrar(df_u, guardar_global, df_inv, df_mov, df_mant, df_lug, df_papelera)
            with tabs[5]: historial.mostrar(df_mov, guardar_global, df_inv, df_u, df_mant, df_lug, df_papelera)
    except IndexError:
        pass
