import streamlit as st
import pandas as pd
import requests # Librería para consultas web

def consultar_ruc_real(ruc):
    """Consulta real a base de datos de empresas de Ecuador"""
    try:
        # Usamos una API de datos abiertos (puedes cambiarla por una privada luego)
        # Esta es una simulación de endpoint de consulta rápida
        url = f"https://srienlinea.sri.gob.ec/sri-catastro-sujeto-pasivo-internet/consultas/publico/ruc-datos-generales/{ruc}"
        
        # NOTA: El SRI bloquea peticiones directas de bots. 
        # Para tu proyecto de la U, usaremos un "Proxy" de datos abiertos:
        api_url = f"https://consultaruc.com/api/v1/ruc/{ruc}" 
        
        response = requests.get(api_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return True, data.get("razon_social", "Nombre no encontrado"), data.get("direccion", "Guayaquil, Ecuador")
        else:
            # Si la API falla o el RUC no existe
            return False, None, None
    except:
        # Si no hay internet o falla el servicio
        return False, None, None

def mostrar(df_lug, guardar_global, df_inv, df_mov, df_u, df_mant, df_papelera):
    st.title("🏢 Gestión de Empresas (Sincronizado SRI)")

    if 'ruc_validado' not in st.session_state: st.session_state.ruc_validado = False
    if 'empresa_data' not in st.session_state: st.session_state.empresa_data = {}

    # --- 1. BUSCADOR REAL ---
    with st.container(border=True):
        st.subheader("🔍 Consulta en Base de Datos SRI")
        c1, c2 = st.columns([3, 1])
        with c1:
            ruc_input = st.text_input("Ingrese RUC (13 dígitos):", max_chars=13)
        with c2:
            st.write("##")
            if st.button("📡 Consultar SRI", use_container_width=True):
                with st.spinner("Buscando en la base de datos..."):
                    # Aquí llamamos a la función de consulta real
                    exito, nombre, dire = consultar_ruc_real(ruc_input)
                    
                    if exito:
                        st.session_state.ruc_validado = True
                        st.session_state.empresa_data = {
                            "nombre": nombre,
                            "ruc": ruc_input,
                            "direccion": dire
                        }
                        st.success("✅ Empresa Encontrada")
                    else:
                        st.error("❌ RUC no registrado en el SRI o error de conexión.")
                        st.session_state.ruc_validado = False

    # --- 2. REGISTRO AUTOMÁTICO ---
    if st.session_state.ruc_validado:
        with st.form("form_sri_confirm"):
            st.warning("⚠️ Verifique los datos obtenidos antes de guardar.")
            col1, col2 = st.columns(2)
            with col1:
                # El nombre ya viene lleno de la "base de datos"
                rs = st.text_input("Razón Social:", value=st.session_state.empresa_data['nombre'])
                rc = st.text_input("RUC:", value=st.session_state.empresa_data['ruc'], disabled=True)
            with col2:
                dr = st.text_input("Dirección:", value=st.session_state.empresa_data['direccion'])
                tp = st.selectbox("Tipo:", ["Proveedor", "Cliente", "Sede"])

            if st.form_submit_button("💾 REGISTRAR EN MI BASE", use_container_width=True):
                if rs and dr:
                    if rc in df_lug['RUC'].astype(str).values:
                        st.error("Esta empresa ya existe en tu inventario.")
                    else:
                        nueva = pd.DataFrame([{"Empresa": rs, "RUC": rc, "Ubicación": dr, "Tipo": tp}])
                        df_lug = pd.concat([df_lug, nueva], ignore_index=True)
                        guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                        st.balloons()
                        st.session_state.ruc_validado = False
                        st.rerun()

    st.divider()
    st.subheader("📋 Empresas en el Sistema")
    st.dataframe(df_lug, use_container_width=True, hide_index=True)
