import streamlit as st
import pandas as pd

def mostrar(df_mov, guardar_func, df_inv, df_u, df_mant, df_lug, df_papelera):
    st.subheader("📜 Auditoría de Sistema")

    tab_movs, tab_safe = st.tabs(["🔄 Movimientos", "🛡️ Papelera de Seguridad"])

    with tab_movs:
        st.write("Registro histórico de salidas y devoluciones:")
        if not df_mov.empty:
            # Ocultamos el Id_Historial para que se vea más limpio
            vista = df_mov.drop(columns=['Id_Historial']) if 'Id_Historial' in df_mov.columns else df_mov
            st.dataframe(vista, use_container_width=True)
        else:
            st.info("No hay movimientos registrados.")

    with tab_safe:
        st.write("🕵️ Registro de elementos eliminados del inventario:")
        if not df_papelera.empty:
            st.error("Atención: Los siguientes registros fueron borrados del inventario principal.")
            st.dataframe(df_papelera, use_container_width=True)
            
            st.divider()
            # Solo el Desarrollador puede limpiar el rastro definitivo
            if st.session_state['rol'] == "Desarrollador":
                if st.button("🚨 Vaciar Papelera (Acción Irreversible)"):
                    df_vacia = pd.DataFrame(columns=df_papelera.columns)
                    guardar_func(df_inv, df_mov, df_u, df_mant, df_lug, df_vacia)
                    st.success("Papelera de seguridad vaciada correctamente.")
                    st.rerun()
        else:
            st.success("La papelera está limpia. No hay registros eliminados.")