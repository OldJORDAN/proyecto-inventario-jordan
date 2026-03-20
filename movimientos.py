import streamlit as st
import pandas as pd
from datetime import datetime

def mostrar(df_inv, df_mov, df_lug, user_actual, guardar_func, df_u, df_mant, df_papelera):
    st.header("🔄 Movimientos de Herramientas")

    # Preparar lista de personal (Buscador Global)
    if not df_u.empty:
        df_u['Display'] = df_u['Nombre'] + " (" + df_u['Rol'] + ")"
        lista_personal = df_u['Display'].tolist()
    else:
        lista_personal = ["No hay personal registrado"]

    t_salida, t_devolucion = st.tabs(["📤 Salida de Herramienta", "📥 Devolución"])

    # --- 1. PESTAÑA DE SALIDA ---
    with t_salida:
        with st.form("form_salida"):
            col1, col2 = st.columns(2)
            with col1:
                inv_disponible = df_inv[df_inv['Stock'] > 0]
                lista_h = (inv_disponible['ID'].astype(str) + " | " + inv_disponible['Herramienta']).tolist()
                h_sel = st.selectbox("Seleccionar Herramienta:", lista_h)
                receptor = st.selectbox("Operario Receptor:", lista_personal)
            with col2:
                destino = st.selectbox("Lugar de Destino:", df_lug['Empresa'].tolist() if not df_lug.empty else ["Bodega Central"])
                cant = st.number_input("Cantidad a sacar:", min_value=1, value=1)

            if st.form_submit_button("Registrar Salida"):
                id_h = h_sel.split(" | ")[0]
                fila_inv = df_inv[df_inv['ID'] == id_h].iloc[0]
                
                if fila_inv['Stock'] >= cant:
                    idx_inv = df_inv[df_inv['ID'] == id_h].index[0]
                    df_inv.at[idx_inv, 'Stock'] -= cant
                    
                    nuevo_mov = {
                        "Id_Historial": len(df_mov) + 1,
                        "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Usuario_Admin": user_actual,
                        "ID": id_h,
                        "Herramienta": fila_inv['Herramienta'],
                        "Marca": fila_inv['Marca'],
                        "Operario_Receptor": receptor,
                        "Lugar": destino,
                        "Accion": "Salida",
                        "Cantidad": cant
                    }
                    df_mov = pd.concat([df_mov, pd.DataFrame([nuevo_mov])], ignore_index=True)
                    guardar_func(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                    st.success(f"Salida registrada: {cant} unidad(es).")
                    st.rerun()
                else:
                    st.error("No hay suficiente stock en bodega.")

    # --- 2. PESTAÑA DE DEVOLUCIÓN (LÓGICA CORREGIDA) ---
    with t_devolucion:
        # LÓGICA DE SALDO:
        # 1. Agrupamos todas las SALIDAS por ID
        salidas = df_mov[df_mov['Accion'] == 'Salida'].groupby('ID')['Cantidad'].sum()
        # 2. Agrupamos todas las DEVOLUCIONES por ID
        devoluciones = df_mov[df_mov['Accion'] == 'Devolución'].groupby('ID')['Cantidad'].sum()
        
        # 3. Calculamos qué hay afuera realmente (Salidas - Devoluciones)
        df_saldo = salidas.subtract(devoluciones, fill_value=0)
        herramientas_afuera = df_saldo[df_saldo > 0]

        if not herramientas_afuera.empty:
            with st.form("form_devolucion"):
                # Creamos la lista solo con lo que realmente falta por devolver
                opciones_dev = []
                for id_pend, cant_pend in herramientas_afuera.items():
                    nombre_h = df_inv[df_inv['ID'] == id_pend]['Herramienta'].values[0]
                    marca_h = df_inv[df_inv['ID'] == id_pend]['Marca'].values[0]
                    opciones_dev.append(f"{id_pend} | {nombre_h} ({marca_h}) - Pendientes: {int(cant_pend)}")
                
                h_dev_sel = st.selectbox("Seleccionar herramienta para devolver:", opciones_dev)
                id_dev = h_dev_sel.split(" | ")[0]
                cant_max = herramientas_afuera[id_dev]
                
                emisor = st.selectbox("Quién entrega:", lista_personal)
                cant_dev = st.number_input("Cantidad a devolver:", min_value=1, max_value=int(cant_max), value=int(cant_max))

                if st.form_submit_button("Confirmar Devolución"):
                    # 1. Sumar al Inventario
                    idx_inv = df_inv[df_inv['ID'] == id_dev].index[0]
                    df_inv.at[idx_inv, 'Stock'] += cant_dev
                    
                    # 2. Registrar el movimiento de re-ingreso
                    nom_h_final = df_inv.at[idx_inv, 'Herramienta']
                    mar_h_final = df_inv.at[idx_inv, 'Marca']
                    
                    nuevo_reg = {
                        "Id_Historial": len(df_mov) + 1,
                        "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Usuario_Admin": user_actual,
                        "ID": id_dev,
                        "Herramienta": nom_h_final,
                        "Marca": mar_h_final,
                        "Operario_Receptor": emisor,
                        "Lugar": "Bodega Central",
                        "Accion": "Devolución",
                        "Cantidad": cant_dev
                    }
                    df_mov = pd.concat([df_mov, pd.DataFrame([nuevo_reg])], ignore_index=True)
                    guardar_func(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                    st.success(f"Devolución exitosa: {cant_dev} unidad(es) de {id_dev}.")
                    st.rerun()
        else:
            st.info("✅ Todas las herramientas están en bodega. No hay pendientes de devolución.")

    st.divider()
    # --- 3. HISTORIAL ---
    st.subheader("📋 Historial Reciente")
    if not df_mov.empty:
        vista = df_mov.drop(columns=['Id_Historial']).tail(10)
        st.dataframe(vista, use_container_width=True)