import streamlit as st
import pandas as pd
from datetime import datetime

def mostrar(df_inv, df_mov, df_lug, usuario_actual, guardar_global, df_u, df_mant, df_papelera):
    st.title("🔄 Registro de Movimientos (Entradas y Salidas)")

    # --- 1. LIMPIEZA DE DATOS ---
    if not df_inv.empty:
        # Aseguramos que el Stock sea número para poder comparar
        df_inv['Stock'] = pd.to_numeric(df_inv['Stock'], errors='coerce').fillna(0)

    # --- 2. FORMULARIO DE REGISTRO ---
    with st.form("form_movimientos_estable"):
        st.subheader("📝 Registrar Nueva Acción")
        
        col1, col2 = st.columns(2)
        with col1:
            tipo = st.selectbox("Tipo de Movimiento", ["Salida (Préstamo)", "Entrada (Devolución)"])
            
            # Filtro: Si es salida, solo mostrar lo que tiene Stock
            if tipo == "Salida (Préstamo)":
                df_f = df_inv[df_inv['Stock'] > 0]
            else:
                df_f = df_inv
            
            opciones_h = df_f['Herramienta'].tolist() if not df_f.empty else ["Sin Stock disponible"]
            herramienta = st.selectbox("Seleccione Herramienta", opciones_h)
            cantidad = st.number_input("Cantidad", min_value=1, step=1, value=1)

        with col2:
            # Usamos la primera columna de Lugares por si acaso cambió el nombre
            lista_l = df_lug.iloc[:, 0].tolist() if not df_lug.empty else ["Oficina Central"]
            destino = st.selectbox("Lugar / Obra de Destino", lista_l)
            fecha = st.date_input("Fecha", datetime.now())
            notas = st.text_area("Notas / Observaciones")

        # BOTÓN DE ENVÍO (Indispensable para el formulario)
        btn_reg = st.form_submit_button("🚀 Registrar Movimiento", use_container_width=True)

    # --- 3. PROCESAMIENTO ---
    if btn_reg:
        if herramienta == "Sin Stock disponible":
            st.error("No hay herramientas para procesar este movimiento.")
        else:
            idx_h = df_inv[df_inv['Herramienta'] == herramienta].index[0]
            stock_act = df_inv.at[idx_h, 'Stock']

            if tipo == "Salida (Préstamo)" and cantidad > stock_act:
                st.error(f"❌ Stock insuficiente. Solo hay {int(stock_act)} unidades.")
            else:
                # Actualizar Inventario
                if tipo == "Salida (Préstamo)":
                    df_inv.at[idx_h, 'Stock'] = stock_act - cantidad
                else:
                    df_inv.at[idx_h, 'Stock'] = stock_act + cantidad

                # Crear nuevo registro para el historial
                nuevo_m = pd.DataFrame([{
                    "Fecha": fecha.strftime("%d/%m/%Y"),
                    "Herramienta": herramienta,
                    "Tipo": tipo,
                    "Cantidad": cantidad,
                    "Destino": destino,
                    "Usuario": usuario_actual,
                    "Notas": notas
                }])

                # Unir y Guardar
                df_mov = pd.concat([df_mov, nuevo_m], ignore_index=True)
                guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                
                st.success(f"✅ {tipo} registrada con éxito.")
                st.rerun()

    st.divider()

    # --- 4. VISTA RÁPIDA DE ÚLTIMOS MOVIMIENTOS ---
    if not df_mov.empty:
        st.subheader("🕒 Historial Reciente")
        # Mostramos los últimos 10 movimientos registrados
        st.dataframe(df_mov.tail(10).sort_index(ascending=False), use_container_width=True)
    else:
        st.info("Aún no hay movimientos registrados en esta sesión.")
