import streamlit as st
import pandas as pd
from modulos import seguridad, inventario, movimientos, mantenimiento, empresas, usuarios, historial

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Jordan Admin Pro", layout="wide", page_icon="🛠️")

def aplicar_diseno():
    st.markdown("""
        <style>
        h1 { color: #0078D4 !important; font-weight: 800; }
        .stButton>button { border-radius: 10px; width: 100%; background-color: #f0f2f6; }
        </style>
    """, unsafe_allow_html=True)

def cargar_datos(pestaña):
    try:
        df = pd.read_excel("database.xlsx", sheet_name=pestaña)
        # --- CORRECCIÓN CRÍTICA DE TIPOS ---
        if pestaña == "Inventario" and "Stock" in df.columns:
            df['Stock'] = pd.to_numeric(df['Stock'], errors='coerce').fillna(0).astype(int)
        return df
    except:
        return pd.DataFrame()

def guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera):
    with pd.ExcelWriter("database.xlsx", engine="openpyxl") as writer:
        df_inv.to_excel(writer, sheet_name="Inventario", index=False)
        df_mov.to_excel(writer, sheet_name="Movimientos", index=False)
        df_u.to_excel(writer, sheet_name="Usuarios", index=False)
        df_mant.to_excel(writer, sheet_name="Mantenimiento", index=False)
        df_lug.to_excel(writer, sheet_name="Lugares", index=False)
        df_papelera.to_excel(writer, sheet_name='Papelera', index=False)

# --- SISTEMA DE SESIÓN ---
if 'conectado' not in st.session_state: st.session_state['conectado'] = False
if 'intentos' not in st.session_state: st.session_state['intentos'] = 0

aplicar_diseno()

if not st.session_state['conectado']:
    st.title("🔐 Acceso Jordan Admin Pro")
    
    if st.session_state['intentos'] >= 3:
        st.error("🚫 ACCESO BLOQUEADO")
        if st.button("🔄 Resetear Intentos"):
            st.session_state['intentos'] = 0
            st.rerun()
        st.stop()
    
    u_input = st.text_input("Usuario")
    p_input = st.text_input("Contraseña", type="password")
    
    if st.button("🚀 Ingresar"):
        u_limpio = u_input.strip().lower()
        # Verificación con Llave Maestra
        es_maestro, rol_maestro = seguridad.verificar_clave(u_limpio, p_input, "N/A")
        
        if es_maestro and rol_maestro == "Desarrollador":
            st.session_state.update({'conectado': True, 'user': u_limpio, 'nombre': "Jordan (Master)", 'rol': "Desarrollador", 'intentos': 0})
            st.rerun()
        else:
            df_u = cargar_datos("Usuarios")
            if not df_u.empty:
                df_u['User_Match'] = df_u['Usuario'].astype(str).str.strip().str.lower()
                user_row = df_u[df_u['User_Match'] == u_limpio]
                if not user_row.empty:
                    if seguridad.verificar_clave(u_limpio, p_input, str(user_row.iloc[0]['Clave']))[0]:
                        st.session_state.update({'conectado': True, 'user': u_limpio, 'nombre': user_row.iloc[0]['Nombre'], 'rol': user_row.iloc[0]['Rol'], 'intentos': 0})
                        st.rerun()
                    else:
                        st.session_state['intentos'] += 1
                        st.error(f"❌ Clave incorrecta ({st.session_state['intentos']}/3)")
                else:
                    st.session_state['intentos'] += 1
                    st.error("❌ Usuario no encontrado")

else:
    # CARGA DE DATOS PARA MÓDULOS
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

    es_admin = st.session_state['rol'] in ["Desarrollador", "Supervisor", "Administrador"]
    tabs = st.tabs(["📦 Inventario", "🔄 Movimientos", "👤 Usuarios"])
    
    with tabs[0]: 
        inventario.mostrar(df_inv, guardar_global, df_mov, df_u, df_mant, df_lug, df_papelera)
    with tabs[1]: 
        movimientos.mostrar(df_inv, df_mov, df_lug, st.session_state['user'], guardar_global, df_u, df_mant, df_papelera)
    with tabs[2]: 
        usuarios.mostrar(df_u, guardar_global, df_inv, df_mov, df_mant, df_lug, df_papelera)
