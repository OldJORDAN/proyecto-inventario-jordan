import streamlit as st
import pandas as pd
from datetime import datetime

def mostrar(df_inv, df_mov, df_lug, usuario_actual, guardar_global, df_u, df_mant, df_papelera):
    st.title("🔄 Registro de Movimientos")

    # --- 1. PREPARACIÓN DE DATOS (PROTECCIÓN CONTRA KEYERROR) ---
    # Limpiamos nombres de columnas de Lugares para evitar el KeyError
    if not df_lug.empty:
        df_lug.columns = df_lug.columns.str.strip() # Quita espacios raros
        # Si no existe 'Nombre', intentamos buscar la primera columna disponible
        col_lugares = 'Nombre' if 'Nombre' in df_lug.columns else df_lug.columns[0]
        lista_lugares = df_lug[col_lugares].tolist()
    else:
        lista_lugares = ["Oficina Central", "Obra General"]

    if not df_inv.empty:
        df_inv['Stock'] = pd.to_numeric(df_inv['Stock'], errors='coerce').fillna(0)

    # --- 2. FORMULARIO DE MOVIMIENTO ---
    with st.form("form_movimiento_nuevo"):
        st.subheader("📝 Registrar Entrada o Salida")
        
        c1, c2 = st.columns(2)
        with c1:
            tipo = st.selectbox("Tipo", ["Salida (Préstamo)", "Entrada (Devolución)"])
            
            # Filtro de herramientas con stock
            if tipo == "Salida (Préstamo)":
                df_f = df_inv[df_inv['Stock'] > 0]
            else:
                df_f = df_inv
                
            opciones_h = df_f['Herramienta'].tolist() if not df_f.empty else ["Sin herramientas"]
            herramienta = st.selectbox("Herramienta", opciones_h)
            cantidad = st.number_input("Cantidad", min_value=1, value=1)

        with c2:
            destino = st.selectbox("Lugar / Obra de Destino", lista_lugares)
            fecha = st.date_input("Fecha", datetime.now())
            notas = st.text_area("Observaciones")

        # EL BOTÓN QUE CIERRA EL FORMULARIO
        btn_registro = st.form_submit_button("🚀 Registrar Acción", use_container_width=True)

    # --- 3. PROCESAR EL REGISTRO ---
    if btn_registro:
        if herramienta == "Sin herramientas":
            st.warning("No hay herramientas para procesar.")
        else:
            try:
                idx_h = df_inv[df_inv['Herramienta'] == herramienta].index[0]
                stock_act = df_inv.at[idx_h, 'Stock']

                if tipo == "Salida (Préstamo)" and cantidad > stock_act:
                    st.error(f"❌ Stock insuficiente. Solo quedan {int(stock_act)}")
                else:
                    # Actualizar Inventario
                    if tipo == "Salida (Préstamo)":
                        df_inv.at[idx_h, 'Stock'] = stock_act - cantidad
                    else:
                        df_inv.at[idx_h, 'Stock'] = stock_act + cantidad

                    # Crear registro de historial
                    nuevo_h = pd.DataFrame([{
                        "Fecha": fecha.strftime("%d/%m/%Y"),
                        "Herramienta": herramienta,
                        "Tipo": tipo,
                        "Cantidad": cantidad,
                        "Destino": destino,
                        "Usuario": usuario_actual,
                        "Notas": notas
                    }])

                    df_mov = pd.concat([df_mov, nuevo_h], ignore_index=True)
                    
                    # GUARDAR TODO
                    guardar_global(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                    st.success("✅ Movimiento guardado con éxito")
                    st.rerun()
            except Exception as e:
                st.error(f"Ocurrió un error inesperado: {e}")

    st.divider()
    # Ver historial
    if not df_mov.empty:
        st.subheader("🕒 Últimos Registros")
        st.dataframe(df_mov.sort_index(ascending=False).head(5), use_container_width=True)
