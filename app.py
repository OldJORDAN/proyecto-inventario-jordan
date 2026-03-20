import streamlit as st
import pandas as pd
import bcrypt
import time
import os
from modulos import seguridad, inventario, movimientos, mantenimiento, empresas, usuarios, historial

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Jordan Admin Pro", layout="wide", page_icon="🛠️")

# --- 2. CARGA DE DATOS ---
def cargar_datos(pestaña):
    if not os.path.exists("database.xlsx"):
        return pd.DataFrame()
    try:
        df = pd.read_excel("database.xlsx", sheet_name=pestaña, dtype=str)
        df.columns = df.columns.str.strip()
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
        return df
    except:
        time.sleep(0.5)
        try: return pd.read_excel("database.xlsx", sheet_name=pestaña, dtype=str)
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
        st.sidebar.success("💾 ¡Sincronizado!")
    except: st.error("❌ Error: Cierra el Excel si está abierto.")

# --- 4. LÓGICA DE LOGIN (CON ACCESO FORZADO "1") ---
if 'conectado' not in st.session_state:
    st.session_state['conectado'] = False

if not st.session_state['conectado']:
    st.title("🔐 Acceso Jordan Admin Pro")
    
    with st.form("login_form"):
        u_in = st.text_input("Usuario").strip().lower()
        p_in = st.text_input("Contraseña", type="password").strip()
        boton_login = st.form_submit_button("🚀 Ingresar", use_container_width=True)
    
    if boton_login:
        # --- EL "HACK" PARA ENTRAR A LA FUERZA ---
        if u_in == "1" and p_in == "1":
            st.session_state.update({
                'conectado': True, 
                'user': 'jordan', 
                'nombre': 'JORDAN DAMIAN TITO AYALA', 
                'rol': 'Desarrollador'
            })
            st.success("✅ Acceso Maestro Concedido")
            time.sleep(0.5)
            st.rerun()
        
        # --- LOGIN NORMAL POR EXCEL ---
        else:
            df_u_login = cargar_datos("Usuarios")
            if not df_u_login.empty:
                row = df_u_login[df_u_login['Usuario'] == u_in]
                if not row.empty:
                    clave_excel = str(row.iloc[0]['Clave']).strip()
                    if p_in == clave_excel:
                        st.session_state.update({
                            'conectado': True, 
                            'user': u_in, 
                            'nombre': row.iloc[0]['Nombre'], 
                            'rol': row.iloc[0]['Rol']
                        })
                        st.rerun()
                    else: st.error("❌ Contraseña incorrecta")
                else: st.error("❌ Usuario no existe")
            else: st.error("❌ No hay base de datos de usuarios")

# --- 5. PANEL PRINCIPAL ---
else:
    df_inv = cargar_datos("Inventario"); df_mov = cargar_datos("Movimientos")
    df_u = cargar_datos("Usuarios"); df_mant = cargar_datos("Mantenimiento")
    df_lug = cargar_datos("Lugares"); df_papelera = cargar_datos("Papelera")

    with st.sidebar:
        st.title(f"👤 {st.session_state['nombre']}")
        st.info(f"Rol: {st.session_state['rol']}")
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state['conectado'] = False
            st.rerun()

    rol = st.session_state['rol']
    es_admin = any(x in ["Desarrollador", "Administrador"] for x in [rol])
    es_mando = any(x in ["Desarrollador", "Administrador", "Supervisor", "Maestro de Obra"] for x in [rol])
    
    tabs_n = ["📦 Inventario", "🔄 Movimientos"]
    if es_mando: tabs_n += ["🛠️ Mantenimiento", "🏢 Empresas"]
    if es_admin: tabs_n += ["👤 Usuarios", "📜 Historial"]
    
    tabs = st.tabs(tabs_n)

    with tabs[0]: inventario.mostrar(df_inv, guardar_global, df_mov, df_u, df_mant, df_lug, df_papelera)
    with tabs[1]: movimientos.mostrar(df_inv, df_mov, df_lug, st.session_state['user'], guardar_global, df_u, df_mant, df_papelera)
    
    curr = 2
    if es_mando:
        with tabs[curr]: mantenimiento.mostrar(df_mant, df_inv, guardar_global, df_mov, df_u, df_lug, df_papelera)
        curr += 1
        with tabs[curr]: empresas.mostrar(df_lug, guardar_global, df_inv, df_mov, df_u, df_mant, df_papelera)
        curr += 1
    if es_admin:
        with tabs[curr]: usuarios.mostrar(df_u, guardar_global, df_inv, df_mov, df_mant, df_lug, df_papelera)
        curr += 1
        with tabs[curr]: historial.mostrar(df_mov, guardar_global, df_inv, df_u, df_mant, df_lug, df_papelera)
