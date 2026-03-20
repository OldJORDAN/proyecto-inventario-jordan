import streamlit as st
import pandas as pd

def mostrar(df_lug, guardar_global, df_inv, df_mov, df_u, df_mant, df_papelera):
    st.title("🏢 Gestión de Empresas y Proveedores")

    # --- 1. BUSCADOR / VALIDADOR DE RUC ---
    st.subheader("🔍 Consultar Empresa por RUC")
    
    # Usamos session_state para que los datos no se borren al dar clic
    if 'ruc_temp' not in st.session_state: st.session_state.ruc_temp = ""
    if 'datos_encontrados' not in st.session_state: st.session_state.datos_encontrados = None

    col1, col2 = st.columns([3, 1])
    with col1:
        ruc_input = st.text_input("Ingrese el número de RUC (13 dígitos):", max_chars=13)
    with col2:
        st.write("##") # Espaciador
        if st.button("🔎 Consultar RUC", use_container_width=True):
            if len(ruc_input) == 13 and ruc_input.isdigit():
                # AQUÍ SIMULAMOS LA CONSULTA
                # En un futuro podrías conectar esto a una API real
                st.session_state.ruc_temp = ruc_input
                st.session_state.datos_encontrados = {
                    "Nombre": f"Empresa Pro {ruc_input[:4]}", 
                    "Ubicación": "Guayaquil, Ecuador",
                    "Tipo": "Proveedor de Herramientas"
                }
            else:
                st.error("⚠️ El RUC debe tener 13 números.")

    # --- 2. OPCIÓN DE REGISTRO (SOLO SI SE CONSULTÓ) ---
    if st.session_state.datos_encontrados:
        st.info("✅ Datos encontrados en el sistema")
        with st.container(border=True):
            c_a, c_b = st.columns(2)
            with c_a:
                nombre_confirm = st.text_input("Nombre Comercial:", value=st.session_state.datos_encontrados["Nombre"])
                ruc_confirm = st.text_input("RUC Confirmado:", value=st.session_state.ruc_temp, disabled=True)
            with c_b:
                ubicacion_confirm = st.text_input("Ubicación / Dirección:", value=st.session_state.datos_encontrados["Ubicación"])
                tipo_confirm = st.selectbox("Categoría:", ["Proveedor", "Cliente", "Sede Interna"])

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("✅ REGISTRAR AHORA", type="primary", use_container_width=True):
                    # Verificamos si ya existe
                    if ruc_confirm in df_lug['RUC'].astype(str).values:
                        st.warning("⚠️ Esta empresa ya está en tu base de datos.")
                    else:
                        nueva_emp = pd.DataFrame([{
                            "Empresa": nombre_confirm,
                            "RUC": ruc_confirm,
                            "Ubicación": ubicacion_confirm,
                            "Tipo": tipo_confirm
                        }])
                        df_lug = pd.concat([df_lug, nueva_emp], ignore_index=True)
                        guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                        st.success("🎉 Empresa guardada con éxito.")
                        st.session_state.datos_encontrados = None # Limpiamos
                        st.rerun()
            with col_btn2:
                if st.button("❌ DESCARTAR", use_container_width=True):
                    st.session_state.datos_encontrados = None
                    st.rerun()

    st.divider()

    # --- 3. LISTADO ACTUAL ---
    st.subheader("📋 Empresas Registradas")
    if not df_lug.empty:
        # Buscador rápido en la tabla
        busqueda = st.text_input("Filtrar por nombre o RUC:")
        df_mostrar = df_lug.copy()
        
        if busqueda:
            df_mostrar = df_mostrar[
                df_mostrar['Empresa'].str.contains(busqueda, case=False, na=False) |
                df_mostrar['RUC'].str.contains(busqueda, na=False)
            ]

        st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
        
        # Opción de borrado rápido
        with st.expander("🗑️ Eliminar una empresa"):
            emp_a_borrar = st.selectbox("Seleccione empresa para eliminar:", df_lug['Empresa'].tolist())
            if st.button("Confirmar Eliminación", type="primary"):
                df_lug = df_lug[df_lug['Empresa'] != emp_a_borrar].reset_index(drop=True)
                guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                st.rerun()
    else:
        st.write("No hay empresas registradas todavía.")
