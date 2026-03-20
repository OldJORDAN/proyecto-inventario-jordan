import streamlit as st
import pandas as pd
from modulos import seguridad, inventario, movimientos, mantenimiento, empresas, usuarios, historial

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Jordan Admin Pro", layout="wide", page_icon="🛠️")

def cargar_datos(pestaña):
    try:
        df = pd.read_excel("database.xlsx", sheet_name=pestaña)
        if pestaña == "Inventario" and "Stock" in df.columns:
            df['Stock'] = pd.to_numeric(df['Stock'], errors='coerce').fillna(0).astype(int)
        return df
    except:
        columnas = {
            "Usuarios": ["Nombre", "Usuario", "Clave", "Rol", "Area"],
            "Inventario": ["ID", "Herramienta", "Marca", "Stock", "Estado", "Lugar"],
            "Movimientos": ["Fecha", "Usuario", "ID", "Herramienta", "Accion", "Cantidad"],
            "Mantenimiento": ["ID", "Herramienta", "Estado", "Fecha"],
            "Lugares": ["Empresa", "Ubicacion"],
            "Papelera": ["ID", "Motivo"]
        }
        return pd.DataFrame(columns=columnas.get(pestaña, []))

def guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera):
    try:
        with pd.ExcelWriter("database.xlsx", engine="openpyxl") as writer:
            df_inv.to_excel(writer, sheet_name="Inventario", index=False)
            df_mov.to_excel(writer, sheet_name="Movimientos", index=False)
            df_u.to_excel(writer, sheet_name="Usuarios", index=False)
            df_mant.to_excel(writer, sheet_name="Mantenimiento", index=False)
            df_lug.to_excel(writer, sheet_name="Lugares", index=False)
            df_papelera.to_excel(writer, sheet_name='Papelera', index=False)
    except Exception as e:
        st.error(f"Error al guardar: {e}")

# --- SESIÓN ---
if 'conectado' not in st.session_state: st.session_state['conectado'] = False
if 'intentos' not in st.session_state: st.session_state['intentos'] = 0

if not st.session_state['conectado']:
    st.title("🔐 Acceso Jordan Admin Pro")
    if st.session_state['intentos'] >= 3:
        st.error("🚫 SISTEMA BLOQUEADO")
        if st.button("🔄 Resetear"):
            st.session_state['intentos'] = 0
            st.rerun()
        st.stop()
    
    u_in = st.text_input("Usuario")
    p_in = st.text_input("Contraseña", type="password")
    
    if st.button("🚀 Ingresar"):
        u_l = u_in.strip().lower()
        es_m, rol_m = seguridad.verificar_clave(u_l, p_in, None)
        
        if es_m:
            st.session_state.update({'conectado': True, 'user': u_l, 'nombre': "Jordan (Master)", 'rol': rol_m or "Desarrollador", 'intentos': 0})
            st.rerun()
        else:
            df_u = cargar_datos("Usuarios")
            if not df_u.empty:
                df_u['User_Match'] = df_u['Usuario'].astype(str).str.strip().str.lower()
                row = df_u[df_u['User_Match'] == u_l]
                if not row.empty:
                    valido, _ = seguridad.verificar_clave(u_l, p_in, row.iloc[0]['Clave'])
                    if valido:
                        st.session_state.update({'conectado': True, 'user': u_l, 'nombre': row.iloc[0]['Nombre'], 'rol': row.iloc[0]['Rol'], 'intentos': 0})
                        st.rerun()
                    else:
                        st.session_state['intentos'] += 1
                        st.error("Contraseña incorrecta")
                else:
                    st.session_state['intentos'] += 1
                    st.error("Usuario no encontrado")

else:
    # CARGA DE DATOS
    df_inv = cargar_datos("Inventario")
    df_mov = cargar_datos("Movimientos")
    df_u = cargar_datos("Usuarios")
    df_mant = cargar_datos("Mantenimiento")
    df_lug = cargar_datos("Lugares")
    df_papelera = cargar_datos("Papelera")

    st.sidebar.title(f"👤 {st.session_state['nombre']}")
    st.sidebar.info(f"Rol: {st.session_state['rol']}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['conectado'] = False
        st.rerun()

    # --- LÓGICA DE PESTAÑAS PARA EL MAESTRO ---
    es_admin = st.session_state['rol'] in ["Desarrollador", "Supervisor", "Administrador"]
    
    # Aquí definimos todas las pestañas
    if es_admin:
        lista_tabs = ["📦 Inventario", "🔄 Movimientos", "🛠️ Mantenimiento", "🏢 Empresas", "👤 Usuarios", "📜 Historial"]
    else:
        lista_tabs = ["📦 Inventario", "🔄 Movimientos"]
    
    tabs = st.tabs(lista_tabs)

    with tabs[0]: 
        inventario.mostrar(df_inv, guardar_global, df_mov, df_u, df_mant, df_lug, df_papelera)
    with tabs[1]: 
        movimientos.mostrar(df_inv, df_mov, df_lug, st.session_state['user'], guardar_global, df_u, df_mant, df_papelera)
    
    if es_admin:
        with tabs[2]: 
            mantenimiento.mostrar(df_mant, df_inv, guardar_global, df_mov, df_u, df_lug, df_papelera)
        with tabs[3]: 
            empresas.mostrar(df_lug, guardar_global, df_inv, df_mov, df_u, df_mant, df_papelera)
        with tabs[4]: 
            usuarios.mostrar(df_u, guardar_global, df_inv, df_mov, df_mant, df_lug, df_papelera)
        with tabs[5]: 
            historial.mostrar(df_mov, guardar_global, df_inv, df_u, df_mant, df_lug, df_papelera)
