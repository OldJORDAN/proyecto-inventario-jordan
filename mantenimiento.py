import streamlit as st
import pandas as pd
from datetime import datetime

def mostrar(df_mant, df_inv, guardar_func, df_mov, df_u, df_lug, df_papelera):
    st.header("🛠️ Bitácora de Mantenimiento")

    # --- 1. REGISTRAR SALIDA A TALLER ---
    with st.expander("➕ Registrar Ingreso a Taller (Salida de Herramienta)"):
        with st.form("form_envio_taller"):
            # Selección de herramienta con buscador
            if not df_inv.empty:
                lista_herramientas = df_inv['ID'].astype(str) + " | " + df_inv['Herramienta'].astype(str)
                h_seleccionada = st.selectbox("Buscar Herramienta:", lista_herramientas)
                id_h = h_seleccionada.split(" | ")[0]
                nom_h = h_seleccionada.split(" | ")[1]
            else:
                st.warning("No hay herramientas en el inventario.")
                st.stop()

            # CAMPO OBLIGATORIO
            falla = st.text_area("Descripción de la falla/mantenimiento (OBLIGATORIO):")
            
            # Buscador de Personal Global (Oficina + Obra)
            if not df_u.empty:
                # Combinamos nombre y rol para que sepas a quién eliges
                df_u['Display'] = df_u['Nombre'] + " (" + df_u['Rol'] + ")"
                lista_personal = df_u['Display'].tolist()
            else:
                lista_personal = ["No hay personal registrado"]
            
            sup_encargado = st.selectbox("Supervisor/Responsable:", options=lista_personal)
            dias_est = st.number_input("Días estimados de entrega:", min_value=1, value=3)

            if st.form_submit_button("Enviar a Mantenimiento"):
                if not falla.strip():
                    st.error("❌ No puedes enviar la herramienta sin describir la falla.")
                else:
                    nueva_entrada = {
                        "ID": id_h,
                        "Herramienta": nom_h,
                        "Tipo de Mantenimiento": falla, # Tu columna del Excel
                        "Fecha de Ingreso": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Días Estimados": dias_est,
                        "Técnico Responsable": sup_encargado,
                        "Estado": "En Proceso"
                    }
                    df_mant = pd.concat([df_mant, pd.DataFrame([nueva_entrada])], ignore_index=True)
                    guardar_func(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                    st.success(f"✅ Herramienta {id_h} registrada en taller.")
                    st.rerun()

    # --- 2. REGISTRAR RE-INGRESO (FINALIZAR) ---
    st.subheader("✅ Finalizar Mantenimiento")
    # Filtramos para que solo salgan las que NO están finalizadas
    herramientas_activas = df_mant[df_mant['Estado'] != 'Finalizado']
    
    if not herramientas_activas.empty:
        with st.expander("📥 Registrar Regreso de Herramienta (Re-ingreso)"):
            with st.form("form_regreso_taller"):
                lista_taller = herramientas_activas['ID'].astype(str) + " | " + herramientas_activas['Herramienta'].astype(str)
                h_regreso = st.selectbox("Seleccionar herramienta que regresa:", lista_taller)
                id_regreso = h_regreso.split(" | ")[0]
                
                # CAMPO OBLIGATORIO
                informe = st.text_area("¿Qué trabajo se realizó finalmente? (OBLIGATORIO):")
                
                if st.form_submit_button("Confirmar Re-ingreso"):
                    if not informe.strip():
                        st.error("❌ Debes describir la reparación antes de finalizar.")
                    else:
                        # Buscamos la fila exacta en el DataFrame original
                        # Usamos el último registro que coincida con ese ID y que no esté finalizado
                        indices = df_mant[(df_mant['ID'] == id_regreso) & (df_mant['Estado'] != 'Finalizado')].index
                        if not indices.empty:
                            idx = indices[-1]
                            
                            # Actualizamos el estado a Finalizado
                            df_mant.at[idx, 'Estado'] = 'Finalizado'
                            
                            # Concatenamos la solución a la descripción original
                            info_previa = str(df_mant.at[idx, 'Tipo de Mantenimiento'])
                            df_mant.at[idx, 'Tipo de Mantenimiento'] = f"{info_previa} | SOLUCIÓN: {informe}"
                            
                            guardar_func(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                            st.success(f"🛠️ Re-ingreso completado. {id_regreso} ahora está disponible.")
                            st.rerun()
                        else:
                            st.error("No se encontró el registro activo.")
    else:
        st.info("No hay herramientas pendientes en mantenimiento.")

    st.divider()

    # --- 3. TABLA DE CONTROL (SOLO PENDIENTES) ---
    st.subheader("📋 Herramientas Actualmente en Taller")
    
    # Aquí es donde hacemos que lo 'Finalizado' desaparezca de la vista principal
    df_pendientes = df_mant[df_mant['Estado'] != 'Finalizado']
    
    if not df_pendientes.empty:
        st.dataframe(df_pendientes, use_container_width=True)
    else:
        st.success("🎉 Todo el equipo está operativo. No hay herramientas en taller.")

    # --- 4. HISTORIAL (PARA CONSULTA) ---
    with st.expander("📜 Ver historial completo (Auditoría)"):
        if not df_mant.empty:
            st.write("Este listado incluye herramientas que ya regresaron (Finalizado).")
            st.dataframe(df_mant, use_container_width=True)
        else:
            st.write("El historial está vacío.")