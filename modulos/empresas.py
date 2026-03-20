import streamlit as st
import pandas as pd

def mostrar(df_lug, guardar_func, df_inv, df_mov, df_u, df_mant, df_papelera):
    st.title("🏢 Gestión de Empresas y Proyectos")
    st.write("Administra los destinos a donde envías tus herramientas.")

    # Creamos dos columnas: una para la lista y otra para el formulario
    col_tabla, col_form = st.columns([1.5, 1])

    with col_tabla:
        st.subheader("📋 Empresas Registradas")
        if not df_lug.empty:
            busqueda = st.text_input("🔍 Buscar empresa por nombre:")
            df_filtrado = df_lug[df_lug['Empresa'].str.contains(busqueda, case=False, na=False)]
            
            st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
            
            # --- FUNCIÓN PARA ELIMINAR ---
            st.divider()
            empresa_a_borrar = st.selectbox("Seleccione una empresa para eliminar:", ["Seleccionar..."] + df_lug['Empresa'].tolist())
            if st.button("🗑️ Eliminar Empresa Seleccionada"):
                if empresa_a_borrar != "Seleccionar...":
                    df_lug = df_lug[df_lug['Empresa'] != empresa_a_borrar]
                    # GUARDAR (Incluyendo df_papelera)
                    guardar_func(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                    st.success(f"Empresa '{empresa_a_borrar}' eliminada.")
                    st.rerun()
        else:
            st.info("Aún no hay empresas registradas.")

    with col_form:
        st.subheader("➕ Nueva Empresa")
        with st.form("form_nueva_empresa", clear_on_submit=True):
            nombre = st.text_input("Nombre de la Empresa o Proyecto:*")
            ubi = st.text_input("Ubicación exacta:")
            resp = st.text_input("Nombre del Responsable en Obra:")
            
            st.write("---")
            enviar = st.form_submit_button("✅ Guardar Empresa")
            
            if enviar:
                if nombre:
                    if nombre in df_lug['Empresa'].values:
                        st.error("Esta empresa ya existe.")
                    else:
                        nueva_fila = {
                            "Empresa": nombre, 
                            "Ubicacion": ubi, 
                            "Responsable": resp
                        }
                        df_lug = pd.concat([df_lug, pd.DataFrame([nueva_fila])], ignore_index=True)
                        
                        # GUARDAR (Incluyendo df_papelera)
                        guardar_func(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                        st.success(f"¡Empresa '{nombre}' guardada con éxito!")
                        st.rerun()
                else:
                    st.warning("El nombre es obligatorio.")

    st.caption("Nota: Las empresas que agregues aparecerán en el selector de Movimientos.")