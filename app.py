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
        .stButton>button { border-radius: 10px; border: 1px solid #0078D4; }
        </style>
    """, unsafe_allow_html=True)

# --- 3. FUNCIONES DE BASE DE DATOS ---
def cargar_datos(pestaña):
    try:
        df = pd.read_excel("database.xlsx", sheet_name=pestaña)
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

# --- 4. SISTEMA DE SESIÓN ---
if 'conectado' not in st.session_state:
    st.session_state['conectado'] = False
if 'intentos' not in st.session_state:
    st.session_state['intentos'] = 0

aplicar_diseno_jordan()

if not st.session_state['conectado']:
    st.title("🔐 Acceso Jordan Admin Pro")
    
    if st.session_state['intentos'] >= 3:
        st.error("🚫 **SISTEMA BLOQUEADO**")
        if st.button("🔄 Resetear Intentos"):
            st.session_state['intentos'] = 0
            st.rerun()
        st.stop()
    
    u_input = st.text_input("Usuario")
    p_input = st.text_input("Contraseña", type="password")
    
    if st.button("Ingresar Sistema"):
        u_limpio = seguridad.limpiar_texto_seguro(u_input)
        
        df_u = cargar_datos("Usuarios")
        if not df_u.empty:
            # Buscamos el usuario convirtiendo todo a string para que no falle
            df_u['Usuario_Str'] = df_u['Usuario'].astype(str).str.strip().str.lower()
            user_row = df_u[df_u['Usuario_Str'] == u_limpio.lower()]
            
            if not user_row.empty:
                clave_excel = str(user_row.iloc[0]['Clave'])
                
                if seguridad.verificar_clave(p_input, clave_excel):
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
                    st.error(f"❌ Clave incorrecta ({st.session_state['intentos']}/3)")
            else:
                st.session_state['intentos'] += 1
                st.error("❌ Usuario no encontrado")
        else:
            st.error("No se pudo leer la tabla de usuarios.")

else:
    # --- PANEL DE CONTROL ---
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
    tabs = st.tabs(["📊 Inventario", "🔄 Movimientos", "🛠️ Mantenimiento", "🏢 Empresas", "👤 Usuarios", "📜 Historial"] if es_admin else ["📊 Inventario", "🔄 Movimientos", "🛠️ Mantenimiento", "🏢 Empresas"])

    with tabs[0]: inventario.mostrar(df_inv, guardar_global, df_mov, df_u, df_mant, df_lug, df_papelera)
    with tabs[1]: movimientos.mostrar(df_inv, df_mov, df_lug, st.session_state['user'], guardar_global, df_u, df_mant, df_papelera)
    with tabs[2]: mantenimiento.mostrar(df_mant, df_inv, guardar_global, df_mov, df_u, df_lug, df_papelera)
    with tabs[3]: empresas.mostrar(df_lug, guardar_global, df_inv, df_mov, df_u, df_mant, df_papelera)
    if es_admin:
        with tabs[4]: usuarios.mostrar(df_u, guardar_global, df_inv, df_mov, df_mant, df_lug, df_papelera)
        with tabs[5]: historial.mostrar(df_mov, guardar_global, df_inv, df_u, df_mant, df_lug, df_papelera)
