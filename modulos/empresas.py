import streamlit as st
import pandas as pd

def algoritmo_sri(ruc):
    """Valida matemáticamente si un RUC es real en Ecuador"""
    if len(ruc) != 13 or not ruc.isdigit() or ruc[10:] != "001":
        return False
    
    # Verificación de cédula base (primeros 10 dígitos)
    coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    suma = 0
    for i in range(9):
        mult = int(ruc[i]) * coeficientes[i]
        if mult >= 10: mult -= 9
        suma += mult
    
    verificador = (10 - (suma % 10)) if suma % 10 != 0 else 0
    return verificador == int(ruc[9])

def mostrar(df_lug, guardar_global, df_inv, df_mov, df_u, df_mant, df_papelera):
    st.title("🏢 Gestión de Empresas (Validador Offline)")

    # Parche de columnas
    for col in ['RUC', 'Empresa', 'Ubicación', 'Tipo']:
        if col not in df_lug.columns: df_lug[col] = ""

    if 'ruc_confirmado' not in st.session_state: st.session_state.ruc_confirmado = False
    if 'ruc_actual' not in st.session_state: st.session_state.ruc_actual = ""

    # --- 1. VALIDADOR MATEMÁTICO ---
    with st.container(border=True):
        st.subheader("🔍 Verificación de Identidad Jurídica")
        c1, c2 = st.columns([3, 1])
        with c1:
            ruc_in = st.text_input("Ingrese RUC (13 dígitos):", max_chars=13)
        with c2:
            st.write("##")
            if st.button("🚀 Validar Estructura", use_container_width=True):
                if algoritmo_sri(ruc_in):
                    st.session_state.ruc_confirmado = True
                    st.session_state.ruc_actual = ruc_in
                    st.success("✅ RUC Matemáticamente Válido")
                else:
                    st.error("❌ RUC Falso o Inválido. Verifique los números.")
                    st.session_state.ruc_confirmado = False

    # --- 2. REGISTRO (SOLO SE ABRE SI EL RUC ES REAL) ---
    if st.session_state.ruc_confirmado:
        with st.form("reg_manual_confirm"):
            st.info(f"🔓 Registro habilitado para: {st.session_state.ruc_actual}")
            col_a, col_b = st.columns(2)
            with col_a:
                nom = st.text_input("Razón Social / Nombre Comercial")
                # El RUC no se puede editar aquí, viene de la validación
                st.text_input("RUC", value=st.session_state.ruc_actual, disabled=True)
            with col_b:
                ubi = st.text_input("Dirección Principal")
                tipo = st.selectbox("Tipo", ["Proveedor", "Contratista", "Cliente"])
            
            if st.form_submit_button("💾 GUARDAR EMPRESA", use_container_width=True):
                if nom and ubi:
                    if st.session_state.ruc_actual in df_lug['RUC'].astype(str).values:
                        st.warning("Esta empresa ya existe.")
                    else:
                        nueva = pd.DataFrame([{"Empresa": nom, "RUC": st.session_state.ruc_actual, "Ubicación": ubi, "Tipo": tipo}])
                        df_lug = pd.concat([df_lug, nueva], ignore_index=True)
                        guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                        st.success("✅ Empresa guardada correctamente.")
                        st.session_state.ruc_confirmado = False
                        st.rerun()
                else: st.error("Llene todos los campos.")

    st.divider()
    st.subheader("📋 Directorio")
    st.dataframe(df_lug, use_container_width=True, hide_index=True)
