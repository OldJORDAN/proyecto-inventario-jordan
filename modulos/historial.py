import streamlit as st
import pandas as pd

def mostrar(df_mov, guardar_global, df_inv, df_u, df_mant, df_lug, df_papelera):
    st.title("📜 Historial de Auditoría")

    if df_mov.empty:
        st.info("No hay movimientos registrados para auditar.")
        return

    # --- 1. EXPORTACIÓN ---
    st.subheader("📥 Respaldos para Auditoría")
    c1, c2 = st.columns(2)
    with c1:
        st.write("Genere el reporte antes de cualquier limpieza:")
        st.button("📄 Descargar PDF de Auditoría", use_container_width=True)

    st.divider()

    # --- 2. VISUALIZACIÓN ---
    st.subheader("🔍 Registro Histórico")
    # Mostramos los movimientos más recientes primero
    st.dataframe(df_mov.sort_index(ascending=False), use_container_width=True)

    st.divider()

    # --- 3. ZONA DE PELIGRO (DESARROLLADOR Y ADMIN) ---
    mi_rol = str(st.session_state.get('rol', '')).lower().strip()
    
    if "desarrollador" in mi_rol or "administrador" in mi_rol:
        st.subheader("⚠️ Mantenimiento de Base de Datos")
        
        with st.expander("🗑️ VACÍAR HISTORIAL COMPLETO"):
            st.error("🚨 ATENCIÓN: Esta acción borrará todos los registros de movimientos.")
            st.write(f"Usuario actual: **{st.session_state['nombre']}** ({st.session_state['rol']})")
            
            # Doble check de seguridad
            c_respaldo = st.checkbox("He descargado y archivado el PDF de respaldo.")
            c_entendido = st.checkbox("Entiendo que esta acción limpiará la pestaña de Movimientos.")
            
            if st.button("🔥 EJECUTAR LIMPIEZA DE AUDITORÍA", type="primary", use_container_width=True):
                if c_respaldo and c_entendido:
                    # Creamos un DataFrame vacío con las mismas columnas
                    df_vacio = pd.DataFrame(columns=df_mov.columns)
                    
                    # Guardamos la base con los movimientos limpios
                    guardar_global(df_inv, df_vacio, df_u, df_mant, df_lug, df_papelera)
                    
                    st.success("✅ Historial vaciado. El sistema está listo para un nuevo ciclo.")
                    st.rerun()
                else:
                    st.warning("Confirme las dos casillas de seguridad para proceder.")
