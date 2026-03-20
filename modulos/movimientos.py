import streamlit as st
import pandas as pd
from datetime import datetime

def mostrar(df_inv, df_mov, df_lug, usuario_actual, guardar_global, df_u, df_mant, df_papelera):
    st.title("🔄 Registro de Movimientos (Entradas y Salidas)")

    # --- 1. LIMPIEZA DE DATOS (PARA EVITAR EL TYPEERROR) ---
    if not df_inv.empty:
        # Forzamos que la columna Stock sea numérica, si hay error pone 0
        df_inv['Stock'] = pd.to_numeric(df_inv['Stock'], errors='coerce').fillna(0)
    
    # --- 2. FORMULARIO DE MOVIMIENTO ---
    with st.form("form_movimiento"):
        st.subheader("📝 Registrar Nueva Acción")
        
        col1, col2 = st.columns(2)
        
        with col1:
            tipo = st.selectbox("Tipo de Movimiento", ["Salida (Préstamo)", "Entrada (Devolución)"])
            # Solo mostramos herramientas que tengan Stock > 0 para salidas
            if tipo == "Salida (Préstamo)":
                df_filtro = df_inv[df_inv['Stock'] > 0]
            else:
                df_filtro = df_inv
                
            herramienta = st.selectbox("Seleccione Herramienta", df_filtro['Herramienta'].tolist() if not df_filtro.empty else ["No hay stock"])
            cantidad = st.number_input("Cantidad", min_value=1, step=1)

        with col2:
            destino = st.selectbox("Lugar / Obra de Destino", df_lug['Nombre'].tolist() if not df_lug.empty else ["Oficina Central"])
            fecha = st.date_input("Fecha", datetime.now())
            notas = st.text_area("Notas / Observaciones", placeholder="Ej: Se entrega en buen estado...")

        # EL BOTÓN QUE FALTABA (Para quitar el aviso de "Missing Submit Button")
        btn_registrar = st.form_submit_button("🚀 Registrar Movimiento", use_container_width=True)

    # --- 3. LÓGICA AL PRESIONAR EL BOTÓN ---
    if btn_registrar:
        if herramienta == "No hay stock":
            st.error("No puedes registrar movimientos sin herramientas disponibles.")
        else:
            # Buscamos la herramienta en el inventario
            idx_inv = df_inv[df_inv['Herramienta'] == herramienta].index[0]
            stock_actual = df_inv.at[idx_inv, 'Stock']

            if tipo == "Salida (Préstamo)" and cantidad > stock_actual:
                st.error(f"❌ No hay suficiente stock. Disponible: {int(stock_actual)}")
            else:
                # Actualizar Stock
                if tipo == "Salida (Préstamo)":
                    df_inv.at[idx_inv, 'Stock'] = stock_actual - cantidad
                else:
                    df_inv.at[idx_inv, 'Stock'] = stock_actual + cantidad

                # Crear el registro del movimiento
                nuevo_mov = pd.DataFrame([{
                    "Fecha": fecha.strftime("%Y-%m-%d"),
                    "Herramienta": herramienta,
                    "Tipo": tipo,
                    "Cantidad": cantidad,
                    "Destino": destino,
                    "Usuario": usuario_actual,
                    "Notas": notas
                }])

                # Concatenar y guardar
                df_mov = pd.concat([df_mov, nuevo_mov], ignore_index=True)
                guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                
                st.success(f"✅ {tipo} registrada correctamente.")
                st.rerun()

    st.divider()

    # --- 4. TABLA DE HISTORIAL RECIENTE ---
    st.subheader("🕒 Últimos Movimientos")
    if not df_mov.empty:
        st.dataframe(df_mov.sort_index(ascending=False).head(10), use_container_width=True)
    else:
        st.info("No hay movimientos registrados recientemente.")
