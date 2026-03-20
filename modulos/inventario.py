import streamlit as st
import pandas as pd
from datetime import datetime
import re

# --- FUNCIÓN PARA GENERAR EL ID AUTOMÁTICO ---
def generar_nuevo_id(df_inv):
    if df_inv.empty:
        return "H-001"
    ids = df_inv['ID'].astype(str).tolist()
    numeros = []
    for id_val in ids:
        match = re.search(r'\d+', id_val)
        if match:
            numeros.append(int(match.group()))
    nuevo_numero = max(numeros) + 1 if numeros else 1
    return f"H-{nuevo_numero:03d}"

def mostrar(df_inv, guardar_func, df_mov, df_u, df_mant, df_lug, df_papelera):
    st.header("📋 Gestión de Inventario")

    # --- 1. FORMULARIO PARA AGREGAR / ACTUALIZAR STOCK ---
    with st.expander("➕ Agregar Nueva Herramienta al Stock", expanded=True):
        with st.form("nuevo_item"):
            # Creamos una lista de herramientas existentes para el buscador
            lista_existentes = df_inv['Herramienta'].unique().tolist() if not df_inv.empty else []
            
            # Usamos selectbox con opción de escribir (Predictivo)
            nom_n = st.selectbox("Nombre de Herramienta (Escribe para buscar o agregar)", 
                                 options=[""] + lista_existentes)
            
            # Si no existe, permitimos escribir el nombre manualmente en un campo de texto
            if nom_n == "":
                nom_n = st.text_input("O escribe el nombre de la NUEVA herramienta:")

            c1, c2 = st.columns(2)
            mar_n = c1.text_input("Marca")
            stock_n = c2.number_input("Cantidad que ingresa", min_value=1, step=1)
            
            c3, c4 = st.columns(2)
            lug_n = c3.selectbox("Ubicación", df_lug['Empresa'].tolist() if not df_lug.empty else ["Bodega Central"])
            estado_n = c4.selectbox("Estado", ["Operativo", "Nuevo", "En Mantenimiento"])

            if st.form_submit_button("Procesar Ingreso de Mercancía"):
                if nom_n and mar_n:
                    # Buscamos si ya existe la combinación exacta de Nombre y Marca
                    existe = df_inv[(df_inv['Herramienta'].str.upper() == nom_n.upper()) & 
                                    (df_inv['Marca'].str.upper() == mar_n.upper())]
                    
                    if not existe.empty:
                        # --- SI EXISTE: SUMAMOS STOCK ---
                        idx = existe.index[0]
                        df_inv.at[idx, 'Stock'] += int(stock_n)
                        msj_exito = f"✅ Se sumaron {stock_n} unidades a la herramienta existente (ID: {df_inv.at[idx, 'ID']})."
                    else:
                        # --- SI NO EXISTE: CREAMOS NUEVO CON ID AUTO ---
                        nuevo_id = generar_nuevo_id(df_inv)
                        nuevo_reg = {
                            "ID": nuevo_id, 
                            "Herramienta": nom_n, 
                            "Marca": mar_n, 
                            "Stock": int(stock_n), 
                            "Estado": estado_n, 
                            "Lugar": lug_n
                        }
                        df_inv = pd.concat([df_inv, pd.DataFrame([nuevo_reg])], ignore_index=True)
                        msj_exito = f"✨ Herramienta nueva registrada con ID automático: {nuevo_id}"
                    
                    guardar_func(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                    st.success(msj_exito)
                    st.rerun()
                else:
                    st.error("⚠️ El nombre y la marca son necesarios para procesar el ingreso.")

    # --- 2. TABLA PRINCIPAL DE INVENTARIO (No cambia) ---
    st.subheader("Stock Actual")
    busqueda = st.text_input("🔍 Buscar herramienta por nombre o ID:")
    if busqueda:
        df_mostrar = df_inv[df_inv['Herramienta'].str.contains(busqueda, case=False) | df_inv['ID'].str.contains(busqueda, case=False)]
    else:
        df_mostrar = df_inv
    st.dataframe(df_mostrar, use_container_width=True, hide_index=True)

    # --- 3. SECCIÓN DE BAJAS Y CONTROL DE ROBOS (No cambia) ---
    st.divider()
    st.subheader("🗑️ Baja de Herramientas (Robo, Daño o Extravío)")
    col_sel, col_cant = st.columns([2, 1])
    id_borrar = col_sel.selectbox("Seleccione ID para dar de baja:", [""] + df_inv['ID'].tolist())
    
    if id_borrar != "":
        fila_h = df_inv[df_inv['ID'] == id_borrar].iloc[0]
        stock_max = int(fila_h['Stock'])
        cant_baja = col_cant.number_input(f"Cantidad a retirar (Máx: {stock_max})", 
                                          min_value=1, max_value=stock_max, value=1)
        motivo_baja = st.text_area("Motivo detallado de la baja (Obligatorio para auditoría):")

        if st.button("🚨 Ejecutar Baja de Inventario"):
            if not motivo_baja.strip():
                st.error("❌ No puedes procesar la baja sin un motivo.")
            else:
                registro_p = {
                    "Fecha_Eliminacion": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Admin_Que_Borro": st.session_state['nombre'],
                    "ID_Original": id_borrar,
                    "Herramienta": fila_h['Herramienta'],
                    "Marca": fila_h['Marca'],
                    "Cantidad_Eliminada": int(cant_baja),
                    "Motivo": motivo_baja
                }
                idx_original = df_inv[df_inv['ID'] == id_borrar].index[0]
                if cant_baja == stock_max:
                    df_inv = df_inv.drop(idx_original)
                else:
                    df_inv.at[idx_original, 'Stock'] -= cant_baja

                df_papelera = pd.concat([df_papelera, pd.DataFrame([registro_p])], ignore_index=True)
                guardar_func(df_inv, df_mov, df_u, df_mant, df_lug, df_papelera)
                st.warning("⚠️ Acción procesada.")
                st.rerun()
    else:
        st.info("Seleccione una herramienta para habilitar el panel de bajas.")