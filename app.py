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
        return pd.read_excel("database.xlsx", sheet_name=pestaña, dtype=str)
    except:
        return pd.DataFrame()

# --- SISTEMA DE SESIÓN ---
if 'conectado' not in st.session_state: st.session_state['conectado'] = False
if 'intentos' not in st.session_state: st.session_state['intentos'] = 0

aplicar_diseno()

if not st.session_state['conectado']:
    st.title("🔐 Acceso Jordan Admin Pro")
    
    if st.session_state['intentos'] >= 3:
        st.error("🚫 ACCESO BLOQUEADO POR SEGURIDAD")
        if st.button("🔄 Resetear Intentos"):
            st.session_state['intentos'] = 0
            st.rerun()
        st.stop()
    
    u_input = st.text_input("Usuario")
    p_input = st.text_input("Contraseña", type="password")
    
    if st.button("🚀 Ingresar al Sistema"):
        u_limpio = u_input.strip().lower()
        
        # --- PASO 1: VERIFICAR SI ES EL ADMIN MAESTRO ---
        es_maestro, rol_maestro = seguridad.verificar_clave(u_limpio, p_input, "N/A")
        
        if es_maestro and rol_maestro == "Desarrollador":
            st.session_state.update({
                'conectado': True,
                'user': u_limpio,
                'nombre': "Jordan (Master)",
                'rol': "Desarrollador",
                'intentos': 0
            })
            st.success("¡Acceso Maestro Concedido!")
            st.rerun()
        
        # --- PASO 2: SI NO ES MAESTRO, BUSCAR EN EXCEL ---
        else:
            df_u = cargar_datos("Usuarios")
            if not df_u.empty:
                # Buscamos al usuario en el DataFrame
                df_u['User_Match'] = df_u['Usuario'].astype(str).str.strip().str.lower()
                user_row = df_u[df_u['User_Match'] == u_limpio]
                
                if not user_row.empty:
                    clave_excel = user_row.iloc[0]['Clave']
                    es_valido, _ = seguridad.verificar_clave(u_limpio, p_input, clave_excel)
                    
                    if es_valido:
                        st.session_state.update({
                            'conectado': True,
                            'user': u_limpio,
                            'nombre': user_row.iloc[0]['Nombre'],
                            'rol': user_row.iloc[0]['Rol'],
                            'intentos': 0
                        })
                        st.rerun()
                    else:
                        st.session_state['intentos'] += 1
                        st.error(f"❌ Contraseña incorrecta ({st.session_state['intentos']}/3)")
                else:
                    st.session_state['intentos'] += 1
                    st.error("❌ Usuario no registrado.")
            else:
                st.error("Error: No se pudo conectar con la base de datos.")

else:
    # --- PANEL DE CONTROL ---
    st.sidebar.title(f"👤 {st.session_state['nombre']}")
    st.sidebar.write(f"Acceso: **{st.session_state['rol']}**")
    
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

    # Módulos (Agregamos todos los tabs)
    tabs = st.tabs(["📦 Inventario", "🔄 Movimientos", "👤 Usuarios"])
    
    with tabs[0]: 
        inventario.mostrar(df_inv, None, df_mov, df_u, df_mant, df_lug, df_papelera)
    with tabs[1]: 
        movimientos.mostrar(df_inv, df_mov, df_lug, st.session_state['user'], None, df_u, df_mant, df_papelera)
    with tabs[2]: 
        usuarios.mostrar(df_u, None, df_inv, df_mov, df_mant, df_lug, df_papelera)
