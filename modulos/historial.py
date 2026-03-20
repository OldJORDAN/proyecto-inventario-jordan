import streamlit as st
import pandas as pd

def mostrar(df_mov, guardar_global, df_inv, df_u, df_mant, df_lug, df_papelera):
    st.title("📜 Historial de Auditoría")

    if df_mov.empty:
        st.info("No hay movimientos registrados en el historial.")
        return

    # --- 1. OPCIONES DE DESCARGA ---
    st.subheader("📥 Exportar Datos")
    col_pdf, col_csv = st.columns(2)
    with col_pdf:
        st.write("Para auditoría física, descargue el reporte completo:")
        # Aquí puedes integrar tu lógica de reportes si ya tienes una
        st.button("📄 Generar PDF de Auditoría")

    st.divider()

    # --- 2. TABLA DE MOVIMIENTOS ---
    st.subheader("🔍 Registro de Movimientos")
    st.dataframe(df_mov, use_container_width=True)

    st.divider()

    # --- 3. ZONA DE PELIGRO (SOLO ADMIN / DESARROLLADOR) ---
    st.subheader("⚠️ Zona de Peligro: Limpieza de Auditoría")
    
    with st.expander("🗑️ Vaciar Historial de Movimientos"):
        st.error("¡CUIDADO! Esta acción eliminará todos los registros de la pestaña 'Movimientos'.")
        st.write("Asegúrese de haber descargado el PDF antes de continuar.")
        
        # Confirmaciones de seguridad
        check1 = st.checkbox("Confirmo que ya descargué el respaldo.")
        check2 = st.checkbox("Entiendo que esta acción no se puede deshacer.")
        
        if st.button("🔥 VACIAR TODO EL HISTORIAL", type="primary", use_container_width=True):
            if check1 and check2:
                # Vaciamos el DataFrame de movimientos pero mantenemos las columnas
                df_vacio = pd.DataFrame(columns=df_mov.columns)
                
                # Guardamos la base de datos con el historial limpio
                guardar_global(df_inv, df_vacio, df_u, df_mant, df_lug, df_papelera)
                
                st.success("✅ Historial vaciado correctamente. La casa está limpia.")
                st.rerun()
            else:
                st.warning("Debe marcar ambas casillas de confirmación para proceder.")
