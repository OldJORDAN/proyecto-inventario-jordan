import streamlit as st
import pandas as pd
from modulos import seguridad, inventario, movimientos, mantenimiento, empresas, usuarios, historial

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Jordan Admin Pro", layout="wide", page_icon="🛠️")

# --- 2. CARGA DE DATOS NORMALIZADA ---
def cargar_datos(pestaña):
    try:
        # Forzamos a que lea todo como TEXTO (str) para que no haya líos con los números
        df = pd.read_excel("database.xlsx", sheet_name=pestaña, dtype=str)
        
        # Si es la pestaña de Usuarios, limpiamos espacios invisibles de una vez
        if pestaña == "Usuarios" and not df.empty:
            df['Usuario'] = df['Usuario'].str.strip().str.lower()
            df['Clate'] = df['Clave'].str.strip() # Guardamos clave limpia
            
        # Si es Inventario, el Stock sí debe ser número para que no falle Movimientos
        if pestaña == "Inventario" and "Stock" in df.columns:
            df['Stock'] = pd.to_numeric(df['Stock'], errors='coerce').fillna(0).astype(int)
            
        return df
    except Exception as e:
        return pd.DataFrame()

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
        st.sidebar.success("💾 Sincronizado en Excel")
    except Exception as e:
        st.error(f"❌ Error al guardar en Excel: {e}")

# --- 4. SISTEMA DE SESIÓN ---
if 'conectado' not in st.session_state: st.session_state['conectado'] = False

if not st.session_state['conectado']:
    st.title("🔐 Acceso Jordan Admin Pro")
    u_in = st.text_input("Usuario")
    p_in = st.text_input("Contraseña", type="password")
    
    if st.button("🚀 Ingresar"):
        u_l = u_in.strip().lower()
        
        # 1. Primero chequear LLAVE MAESTRA (Jordan)
        es_m, rol_m = seguridad.verificar_clave(u_l, p_in, None)
        if es_m:
            st.session_state.update({'conectado': True, 'user': u_l, 'nombre': "Jordan (Master)", 'rol': "Desarrollador"})
            st.rerun()
        
        # 2. Si no es Jordan, buscar en la lista de Usuarios cargada del Excel
        else:
            df_u_login = cargar_datos("Usuarios")
            if not df_u_login.empty:
                # Buscamos coincidencia exacta de usuario
                row = df_u_login[df_u_login['Usuario'] == u_l]
                
                if not row.empty:
                    # Usamos la función de seguridad para comparar la clave
                    clave_excel = str(row.iloc[0]['Clave'])
                    valido, _ = seguridad.verificar_clave(u_l, p_in, clave_excel)
                    
                    if valido:
                        st.session_state.update({
                            'conectado': True, 
                            'user': u_l, 
                            'nombre': row.iloc[0]['Nombre'], 
                            'rol': row.iloc[0]['Rol']
                        })
                        st.rerun()
                    else:
                        st.error("❌ Contraseña incorrecta")
                else:
                    st.error("❌ El usuario no existe o no está habilitado")
            else:
                st.error("❌ No se pudo leer la base de datos de usuarios")

else:
    # CARGA PARA MÓDULOS
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

    rol = st.session_state['rol']
    es_admin = rol in ["Desarrollador", "Administrador"]
    es_maestro = rol in ["Desarrollador", "Administrador", "Supervisor", "Maestro de Obra"]

    lista_tabs = ["📦 Inventario", "🔄 Movimientos"]
    if es_maestro: lista_tabs += ["🛠️ Mantenimiento", "🏢 Empresas"]
    if es_admin: lista_tabs += ["👤 Usuarios", "📜 Historial"]

    tabs = st.tabs(lista_tabs)

    with tabs[0]: inventario.mostrar(df_inv, guardar_global, df_mov, df_u, df_mant, df_lug, df_papelera)
    with tabs[1]: movimientos.mostrar(df_inv, df_mov, df_lug, st.session_state['user'], guardar_global, df_u, df_mant, df_papelera)
    
    if es_maestro:
        with tabs[2]: mantenimiento.mostrar(df_mant, df_inv, guardar_global, df_mov, df_u, df_lug, df_papelera)
        with tabs[3]: empresas.mostrar(df_lug, guardar_global, df_inv, df_mov, df_u, df_mant, df_papelera)
    if es_admin:
        with tabs[4]: usuarios.mostrar(df_u, guardar_global, df_inv, df_mov, df_mant, df_lug, df_papelera)
        with tabs[5]: historial.mostrar(df_mov, guardar_global, df_inv, df_u, df_mant, df_lug, df_papelera)
