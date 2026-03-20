import streamlit as st
import pandas as pd
import bcrypt
from modulos import seguridad, inventario, movimientos, mantenimiento, empresas, usuarios, historial

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Jordan Admin Pro", layout="wide", page_icon="🛠️")

# --- 2. CARGA DE DATOS CON CACHÉ (VELOCIDAD MÁXIMA) ---
@st.cache_data(ttl=600)
def cargar_datos(pestaña):
    try:
        # Lee del Excel y guarda en memoria RAM para que sea instantáneo
        df = pd.read_excel("database.xlsx", sheet_name=pestaña, dtype=str)
        
        if pestaña == "Usuarios" and not df.empty:
            df.columns = df.columns.str.strip()
            # Limpiamos nombres de columnas y datos para evitar errores de login
            df['Usuario'] = df['Usuario'].astype(str).str.strip()
            if 'Estado_Licencia' not in df.columns: df['Estado_Licencia'] = 'Activo'
            df['Estado_Licencia'] = df['Estado_Licencia'].fillna('Activo')
        
        if pestaña == "Inventario" and not df.empty:
            if 'Stock' in df.columns:
                df['Stock'] = pd.to_numeric(df['Stock'], errors='coerce').fillna(0).astype(int)
        
        if pestaña == "Movimientos" and not df.empty:
            if 'Cantidad' in df.columns:
                df['Cantidad'] = pd.to_numeric(df['Cantidad'], errors='coerce').fillna(0)
            
        return df
    except Exception as e:
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
        
        # IMPORTANTE: Borra el caché para que los cambios se vean al instante
        st.cache_data.clear()
        st.sidebar.success("💾 ¡Base Sincronizada!")
    except Exception as e:
        st.error(f"❌ Error al guardar: {e}")

# --- 4. LÓGICA DE ACCESO (LOGIN INTELIGENTE) ---
if 'conectado' not in st.session_state: st.session_state['conectado'] = False

if not st.session_state['conectado']:
    st.title("🔐 Acceso Jordan Admin Pro")
    u_in = st.text_input("Usuario").strip() # Quitamos el .lower() aquí para ver qué escribe
    p_in = st.text_input("Contraseña", type="password")
    
    if st.button("🚀 Ingresar al Sistema"):
        df_u_login = cargar_datos("Usuarios")
        if not df_u_login.empty:
            # Comparamos sin importar Mayúsculas/Minúsculas
            u_buscado = u_in.lower().strip()
            df_u_login['Usuario_Match'] = df_u_login['Usuario'].astype(str).str.lower().str.strip()
            
            row = df_u_login[df_u_login['Usuario_Match'] == u_buscado]
            
            if not row.empty:
                clave_excel = str(row.iloc[0]['Clave']).strip()
                estado = str(row.iloc[0].get('Estado_Licencia', 'Activo'))
                
                if estado != "Activo":
                    st.error("🚫 LICENCIA DESHABILITADA: Contacte al Desarrollador")
                else:
                    es_valido = False
                    # 1. Intentar con Bcrypt (claves encriptadas)
                    if clave_excel.startswith('$2b$'):
                        try:
                            if bcrypt.checkpw(p_in.encode('utf-8'), clave_excel.encode('utf-8')):
                                es_valido = True
                        except: pass
                    
                    # 2. Intentar como texto normal (Tu clave 170362)
                    if not es_valido and p_in == clave_excel:
                        es_valido = True
                    
                    if es_valido:
                        st.session_state.update({
                            'conectado': True, 
                            'user': u_buscado, 
                            'nombre': row.iloc[0]['Nombre'], 
                            'rol': row.iloc[0]['Rol']
                        })
                        st.cache_data.clear() # Limpia para cargar el nuevo perfil
                        st.rerun()
                    else:
                        st.error("❌ Contraseña incorrecta")
            else:
                st.error(f"❌ El usuario '{u_in}' no existe")

# --- 5. PANEL PRINCIPAL (AQUÍ ENTRAS TÚ) ---
else:
    # Carga de datos instantánea
    df_inv = cargar_datos("Inventario"); df_mov = cargar_datos("Movimientos")
    df_u = cargar_datos("Usuarios"); df_mant = cargar_datos("Mantenimiento")
    df_lug = cargar_datos("Lugares"); df_papelera = cargar_datos("Papelera")

    # Sidebar con diseño profesional
    with st.sidebar:
        st.title(f"👤 {st.session_state['nombre']}")
        st.markdown(f"""
            <div style="background-color: #1E1E1E; padding: 10px; border-radius: 5px; border-left: 5px solid #0078D4;">
                <p style="margin: 0; color: #888; font-size: 0.8em;">Rol de Usuario:</p>
                <p style="margin: 0; color: #0078D4; font-weight: bold; font-size: 1.1em;">{st.session_state['rol']}</p>
            </div>
        """, unsafe_allow_html=True)
        st.write("---")
        if st.button("🚪 Cerrar Sesión"):
            st.session_state['conectado'] = False
            st.cache_data.clear()
            st.rerun()

    # Lógica de permisos por pestañas
    rol = st.session_state['rol']
    es_admin = any(x in rol for x in ["Desarrollador", "Administrador"])
    es_mando = any(x in rol for x in ["Desarrollador", "Administrador", "Supervisor", "Maestro de Obra"])
    
    lista_tabs = ["📦 Inventario", "🔄 Movimientos"]
    if es_mando: lista_tabs += ["🛠️ Mantenimiento", "🏢 Empresas"]
    if es_admin: lista_tabs += ["👤 Usuarios", "📜 Historial"]

    tabs = st.tabs(lista_tabs)

    # Conexión con los módulos
    with tabs[0]: 
        inventario.mostrar(df_inv, guardar_global, df_mov, df_u, df_mant, df_lug, df_papelera)
    with tabs[1]: 
        movimientos.mostrar(df_inv, df_mov, df_lug, st.session_state['user'], guardar_global, df_u, df_mant, df_papelera)
    
    try:
        if es_mando:
            with tabs[2]: mantenimiento.mostrar(df_mant, df_inv, guardar_global, df_mov, df_u, df_lug, df_papelera)
            with tabs[3]: empresas.mostrar(df_lug, guardar_global, df_inv, df_mov, df_u, df_mant, df_papelera)
        if es_admin:
            with tabs[4]: usuarios.mostrar(df_u, guardar_global, df_inv, df_mov, df_mant, df_lug, df_papelera)
            with tabs[5]: historial.mostrar(df_mov, guardar_global, df_inv, df_u, df_mant, df_lug, df_papelera)
    except IndexError:
        pass
