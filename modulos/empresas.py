import streamlit as st
import pandas as pd

def validar_ruc_universal(ruc):
    """Validador oficial del SRI para todo tipo de RUC en Ecuador"""
    if len(ruc) != 13 or not ruc.isdigit() or ruc[10:] != "001":
        return False, "❌ Estructura inválida (debe tener 13 dígitos y terminar en 001)."

    provincia = int(ruc[:2])
    if not (0 < provincia <= 24 or provincia == 30):
        return False, "❌ Código de provincia no válido."

    digito_tercero = int(ruc[2])
    
    # 1. SOCIEDADES PÚBLICAS (Tercer dígito = 6)
    if digito_tercero == 6:
        coeficientes = [3, 2, 7, 6, 5, 4, 3, 2]
        verificador = int(ruc[8])
        suma = sum(int(ruc[i]) * coeficientes[i] for i in range(8))
        residuo = 11 - (suma % 11)
        res = 0 if residuo == 11 else residuo
        return (res == verificador), "✅ RUC de Entidad Pública Válido"

    # 2. SOCIEDADES PRIVADAS / EXTRANJEROS (Tercer dígito = 9)
    elif digito_tercero == 9:
        coeficientes = [4, 3, 2, 7, 6, 5, 4, 3, 2]
        verificador = int(ruc[9])
        suma = sum(int(ruc[i]) * coeficientes[i] for i in range(9))
        residuo = 11 - (suma % 11)
        res = 0 if residuo == 11 else residuo
        return (res == verificador), "✅ RUC de Sociedad Privada Válido (Ej: Claro/Tech)"

    # 3. PERSONAS NATURALES (Tercer dígito < 6)
    elif digito_tercero < 6:
        coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
        suma = 0
        for i in range(9):
            mult = int(ruc[i]) * coeficientes[i]
            if mult >= 10: mult -= 9
            suma += mult
        verificador = int(ruc[9])
        res = (10 - (suma % 10)) if suma % 10 != 0 else 0
        return (res == verificador), "✅ RUC de Persona Natural Válido"

    return False, "❌ El número no cumple con los algoritmos del SRI."

def mostrar(df_lug, guardar_global, df_inv, df_mov, df_u, df_mant, df_papelera):
    st.title("🏢 Gestión de Empresas (Validador Universal SRI)")

    # Parche de columnas por si acaso
    for col in ['RUC', 'Empresa', 'Ubicación', 'Tipo']:
        if col not in df_lug.columns: df_lug[col] = ""

    if 'ruc_final' not in st.session_state: st.session_state.ruc_final = ""
    if 'auth_registro' not in st.session_state: st.session_state.auth_registro = False

    # --- 1. MÓDULO DE VALIDACIÓN ---
    with st.container(border=True):
        st.subheader("🔍 Verificación de RUC")
        c1, c2 = st.columns([3, 1])
        with c1:
            ruc_in = st.text_input("Ingrese RUC para validar:", max_chars=13, placeholder="Ej: 1790016919001 (Claro)")
        with c2:
            st.write("##")
            if st.button("🚀 Validar RUC", use_container_width=True):
                es_valido, msj = validar_ruc_universal(ruc_in)
                if es_valido:
                    st.session_state.auth_registro = True
                    st.session_state.ruc_final = ruc_in
                    st.success(msj)
                else:
                    st.error(msj)
                    st.session_state.auth_registro = False

    # --- 2. FORMULARIO DE REGISTRO ---
    if st.session_state.auth_registro:
        with st.form("reg_final_ruc"):
            st.info(f"🔓 Registrando empresa con RUC: {st.session_state.ruc_final}")
            col1, col2 = st.columns(2)
            with col1:
                nom = st.text_input("Razón Social / Nombre de Proyecto")
                st.text_input("Número de RUC", value=st.session_state.ruc_final, disabled=True)
            with col2:
                ubi = st.text_input("Dirección / Ubicación Exacta")
                tip = st.selectbox("Tipo de Relación", ["Proveedor", "Contratista", "Sede", "Cliente"])

            if st.form_submit_button("💾 GUARDAR EMPRESA", use_container_width=True):
                if nom and ubi:
                    if st.session_state.ruc_final in df_lug['RUC'].astype(str).values:
                        st.warning("⚠️ Este RUC ya está registrado en tu sistema.")
                    else:
                        nueva = pd.DataFrame([{"Empresa": nom, "RUC": st.session_state.ruc_final, "Ubicación": ubi, "Tipo": tip}])
                        df_lug = pd.concat([df_lug, nueva], ignore_index=True)
                        guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                        st.success("✅ Empresa guardada en la base de datos.")
                        st.session_state.auth_registro = False
                        st.rerun()
                else: st.error("Llene todos los campos para continuar.")

    st.divider()
    st.subheader("📋 Empresas Registradas")
    st.dataframe(df_lug, use_container_width=True, hide_index=True)
    
    with st.expander("🗑️ Eliminar Empresa"):
        if not df_lug.empty:
            sel = st.selectbox("Seleccione para borrar:", df_lug['Empresa'].tolist())
            if st.button("Confirmar Borrado", type="primary"):
                df_lug = df_lug[df_lug['Empresa'] != sel].reset_index(drop=True)
                guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                st.rerun()
