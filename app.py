import streamlit as st
import pandas as pd
from modulos import seguridad, inventario, movimientos, mantenimiento, empresas, usuarios, historial

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Jordan Admin Pro", layout="wide", page_icon="🛠️")

def aplicar_diseno():
    st.markdown("<style>h1 { color: #0078D4 !important; } .stButton>button { border-radius: 10px; width: 100%; }</style>", unsafe_allow_html=True)

def cargar_datos(pestaña):
    try:
        # Forzamos a que lea todas las celdas como texto para evitar el error del .0
        df = pd.read_excel("database.xlsx", sheet_name=pestaña, dtype=str)
        return df
    except:
        return pd.DataFrame()

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
    
    if st.button("Ingresar Sistema"):
        u_buscado = u_input.strip().lower()
        df_u = cargar_datos("Usuarios")
        
        if not df_u.empty:
            # LIMPIEZA EXTREMA: Quitamos espacios y pasamos a minúsculas en la búsqueda
            df_u['User_Match'] = df_u['Usuario'].astype(str).str.strip().str.lower()
            user_row = df_u[df_u['User_Match'] == u_buscado]
            
            if not user_row.empty:
                clave_excel = user_row.iloc[0]['Clave']
                
                if seguridad.verificar_clave(p_input, clave_excel):
                    st.session_state.update({
                        'conectado': True,
                        'user': u_buscado,
                        'nombre': user_row.iloc[0]['Nombre'],
                        'rol': user_row.iloc[0]['Rol'],
                        'intentos': 0
                    })
                    st.success("¡Acceso concedido!")
                    st.rerun()
                else:
                    st.session_state['intentos'] += 1
                    st.error(f"❌ Contraseña incorrecta ({st.session_state['intentos']}/3)")
            else:
                st.session_state['intentos'] += 1
                st.error(f"❌ El usuario '{u_buscado}' no existe en el Excel.")
        else:
            st.error("Error: No se pudo cargar la hoja 'Usuarios'. Revisa el nombre en tu Excel.")

else:
    # --- PANEL PRINCIPAL ---
    st.sidebar.title(f"👤 {st.session_state['nombre']}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['conectado'] = False
        st.rerun()
    
    # Carga de datos para módulos
    df_inv = cargar_datos("Inventario")
    df_mov = cargar_datos("Movimientos")
    df_u = cargar_datos("Usuarios")
    df_mant = cargar_datos("Mantenimiento")
    df_lug = cargar_datos("Lugares")
    df_papelera = cargar_datos("Papelera")

    es_admin = st.session_state['rol'] in ["Desarrollador", "Supervisor", "Administrador"]
    tabs = st.tabs(["📦 Inv", "🔄 Mov", "🛠️ Mant", "🏢 Emp", "👤 Usu", "📜 Hist"])
    
    with tabs[0]: inventario.mostrar(df_inv, None, df_mov, df_u, df_mant, df_lug, df_papelera)
    with tabs[1]: movimientos.mostrar(df_inv, df_mov, df_lug, st.session_state['user'], None, df_u, df_mant, df_papelera)
    with tabs[4]: usuarios.mostrar(df_u, None, df_inv, df_mov, df_mant, df_lug, df_papelera)
    # Agrega el resto de tus módulos aquí siguiendo el mismo orden...
