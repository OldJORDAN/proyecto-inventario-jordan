import streamlit as st
import pandas as pd
import bcrypt
import time
from modulos import seguridad, inventario, movimientos, mantenimiento, empresas, usuarios, historial

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Jordan Admin Pro", layout="wide", page_icon="🛠️")

# --- 2. FUNCIÓN DE CARGA DE DATOS (SIN CACHÉ PARA EVITAR ERRORES) ---
def cargar_datos(pestaña):
    try:
        # Intentamos leer el Excel
        df = pd.read_excel("database.xlsx", sheet_name=pestaña, dtype=str)
        if pestaña == "Usuarios" and not df.empty:
            df.columns = df.columns.str.strip()
            df['Usuario'] = df['Usuario'].astype(str).str.strip().str.lower()
            if 'Estado_Licencia' not in df.columns:
                df['Estado_Licencia'] = 'Activo'
        return df
    except Exception as e:
        # Si el archivo está ocupado, esperamos un poquito y reintentamos
        time.sleep(0.5)
        try:
            return pd.read_excel("database.xlsx", sheet_name=pestaña, dtype=str)
        except:
            return pd.DataFrame()

# --- 3. FUNCIÓN DE GUARDADO GLOBAL ---
def guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera):
    try:
        with pd.ExcelWriter("database.xlsx", engine="openpyxl") as writer:
            df_inv.to_excel(writer, sheet_name="Inventario", index=False)
            df_mov.to_excel(writer, sheet_name="Movimientos", index=False)
            df_u.to_excel(writer, sheet_name="Usuarios", index=False)
            df_mant.to_excel(writer, sheet_name="Mantenimiento", index=False)
            df_lug.to_excel(writer, sheet_name="Lugares", index=False)
            df_papelera.to_excel(writer, sheet_name='Papelera', index=False)
        st.sidebar.success("💾 Base Actualizada")
    except Exception as e:
        st.error(f"❌ Error al guardar en Excel: {e}")

# --- 4. LÓGICA DE ACCESO (LOGIN) ---
if 'conectado' not in st.session_state:
    st.session_state['conectado'] = False

if not st.session_state['conectado']:
    st.title("🔐 Acceso Jordan Admin Pro")
    u_in = st.text_input("Usuario").strip().lower()
    p_in = st.text_input("Contraseña", type="password")
    
    if st.button("🚀 Ingresar"):
        df_u_login = cargar_datos("Usuarios")
        if not df_u_login.empty:
            row = df_u_login[df_u_login['Usuario'] == u_in]
            if not row.empty:
                clave_ex = str(row.iloc[0]['Clave']).strip()
                valido = False
                # Verificar si la clave está encriptada con bcrypt
                if clave_ex.startswith('$2b$'):
                    try:
                        if bcrypt.checkpw(p_in.encode(), clave_ex.encode()):
                            valido = True
                    except:
                        pass
                # O si es texto plano (para tus usuarios de prueba)
                if not valido and p_in == clave_ex:
                    valido = True
                
                if valido:
                    st.session_state.update({
                        'conectado': True, 
                        'user': u_in, 
                        'nombre': row.iloc[0]['Nombre'], 
                        'rol': row.iloc[0]['Rol']
                    })
                    st.rerun()
                else:
                    st.error("❌ Contraseña incorrecta")
            else:
                st.error("❌ El usuario no existe")

# --- 5. PANEL PRINCIPAL (SI YA ESTÁ LOGUEADO) ---
else:
    # Cargamos todos los datos necesarios para los módulos
    df_inv = cargar_datos("Inventario")
    df_mov = cargar_datos("Movimientos")
    df_u = cargar_datos("Usuarios")
    df_mant = cargar_datos("Mantenimiento")
    df_lug = cargar_datos("Lugares")
    df_papelera = cargar_datos("Papelera")

    # Sidebar con info del usuario
    with st.sidebar:
        st.title(f"👤 {st.session_state['nombre']}")
        st.info(f"Rol: {st.session_state['rol']}")
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state['conectado'] = False
            st.rerun()
        st.write("---")

    # Definición de permisos por Rol
    rol = st.session_state['rol']
    es_admin = any(x in rol for x in ["Desarrollador", "Administrador"])
    es_mando = any(x in rol for x in ["Desarrollador", "Administrador", "Supervisor", "Maestro de Obra"])
    
    # Creamos las pestañas dinámicamente
    tabs_n = ["📦 Inventario", "🔄 Movimientos"]
    if es_mando:
        tabs_n += ["🛠️ Mantenimiento", "🏢 Empresas"]
    if es_admin:
        tabs_n += ["👤 Usuarios", "📜 Historial"]
    
    tabs = st.tabs(tabs_n)

    # 1. Pestaña Inventario
    with tabs[0]:
        inventario.mostrar(df_inv, guardar_global, df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
    
    # 2. Pestaña Movimientos
    with tabs[1]:
        movimientos.mostrar(df_inv, df_mov, df_lug, st.session_state['user'], guardar_global, df_u, df_mant, df_papelera)
    
    # Pestañas condicionales (Mando/Admin)
    try:
        current_tab = 2
        if es_mando:
            with tabs[current_tab]:
                mantenimiento.mostrar(df_mant, df_inv, guardar_global, df_mov, df_u, df_lug, df_papelera)
            current_tab += 1
            with tabs[current_tab]:
                empresas.mostrar(df_lug, guardar_global, df_inv, df_mov, df_u, df_mant, df_papelera)
            current_tab += 1
            
        if es_admin:
            with tabs[current_tab]:
                usuarios.mostrar(df_u, guardar_global, df_inv, df_mov, df_mant, df_lug, df_papelera)
            current_tab += 1
            with tabs[current_tab]:
                historial.mostrar(df_mov, guardar_global, df_inv, df_u, df_mant, df_lug, df_papelera)
    except Exception as e:
        # Esto evita que la app muera si una pestaña falla
        pass
