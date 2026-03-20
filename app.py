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
        if pestaña == "Usuarios":
            if 'Estado_Licencia' not in df.columns: df['Estado_Licencia'] = 'Activo'
            # Aseguramos columnas de perfil si no existen
            for c in ['Apellidos', 'Celular', 'Correo']:
                if c not in df.columns: df[c] = ""
            df['Usuario'] = df['Usuario'].str.lower()
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
    except: st.error("❌ Error: Cierra el Excel.")

# --- 4. LÓGICA DE LOGIN ---
if 'conectado' not in st.session_state: st.session_state['conectado'] = False

if not st.session_state['conectado']:
    st.title("🔐 Acceso Jordan Admin Pro")
    with st.form("login"):
        u_in = st.text_input("Usuario").strip().lower()
        p_in = st.text_input("Contraseña", type="password").strip()
        if st.form_submit_button("🚀 Ingresar", use_container_width=True):
            if u_in == "jordan" and p_in == "170362":
                st.session_state.update({'conectado': True, 'user': 'jordan', 'nombre': 'JORDAN DAMIAN', 'rol': 'Desarrollador'})
                st.rerun()
            else:
                df_u = cargar_datos("Usuarios")
                if not df_u.empty:
                    row = df_u[df_u['Usuario'] == u_in]
                    if not row.empty and str(row.iloc[0]['Clave']).strip() == p_in:
                        st.session_state.update({'conectado': True, 'user': u_in, 'nombre': row.iloc[0]['Nombre'], 'rol': row.iloc[0]['Rol']})
                        st.rerun()
                    else: st.error("❌ Credenciales incorrectas")

# --- 5. PANEL PRINCIPAL ---
else:
    df_inv = cargar_datos("Inventario"); df_mov = cargar_datos("Movimientos")
    df_u = cargar_datos("Usuarios"); df_mant = cargar_datos("Mantenimiento")
    df_lug = cargar_datos("Lugares"); df_papelera = cargar_datos("Papelera")

    # --- SIDEBAR MEJORADO (LO QUE PEDISTE) ---
    with st.sidebar:
        st.subheader(f"👤 {st.session_state['nombre']}")
        st.caption(f"🛡️ Rol: {st.session_state['rol']}") # Muestra el Rol abajo del nombre
        
        with st.expander("⚙️ Mi Perfil"):
            # Buscamos los datos actuales del usuario en el DataFrame
            idx_u = df_u[df_u['Usuario'] == st.session_state['user']].index
            if not idx_u.empty:
                idx = idx_u[0]
                with st.form("perfil_edit"):
                    nuevo_n = st.text_input("Nombres", value=df_u.at[idx, 'Nombre'])
                    nuevo_a = st.text_input("Apellidos", value=df_u.at[idx, 'Apellidos'] if 'Apellidos' in df_u.columns else "")
                    nuevo_c = st.text_input("Celular", value=df_u.at[idx, 'Celular'] if 'Celular' in df_u.columns else "")
                    nuevo_m = st.text_input("Correo", value=df_u.at[idx, 'Correo'] if 'Correo' in df_u.columns else "")
                    
                    if st.form_submit_button("💾 Guardar Perfil"):
                        df_u.at[idx, 'Nombre'] = nuevo_n
                        df_u.at[idx, 'Apellidos'] = nuevo_a
                        df_u.at[idx, 'Celular'] = nuevo_c
                        df_u.at[idx, 'Correo'] = nuevo_m
                        guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                        st.session_state['nombre'] = nuevo_n
                        st.rerun()
        
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state['conectado'] = False
            st.rerun()

    # --- TABS ---
    rol = st.session_state['rol']
    es_admin = any(x in ["Desarrollador", "Administrador"] for x in [rol])
    es_mando = any(x in ["Desarrollador", "Administrador", "Supervisor", "Maestro de Obra"] for x in [rol])
    
    tabs_n = ["📦 Inventario", "🔄 Movimientos"]
    if es_mando: tabs_n += ["🛠️ Mantenimiento", "🏢 Empresas"]
    if es_admin: tabs_n += ["👤 Usuarios", "📜 Historial"]
    
    tabs = st.tabs(tabs_n)
    with tabs[0]: inventario.mostrar(df_inv, guardar_global, df_mov, df_u, df_mant, df_lug, df_papelera)
    with tabs[1]: movimientos.mostrar(df_inv, df_mov, df_lug, st.session_state['user'], guardar_global, df_u, df_mant, df_papelera)
    
    c = 2
    if es_mando:
        with tabs[c]: mantenimiento.mostrar(df_mant, df_inv, guardar_global, df_mov, df_u, df_lug, df_papelera); c+=1
        with tabs[c]: empresas.mostrar(df_lug, guardar_global, df_inv, df_mov, df_u, df_mant, df_papelera); c+=1
    if es_admin:
        with tabs[c]: usuarios.mostrar(df_u, guardar_global, df_inv, df_mov, df_mant, df_lug, df_papelera); c+=1
        with tabs[c]: historial.mostrar(df_mov, guardar_global, df_inv, df_u, df_mant, df_lug, df_papelera)
