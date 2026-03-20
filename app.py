import streamlit as st
import pandas as pd
import bcrypt
from modulos import seguridad, inventario, movimientos, mantenimiento, empresas, usuarios, historial

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Jordan Admin Pro", layout="wide", page_icon="🛠️")

# --- 2. CARGA DE DATOS ---
def cargar_datos(pestaña):
    try:
        df = pd.read_excel("database.xlsx", sheet_name=pestaña, dtype=str)
        if pestaña == "Usuarios" and not df.empty:
            df.columns = df.columns.str.strip()
            df['Usuario'] = df['Usuario'].astype(str).str.strip().str.lower()
            if 'Estado_Licencia' not in df.columns: df['Estado_Licencia'] = 'Activo'
            df['Estado_Licencia'] = df['Estado_Licencia'].fillna('Activo')
        
        if pestaña == "Inventario" and not df.empty:
            if 'Stock' in df.columns:
                df['Stock'] = pd.to_numeric(df['Stock'], errors='coerce').fillna(0).astype(int)
        
        if pestaña == "Movimientos" and not df.empty:
            if 'Cantidad' in df.columns:
                df['Cantidad'] = pd.to_numeric(df['Cantidad'], errors='coerce').fillna(0)
            
        return df
    except:
        return pd.DataFrame()

# --- 3. FUNCIÓN DE GUARDADO (LA QUE DABA EL ERROR) ---
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

# --- 4. LOGIN ---
if 'conectado' not in st.session_state: st.session_state['conectado'] = False

if not st.session_state['conectado']:
    st.title("🔐 Acceso Jordan Admin Pro")
    u_in = st.text_input("Usuario").strip().lower()
    p_in = st.text_input("Contraseña", type="password")
    
    if st.button("🚀 Ingresar"):
        df_u = cargar_datos("Usuarios")
        if not df_u.empty:
            row = df_u[df_u['Usuario'] == u_in]
            if not row.empty:
                hash_excel = str(row.iloc[0]['Clave'])
                try:
                    match = bcrypt.checkpw(p_in.encode('utf-8'), hash_excel.encode('utf-8'))
                except:
                    match = (p_in == hash_excel)
                
                if match:
                    st.session_state.update({'conectado': True, 'user': u_in, 'nombre': row.iloc[0]['Nombre'], 'rol': row.iloc[0]['Rol']})
                    st.rerun()
                else: st.error("❌ Contraseña incorrecta")
            else: st.error("❌ Usuario no encontrado")

# --- 5. PANEL PRINCIPAL (CORRECCIÓN DE 'NONE') ---
else:
    df_inv = cargar_datos("Inventario"); df_mov = cargar_datos("Movimientos")
    df_u = cargar_datos("Usuarios"); df_mant = cargar_datos("Mantenimiento")
    df_lug = cargar_datos("Lugares"); df_papelera = cargar_datos("Papelera")

    st.sidebar.title(f"👤 {st.session_state['nombre']}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['conectado'] = False
        st.rerun()

    rol = st.session_state['rol']
    es_admin = any(x in rol for x in ["Desarrollador", "Administrador"])
    es_mando = any(x in rol for x in ["Desarrollador", "Administrador", "Supervisor", "Maestro de Obra"])
    
    lista_tabs = ["📦 Inventario", "🔄 Movimientos"]
    if es_mando: lista_tabs += ["🛠️ Mantenimiento", "🏢 Empresas"]
    if es_admin: lista_tabs += ["👤 Usuarios", "📜 Historial"]

    tabs = st.tabs(lista_tabs)
    
    # --- AQUÍ ESTÁ EL ARREGLO: PASAMOS 'guardar_global' EN LUGAR DE 'None' ---
    with tabs[0]: 
        inventario.mostrar(df_inv, guardar_global, df_mov, df_u, df_mant, df_lug, df_papelera)
    with tabs[1]: 
        movimientos.mostrar(df_inv, df_mov, df_lug, st.session_state['user'], guardar_global, df_u, df_mant, df_papelera)
    
    try:
        if es_mando:
            with tabs[2]: mantenimiento.mostrar(df_mant, df_inv, guardar_global, df_mov, df_u, df_lug, df_papelera)
            with tabs[3]: empresas.mostrar(df_lug, guardar_global, df_inv, df_mov, df_u, df_mant, df_papelera)
        if es_admin:
            # Línea 112 corregida: pasamos guardar_global
            with tabs[4]: usuarios.mostrar(df_u, guardar_global, df_inv, df_mov, df_mant, df_lug, df_papelera)
            with tabs[5]: historial.mostrar(df_mov, guardar_global, df_inv, df_u, df_mant, df_lug, df_papelera)
    except IndexError:
        pass
