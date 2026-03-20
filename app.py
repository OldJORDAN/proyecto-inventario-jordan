import streamlit as st
import pandas as pd
import time
import os
from modulos import seguridad, inventario, movimientos, mantenimiento, empresas, usuarios, historial

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Jordan Admin Pro", layout="wide", page_icon="🛠️")

# --- 2. CARGA DE DATOS SEGUROS ---
def cargar_datos(pestaña):
    if not os.path.exists("database.xlsx"): return pd.DataFrame()
    try:
        df = pd.read_excel("database.xlsx", sheet_name=pestaña, dtype=str)
        df.columns = df.columns.str.strip()
        # Limpiamos datos para evitar errores de comparación
        for col in df.columns: df[col] = df[col].astype(str).str.strip()
        if pestaña == "Usuarios":
            df['Usuario'] = df['Usuario'].str.lower()
            if 'Estado_Licencia' not in df.columns: df['Estado_Licencia'] = 'Activo'
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
        st.sidebar.success("💾 Base Sincronizada")
    except: st.error("❌ Error: Cierra el Excel antes de guardar.")

# --- 4. LÓGICA DE LOGIN Y BLOQUEO ---
if 'conectado' not in st.session_state: st.session_state['conectado'] = False
if 'intentos' not in st.session_state: st.session_state['intentos'] = 0

if not st.session_state['conectado']:
    st.title("🔐 Acceso Jordan Admin Pro")
    
    # PUNTO 1: Bloqueo tras 3 intentos
    if st.session_state['intentos'] >= 3:
        st.error("🚫 SISTEMA BLOQUEADO: Demasiados intentos. Contacte al administrador.")
        if st.button("🔄 Reiniciar intentos (Jordan Only)"):
            st.session_state['intentos'] = 0
            st.rerun()
    else:
        with st.form("login_seguro"):
            u_in = st.text_input("Usuario").strip().lower()
            p_in = st.text_input("Contraseña", type="password").strip()
            if st.form_submit_button("🚀 Ingresar", use_container_width=True):
                # PUNTO 2: Acceso Maestro Jordan
                if u_in == "jordan" and p_in == "170362":
                    st.session_state.update({'conectado': True, 'user': 'jordan', 'nombre': 'JORDAN DAMIAN', 'rol': 'Desarrollador', 'intentos': 0})
                    st.rerun()
                else:
                    df_u = cargar_datos("Usuarios")
                    row = df_u[df_u['Usuario'] == u_in] if not df_u.empty else pd.DataFrame()
                    
                    if not row.empty and str(row.iloc[0]['Clave']).strip() == p_in:
                        # PUNTO 3: Verificación de Estado (Si está deshabilitado no entra)
                        if row.iloc[0].get('Estado_Licencia') == "Inactivo":
                            st.error("🚫 Tu cuenta ha sido deshabilitada.")
                        else:
                            st.session_state.update({'conectado': True, 'user': u_in, 'nombre': row.iloc[0]['Nombre'], 'rol': row.iloc[0]['Rol'], 'intentos': 0})
                            st.rerun()
                    else:
                        st.session_state['intentos'] += 1
                        st.error(f"❌ Datos incorrectos. Intento {st.session_state['intentos']} de 3")
                        if st.session_state['intentos'] >= 3: st.rerun()

# --- 5. PANEL PRINCIPAL ---
else:
    df_inv = cargar_datos("Inventario"); df_mov = cargar_datos("Movimientos")
    df_u = cargar_datos("Usuarios"); df_mant = cargar_datos("Mantenimiento")
    df_lug = cargar_datos("Lugares"); df_papelera = cargar_datos("Papelera")

    # Sidebar con Perfil
    with st.sidebar:
        st.subheader(f"👤 {st.session_state['nombre']}")
        st.caption(f"🛡️ Rol: {st.session_state['rol']}")
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state['conectado'] = False
            st.rerun()

    # PUNTO 4: Permisos por Rol
    rol = st.session_state['rol']
    es_admin = any(x in ["Desarrollador", "Administrador"] for x in [rol])
    es_mando = any(x in ["Desarrollador", "Administrador", "Supervisor", "Maestro de Obra"] for x in [rol])
    
    # Construcción de pestañas dinámica
    tabs_n = ["📦 Inventario", "🔄 Movimientos"]
    if es_mando: tabs_n += ["🛠️ Mantenimiento", "🏢 Empresas"]
    if es_admin: tabs_n += ["👤 Usuarios", "📜 Historial"]
    
    tabs = st.tabs(tabs_n)
    
    # PUNTO 5: Inyección controlada
    with tabs[0]: inventario.mostrar(df_inv, guardar_global, df_mov, df_u, df_mant, df_lug, df_papelera)
    with tabs[1]: movimientos.mostrar(df_inv, df_mov, df_lug, st.session_state['user'], guardar_global, df_u, df_mant, df_papelera)
    
    idx = 2
    if es_mando:
        with tabs[idx]: mantenimiento.mostrar(df_mant, df_inv, guardar_global, df_mov, df_u, df_lug, df_papelera); idx += 1
        with tabs[idx]: empresas.mostrar(df_lug, guardar_global, df_inv, df_mov, df_u, df_mant, df_papelera); idx += 1
    if es_admin:
        with tabs[idx]: usuarios.mostrar(df_u, guardar_global, df_inv, df_mov, df_mant, df_lug, df_papelera); idx += 1
        with tabs[idx]: historial.mostrar(df_mov, guardar_global, df_inv, df_u, df_mant, df_lug, df_papelera)
