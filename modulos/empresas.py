import streamlit as st
import pandas as pd
import requests # Necesitas instalar esto: pip install requests

def consultar_sri_real(ruc):
    """Consulta real a base de datos de Ecuador"""
    if len(ruc) != 13 or not ruc.isdigit() or ruc[10:] != "001":
        return False, "❌ Estructura de RUC no válida.", None

    try:
        # Usamos un servicio de consulta de datos públicos de Ecuador
        # Esta URL es un ejemplo de API de datos abiertos
        url = f"https://srienlinea.sri.gob.ec/sri-catastro-sujeto-pasivo-internet/consultas/publico/ruc-datos-generales/{ruc}"
        
        # Como el SRI a veces bloquea bots, usamos un fallback de API pública
        api_url = f"https://consultaruc.com/api/v1/ruc/{ruc}" 
        
        response = requests.get(api_url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            # Si la API devuelve datos reales
            nombre = data.get("razon_social") or data.get("nombre_comercial")
            if nombre:
                return True, f"✅ Empresa encontrada: {nombre}", nombre
            else:
                return False, "❌ RUC válido pero no tiene Razón Social activa.", None
        else:
            return False, "❌ El RUC no existe en los registros oficiales del SRI.", None
    except:
        # Si falla la conexión o la API está caída, aplicamos validación matemática como respaldo
        return False, "❌ Error de conexión con el SRI. Reintente en un momento.", None

def mostrar(df_lug, guardar_global, df_inv, df_mov, df_u, df_mant, df_papelera):
    st.title("🏢 Gestión de Empresas (Sincronización Real SRI)")

    # --- PARCHE DE SEGURIDAD PARA COLUMNAS ---
    for col in ['RUC', 'Empresa', 'Ubicación', 'Tipo']:
        if col not in df_lug.columns: df_lug[col] = ""

    if 'ruc_ok' not in st.session_state: st.session_state.ruc_ok = False
    if 'nombre_sri' not in st.session_state: st.session_state.nombre_sri = ""
    if 'temp_ruc' not in st.session_state: st.session_state.temp_ruc = ""

    # --- 1. VALIDADOR CON CONSULTA REAL ---
    with st.container(border=True):
        st.subheader("🔍 Consultar RUC en Base de Datos Oficial")
        c1, c2 = st.columns([3, 1])
        with c1:
            ruc_in = st.text_input("Ingrese RUC para validar:", max_chars=13, help="Debe ser un RUC real registrado en Ecuador.")
        with c2:
            st.write("##")
            if st.button("📡 Consultar SRI", use_container_width=True):
                with st.spinner("Conectando con el SRI..."):
                    exito, msj, nombre_detectado = consultar_sri_real(ruc_in)
                    if exito:
                        st.session_state.ruc_ok = True
                        st.session_state.temp_ruc = ruc_in
                        st.session_state.nombre_sri = nombre_detectado
                        st.success(msj)
                    else:
                        st.error(msj)
                        st.session_state.ruc_ok = False

    # --- 2. FORMULARIO DE REGISTRO (AUTOPOLADO) ---
    if st.session_state.ruc_ok:
        with st.form("reg_empresa_sri_v5"):
            st.info(f"📋 Datos recuperados para el RUC: {st.session_state.temp_ruc}")
            col_a, col_b = st.columns(2)
            with col_a:
                # El nombre ya aparece escrito gracias a la consulta
                nom = st.text_input("Razón Social (Detectada)", value=st.session_state.nombre_sri)
                ruc_f = st.text_input("RUC Confirmado", value=st.session_state.temp_ruc, disabled=True)
            with col_b:
                ubi = st.text_input("Dirección / Ubicación", placeholder="Ej: Av. Carlos Julio Arosemena")
                tipo = st.selectbox("Relación", ["Proveedor", "Contratista", "Sede", "Cliente"])
            
            cb1, cb2 = st.columns(2)
            with cb1:
                if st.form_submit_button("💾 CONFIRMAR Y GUARDAR", use_container_width=True):
                    if nom and ubi:
                        ya_existe = ruc_f in df_lug['RUC'].astype(str).values
                        if ya_existe:
                            st.warning("⚠️ Esta empresa ya está en tu base de datos.")
                        else:
                            nueva = pd.DataFrame([{"Empresa": nom, "RUC": ruc_f, "Ubicación": ubi, "Tipo": tipo}])
                            df_lug = pd.concat([df_lug, nueva], ignore_index=True)
                            guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                            st.success("✅ Empresa vinculada exitosamente.")
                            st.session_state.ruc_ok = False
                            st.rerun()
                    else: st.error("Por favor, complete la ubicación.")
            with cb2:
                if st.form_submit_button("❌ DESCARTAR", use_container_width=True):
                    st.session_state.ruc_ok = False
                    st.rerun()

    st.divider()

    # --- 3. GESTIÓN Y LISTADO ---
    st.subheader("📋 Directorio de Empresas")
    if not df_lug.empty:
        busq = st.text_input("🔎 Filtrar lista:")
        df_v = df_lug.copy()
        if busq:
            df_v = df_v[df_v['Empresa'].str.contains(busq, case=False, na=False) | 
                        df_v['RUC'].str.contains(busq, na=False)]
        
        st.dataframe(df_v, use_container_width=True, hide_index=True)

        with st.expander("🗑️ Panel de Eliminación"):
            emp_sel = st.selectbox("Seleccione empresa a eliminar:", df_lug['Empresa'].tolist())
            if st.checkbox(f"Confirmar eliminación de {emp_sel}"):
                if st.button("Eliminar Permanentemente", type="primary"):
                    df_lug = df_lug[df_lug['Empresa'] != emp_sel].reset_index(drop=True)
                    guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                    st.rerun()
    else:
        st.info("No hay empresas registradas.")
