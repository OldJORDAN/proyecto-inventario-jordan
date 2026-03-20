import streamlit as st
import pandas as pd

def validar_ruc_ecuador_pro(ruc):
    """Validador técnico basado en los 3 algoritmos oficiales del SRI"""
    if len(ruc) != 13 or not ruc.isdigit() or ruc[10:] != "001":
        return False, "❌ Estructura inválida (debe tener 13 dígitos y terminar en 001)."

    provincia = int(ruc[:2])
    if not (0 < provincia <= 24 or provincia == 30):
        return False, "❌ Código de provincia no válido."

    tercer_digito = int(ruc[2])
    
    # 1. SOCIEDADES PÚBLICAS
    if tercer_digito == 6:
        coeficientes = [3, 2, 7, 6, 5, 4, 3, 2]
        verificador = int(ruc[8])
        suma = sum(int(ruc[i]) * coeficientes[i] for i in range(8))
        residuo = 11 - (suma % 11)
        res = 0 if residuo == 11 else residuo
        return (res == verificador), "✅ RUC de Entidad Pública Válido"

    # 2. SOCIEDADES PRIVADAS / JURÍDICAS
    elif tercer_digito == 9:
        coeficientes = [4, 3, 2, 7, 6, 5, 4, 3, 2]
        verificador = int(ruc[9])
        suma = sum(int(ruc[i]) * coeficientes[i] for i in range(9))
        residuo = 11 - (suma % 11)
        res = 0 if residuo == 11 else residuo
        return (res == verificador), "✅ RUC Jurídico Válido"

    # 3. PERSONAS NATURALES
    elif tercer_digito < 6:
        coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
        suma = 0
        for i in range(9):
            mult = int(ruc[i]) * coeficientes[i]
            if mult >= 10: mult -= 9
            suma += mult
        verificador = int(ruc[9])
        res = (10 - (suma % 10)) if suma % 10 != 0 else 0
        return (res == verificador), "✅ RUC de Persona Natural Válido"

    return False, "❌ El número no cumple con los registros del SRI."

def mostrar(df_lug, guardar_global, df_inv, df_mov, df_u, df_mant, df_papelera):
    st.title("🏢 Gestión de Empresas (Validador Universal SRI)")

    # Parche de columnas
    for c in ['Empresa', 'RUC', 'Ubicación', 'Tipo']:
        if c not in df_lug.columns: df_lug[c] = ""

    if 'auth_reg' not in st.session_state: st.session_state.auth_reg = False
    if 'ruc_validado' not in st.session_state: st.session_state.ruc_validado = ""

    # --- 1. SECCIÓN DE VALIDACIÓN ---
    with st.container(border=True):
        st.subheader("🔍 Verificación de RUC")
        col_in, col_btn = st.columns([3, 1])
        with col_in:
            # AJUSTE: Solo las 13 X como ejemplo
            ruc_input = st.text_input("Ingrese RUC para validar:", max_chars=13, placeholder="ej. XXXXXXXXXXXXX")
        with col_btn:
            st.write("##")
            if st.button("🚀 Validar RUC", use_container_width=True):
                valido, msj = validar_ruc_ecuador_pro(ruc_input)
                if valido:
                    st.session_state.auth_reg = True
                    st.session_state.ruc_validado = ruc_input
                    st.success(msj)
                else:
                    st.error(msj)
                    st.session_state.auth_reg = False

    # --- 2. FORMULARIO DE REGISTRO ---
    if st.session_state.auth_reg:
        with st.form("form_reg_final"):
            st.info(f"🔓 Registro habilitado para RUC: {st.session_state.ruc_validado}")
            c1, c2 = st.columns(2)
            with c1:
                nombre_emp = st.text_input("Razón Social / Nombre")
                st.text_input("RUC Vinculado", value=st.session_state.ruc_validado, disabled=True)
            with c2:
                direc = st.text_input("Ubicación Exacta")
                relacion = st.selectbox("Categoría", ["Proveedor", "Sede", "Cliente"])
            
            if st.form_submit_button("💾 GUARDAR EMPRESA", use_container_width=True):
                if nombre_emp and direc:
                    if st.session_state.ruc_validado in df_lug['RUC'].astype(str).values:
                        st.warning("⚠️ Este RUC ya existe.")
                    else:
                        nueva_f = pd.DataFrame([{"Empresa": nombre_emp, "RUC": st.session_state.ruc_validado, "Ubicación": direc, "Tipo": relacion}])
                        df_lug = pd.concat([df_lug, nueva_f], ignore_index=True)
                        guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                        st.success("✅ Guardado.")
                        st.session_state.auth_reg = False
                        st.rerun()
                else: st.error("Llene los campos.")

    st.divider()
    st.subheader("📋 Empresas Registradas")
    st.dataframe(df_lug, use_container_width=True, hide_index=True)
    
    with st.expander("🗑️ Eliminar Empresa"):
        if not df_lug.empty:
            sel = st.selectbox("Seleccione:", df_lug['Empresa'].tolist())
            if st.button("Eliminar", type="primary"):
                df_lug = df_lug[df_lug['Empresa'] != sel].reset_index(drop=True)
                guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                st.rerun()
