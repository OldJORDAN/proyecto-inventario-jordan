import streamlit as st
import pandas as pd

def validar_ruc_ecuador(ruc):
    if len(ruc) != 13 or not ruc.isdigit():
        return False, "❌ El RUC debe tener 13 dígitos numéricos."
    if ruc[10:] != "001":
        return False, "❌ El RUC debe terminar en '001'."
    return True, "✅ RUC Válido"

def mostrar(df_lug, guardar_global, df_inv, df_mov, df_u, df_mant, df_papelera):
    st.title("🏢 Gestión de Empresas (Validación SRI)")

    # --- PARCHE DE SEGURIDAD PARA COLUMNAS ---
    if 'RUC' not in df_lug.columns: df_lug['RUC'] = ""
    if 'Empresa' not in df_lug.columns: df_lug['Empresa'] = ""
    if 'Ubicación' not in df_lug.columns: df_lug['Ubicación'] = ""
    if 'Tipo' not in df_lug.columns: df_lug['Tipo'] = ""

    if 'ruc_ok' not in st.session_state: st.session_state.ruc_ok = False
    if 'temp_ruc' not in st.session_state: st.session_state.temp_ruc = ""

    # --- 1. VALIDADOR ---
    with st.container(border=True):
        st.subheader("🔍 Validador de Identidad Jurídica")
        c1, c2 = st.columns([3, 1])
        with c1:
            ruc_in = st.text_input("Ingrese RUC para validar:", max_chars=13)
        with c2:
            st.write("##")
            if st.button("🚀 Validar en SRI", use_container_width=True):
                val, msj = validar_ruc_ecuador(ruc_in)
                if val:
                    st.session_state.ruc_ok = True
                    st.session_state.temp_ruc = ruc_in
                    st.toast(msj)
                else:
                    st.error(msj)
                    st.session_state.ruc_ok = False

    # --- 2. FORMULARIO DE REGISTRO ---
    if st.session_state.ruc_ok:
        with st.form("reg_empresa_v4"):
            st.success(f"🔓 Formulario habilitado para RUC: {st.session_state.temp_ruc}")
            col_a, col_b = st.columns(2)
            with col_a:
                nom = st.text_input("Razón Social")
                ruc_f = st.text_input("RUC", value=st.session_state.temp_ruc, disabled=True)
            with col_b:
                ubi = st.text_input("Dirección / Ubicación")
                tipo = st.selectbox("Relación", ["Proveedor", "Contratista", "Cliente"])
            
            cb1, cb2 = st.columns(2)
            with cb1:
                if st.form_submit_button("💾 GUARDAR EMPRESA", use_container_width=True):
                    if nom and ubi:
                        # Buscamos si ya existe (evitando el KeyError)
                        ya_existe = ruc_f in df_lug['RUC'].astype(str).values
                        if ya_existe:
                            st.warning("⚠️ Este RUC ya está registrado.")
                        else:
                            nueva = pd.DataFrame([{"Empresa": nom, "RUC": ruc_f, "Ubicación": ubi, "Tipo": tipo}])
                            df_lug = pd.concat([df_lug, nueva], ignore_index=True)
                            guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                            st.success("✅ Empresa guardada.")
                            st.session_state.ruc_ok = False
                            st.rerun()
                    else: st.error("Faltan datos.")
            with cb2:
                if st.form_submit_button("❌ CANCELAR", use_container_width=True):
                    st.session_state.ruc_ok = False
                    st.rerun()

    st.divider()

    # --- 3. GESTIÓN Y BORRADO (LO QUE BUSCABAS) ---
    st.subheader("📋 Empresas Registradas")
    if not df_lug.empty:
        # Filtro de búsqueda
        busq = st.text_input("🔎 Buscar empresa por nombre o RUC:")
        df_v = df_lug.copy()
        if busq:
            df_v = df_v[df_v['Empresa'].str.contains(busq, case=False, na=False) | 
                        df_v['RUC'].str.contains(busq, na=False)]
        
        st.dataframe(df_v, use_container_width=True, hide_index=True)

        # PANEL DE BORRADO
        with st.expander("🗑️ Panel de Eliminación"):
            lista_emp = df_lug['Empresa'].tolist()
            emp_sel = st.selectbox("Seleccione empresa a eliminar:", lista_emp)
            if st.checkbox("Confirmar que deseo eliminar esta empresa"):
                if st.button("Eliminar Permanentemente", type="primary"):
                    df_lug = df_lug[df_lug['Empresa'] != emp_sel].reset_index(drop=True)
                    guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                    st.success(f"Empresa {emp_sel} eliminada.")
                    st.rerun()
    else:
        st.info("No hay empresas en la base de datos.")
