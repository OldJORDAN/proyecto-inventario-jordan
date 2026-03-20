import streamlit as st
import pandas as pd
import bcrypt # Importante para leer tus hashes del Excel
from modulos import seguridad, inventario, movimientos, mantenimiento, empresas, usuarios, historial

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Jordan Admin Pro", layout="wide", page_icon="🛠️")

# --- 2. FUNCIÓN DE CARGA DE DATOS ---
def cargar_datos(pestaña):
    try:
        df = pd.read_excel("database.xlsx", sheet_name=pestaña, dtype=str)
        if pestaña == "Usuarios" and not df.empty:
            df.columns = df.columns.str.strip()
            df['Usuario'] = df['Usuario'].str.strip().str.lower()
            if 'Estado_Licencia' not in df.columns:
                df['Estado_Licencia'] = 'Activo'
        return df
    except:
        return pd.DataFrame()

# --- 3. LÓGICA DE LOGIN CON DESENCRIPTACIÓN ---
def verificar_acceso(usuario_ingresado, clave_ingresada, df_usuarios):
    # 1. Buscar el usuario en el DF
    row = df_usuarios[df_usuarios['Usuario'] == usuario_ingresado]
    
    if not row.empty:
        hash_excel = str(row.iloc[0]['Clave']).strip()
        estado = str(row.iloc[0].get('Estado_Licencia', 'Activo'))
        
        if estado != "Activo":
            return False, "🚫 LICENCIA DESHABILITADA", None
        
        try:
            # ESTA ES LA MAGIA: Compara el texto plano con el Hash del Excel
            if bcrypt.checkpw(clave_ingresada.encode('utf-8'), hash_excel.encode('utf-8')):
                return True, "✅ Éxito", row.iloc[0]
            else:
                return False, "❌ Contraseña incorrecta", None
        except Exception as e:
            # Por si acaso alguna clave en el Excel NO esté encriptada y dé error
            if clave_ingresada == hash_excel:
                return True, "✅ Éxito (Legacy)", row.iloc[0]
            return False, f"❌ Error de formato de clave", None
            
    return False, "❌ Usuario no encontrado", None

# --- 4. INTERFAZ DE ACCESO ---
if 'conectado' not in st.session_state: st.session_state['conectado'] = False

if not st.session_state['conectado']:
    st.title("🔐 Acceso Jordan Admin Pro")
    u_in = st.text_input("Usuario").strip().lower()
    p_in = st.text_input("Contraseña", type="password")
    
    if st.button("🚀 Ingresar"):
        # Primero: Chequear contra el Excel con Bcrypt
        df_u = cargar_datos("Usuarios")
        if not df_u.empty:
            es_valido, mensaje, datos_usuario = verificar_acceso(u_in, p_in, df_u)
            
            if es_valido:
                st.session_state.update({
                    'conectado': True, 
                    'user': u_in, 
                    'nombre': datos_usuario['Nombre'], 
                    'rol': datos_usuario['Rol']
                })
                st.rerun()
            else:
                st.error(mensaje)
        else:
            st.error("No se pudo cargar la base de datos de usuarios.")

else:
    # --- PANEL PRINCIPAL (SI YA ESTÁ CONECTADO) ---
    df_inv = cargar_datos("Inventario")
    df_mov = cargar_datos("Movimientos")
    df_u = cargar_datos("Usuarios")
    # ... resto de la carga y tabs ...
    st.sidebar.success(f"Conectado como: {st.session_state['nombre']}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['conectado'] = False
        st.rerun()
