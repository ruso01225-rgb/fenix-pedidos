import streamlit as st
import requests
import pandas as pd
import os

# ---------------------------------------------------------
# 1. CONFIGURACIÓN
# ---------------------------------------------------------
st.set_page_config(page_title="Fenix Pedidos", page_icon="🔥", layout="centered")

# =========================================================
# 🔐 SISTEMA DE LOGIN DE SEGURIDAD
# =========================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # Diseño centrado para el login
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center;'>🔒 Acceso Restringido</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Sistema Fenix Pedidos</p>", unsafe_allow_html=True)
    
    col_log1, col_log2, col_log3 = st.columns([1, 2, 1])
    with col_log2:
        codigo_ingreso = st.text_input("Ingrese Código:", type="password", placeholder="****", label_visibility="collapsed")
        
        if st.button("INGRESAR", type="primary", use_container_width=True):
            if codigo_ingreso == "1408":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("❌ Código incorrecto")
    
    # Detener la ejecución del resto de la app si no está logueado
    st.stop()

# =========================================================
# 🟢 INICIO DE LA APLICACIÓN (SOLO SI LOGUEADO)
# =========================================================

# ⚠️ TU URL DE GOOGLE APPS SCRIPT
URL_SHEETS = "https://script.google.com/macros/s/AKfycbzEa9UwrBhOVaA1QR6ui5VRUTz1oGSzV-WZ7MIN5YbdJUsBrZRUv9l80Jl1kqAbheNDlw/exec"

# ARCHIVOS LOCALES
ARCHIVO_DB = "productos_db.csv"
ARCHIVO_CONSECUTIVO = "consecutivo.txt"

# 🔒 CONTRASEÑA DE ADMINISTRADOR (Para editar productos)
PASSWORD_ADMIN = "1234"  

# ---------------------------------------------------------
# 2. LISTA MAESTRA INICIAL (FORMATO: [PRECIO, STOCK])
# ---------------------------------------------------------
PRODUCTOS_INICIALES_DICT = {
    # --- Aguardientes ---
    "Aguardiente Garrafa tapa roja": [98000, 20],
    "Aguardiente Botella tapa roja": [58000, 20],
    "Aguardiente Tapa roja media": [34000, 20],
    "Aguardiente Garrafa tapa special": [102000, 20],
    "Aguardiente Botella tapa special": [60000, 20],
    "Aguardiente Tapa special media": [36000, 20],
    "Aguardiente Amarillo": [67000, 20],
    "Aguardiente Tapa Rosado": [78000, 20],
    "Aguardiente Botella Nectar verde": [50000, 20],
    "Aguardiente Nectar verde media": [33000, 20],

    # --- Rones ---
    "Ron Mojito": [55000, 20],
    "Ron Bacardi Limon": [55000, 20],
    "Ron Botella Viejo de Caldas": [65000, 20],
    "Ron Viejo de Caldas media": [35000, 20],

    # --- Cervezas ---
    "Cerveza Six Heineken": [21000, 20],
    "Cerveza Six Corona 355": [30000, 20],
    "Cerveza Six Costeña": [17000, 20],
    "Cerveza Six Costeñita": [17000, 20],
    "Cerveza Six 330 Aguila": [23000, 20],
    "Cerveza Six Poker": [23000, 20],
    "Cerveza Sixpack Andina": [16000, 20],
    "Cerveza Six Light Aguila": [23000, 20],
    "Cerveza Sixpack Club Colombia": [24000, 20],
    "Cerveza Six Budweiser": [17000, 20],

    # --- Otros Licores / Bebidas ---
    "Four Loco Sandia": [15000, 20],
    "Four Loco Purple": [15000, 20],
    "Four Loco Blue": [15000, 20],
    "Four Loco Gold": [15000, 20],

    # --- Cigarrillos ---
    "Cigarrillo Mustang": [8000, 20],
    "Cigarrillo Marlboro Rojo": [9000, 20],
    "Cigarrillo Boston": [8000, 20],
    "Cigarrillo Marlboro Sandia": [9000, 20],
    "Cigarrillo Marlboro Fusion": [9000, 20],
    "Cigarrillo Lucky Verde": [9000, 20],
    "Cigarrillo Lucky Alaska": [9000, 20],
    "Cigarrillo Green": [8000, 20],

    # --- Whiskys ---
    "Whisky Jack Daniels": [147000, 20],
    "Whisky Jack Daniels Honey": [147000, 20],
    "Whisky Chivas": [155000, 20],
    "Whisky Buchannas Botella": [183000, 20],
    "Whisky Buchannas Media": [104000, 20],
    "Whisky Grans": [73000, 20],
    "Whisky Old Parr Botella": [164000, 20],
    "Whisky Old Parr Media": [116000, 20],
    "Whisky Haig Club": [116000, 20],
    "Whisky Black White Botella": [60000, 20],
    "Whisky Black White Media": [33000, 20],
    "Whisky Something Botella": [76000, 20],
    "Whisky Sello Rojo Litro": [104000, 20],
    "Whisky Sello Rojo Botella": [80000, 20],
    "Whisky Sello Rojo Media": [51000, 20],

    # --- Cremas ---
    "Crema de Whisky Black Jack": [58000, 20],
    "Crema de Whisky Baileys Litro": [116000, 20],
    "Crema de Whisky Baileys Botella": [85000, 20],
    "Crema de Whisky Baileys Media": [53000, 20],

    # --- Tequilas / Ginebra / Vodka ---
    "Tequila Jose Cuervo Botella": [96000, 20],
    "Tequila Jose Cuervo Media": [60000, 20],
    "Tequila Jimador Botella": [125000, 20],
    "Tequila Jimador Media": [76000, 20],
    "Ginebra Tanqueray": [135000, 20],
    "Ginebra Bombay": [120000, 20],
    "Vodka Absolut Litro": [120000, 20],
    "Vodka Absolut Botella": [92000, 20],
    "Vodka Absolut Media": [58000, 20],
    "Smirnoff Ice Lata": [9500, 20],
    "Smirnoff Manzana Lata": [9500, 20],
    "Smirnoff Lulo Botella": [52000, 20],
    "Smirnoff Lulo Media": [29000, 20],
    "Jagermaister Hiervas": [130000, 20],

    # --- Vinos ---
    "Vino Gato Tinto Tetrapack": [27000, 20],
    "Vino Gato Negro Merlot": [47000, 20],
    "Vino Gato Negro Sauvignon": [47000, 20],
    "Vino Gato Negro Malbec": [47000, 20],
    "Vino Casillero del Diablo": [75000, 20],
    "Vino Finca Las Moras Sauvignon": [58000, 20],
    "Vino Finca Las Moras Malbec": [58000, 20],
    "Vino Duvoned": [73000, 20],
    "Vino Espumoso JP Chanet Blanco": [70000, 20],
    "Vino Espumoso JP Chanet Rosado": [70000, 20],
    "Vino Espumoso JP Chanet Morado": [70000, 20],
    "Vino Espumoso JP Chanet Syrah": [65000, 20],
    "Vino Espumoso JP Chanet Brut": [65000, 20],
    "Vino Espumoso JP Chanet Chardonnay": [65000, 20],

    # --- Bebidas sin Alcohol / Energizantes ---
    "Gatorade": [5000, 20],
    "Agua con Gas": [2500, 20],
    "Agua sin Gas": [2000, 20],
    "Redbull": [7000, 20],
    "Coca Cola 1.5L": [7500, 20],
    "Gaseosa Ginger 1.5L": [7500, 20],
    "Gaseosa Soda Bretaña 1.5L": [7500, 20],
    "Jugo Naranja Del Valle": [7000, 20],
    "Electrolit Naran/Mandarina": [9500, 20],
    "Electrolit Maracuya": [9500, 20],

    # --- Snacks / Varios ---
    "Detodito Natural 165gr": [8500, 20],
    "Detodito BBQ 165gr": [8500, 20],
    "Detodito Mix 165gr": [8500, 20],
    "Chicles Trident": [2000, 20],
    "Encendedor": [1000, 20],
    "Bonfiest": [4000, 20],
    "Preservativos": [3000, 20],
    "Sildenafil Viagra": [7000, 20],
    "Salchichas": [7000, 20],
    "Bombombunes": [600, 20],
    "Hielo": [2000, 20]
}

# ---------------------------------------------------------
# 3. GESTIÓN DE BASE DE DATOS Y CONSECUTIVO
# ---------------------------------------------------------

# --- PRODUCTOS ---
def cargar_productos():
    """Carga CSV o crea usando el diccionario maestro."""
    if not os.path.exists(ARCHIVO_DB):
        data_list = []
        for prod, valores in PRODUCTOS_INICIALES_DICT.items():
            data_list.append({
                "Producto": prod, 
                "Precio": valores[0], 
                "Stock": valores[1]
            })
        df = pd.DataFrame(data_list)
        df.to_csv(ARCHIVO_DB, index=False)
        return df
    else:
        try:
            return pd.read_csv(ARCHIVO_DB)
        except:
            data_list = []
            for prod, valores in PRODUCTOS_INICIALES_DICT.items():
                data_list.append({
                    "Producto": prod, 
                    "Precio": valores[0], 
                    "Stock": valores[1]
                })
            df = pd.DataFrame(data_list)
            df.to_csv(ARCHIVO_DB, index=False)
            return df

def guardar_productos(df):
    df.to_csv(ARCHIVO_DB, index=False)

# --- CONSECUTIVO FACTURA ---
def obtener_siguiente_factura():
    """Lee el número actual del archivo o inicia en 3001."""
    if not os.path.exists(ARCHIVO_CONSECUTIVO):
        return 3001
    try:
        with open(ARCHIVO_CONSECUTIVO, "r") as f:
            return int(f.read().strip())
    except:
        return 3001

def actualizar_factura_siguiente(nuevo_numero):
    """Guarda el nuevo número para la PRÓXIMA factura."""
    with open(ARCHIVO_CONSECUTIVO, "w") as f:
        f.write(str(nuevo_numero))

# Inicialización
df_productos = cargar_productos()
PRODUCTOS_DISPONIBLES = dict(zip(df_productos["Producto"], df_productos["Precio"]))
STOCK_DISPONIBLE = dict(zip(df_productos["Producto"], df_productos["Stock"]))

# ---------------------------------------------------------
# 4. PANEL DE ADMINISTRACIÓN (SIDEBAR)
# ---------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Configuración")
    
    activar_admin = st.checkbox("Administrar Productos")
    
    if activar_admin:
        password = st.text_input("Contraseña de Admin", type="password")
        
        if password == PASSWORD_ADMIN:
            st.success("Modo Administrador Activo")
            
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["📦 Stock", "➕ Crear", "✏️ Editar", "🗑️ Borrar", "📂 Masivo"])
            
            with tab1:
                st.subheader("Gestión de Stock")
                st.info("Edita el stock directamente en la tabla:")
                df_stock_edit = st.data_editor(
                    df_productos[["Producto", "Stock"]],
                    column_config={
                        "Producto": st.column_config.TextColumn(disabled=True),
                        "Stock": st.column_config.NumberColumn("Unidades", min_value=0, step=1)
                    },
                    hide_index=True,
                    key="editor_stock_admin"
                )
                if st.button("💾 Guardar Stock"):
                    for index, row in df_stock_edit.iterrows():
                        nombre_prod = row["Producto"]
                        nuevo_stock = row["Stock"]
                        df_productos.loc[df_productos["Producto"] == nombre_prod, "Stock"] = nuevo_stock
                    guardar_productos(df_productos)
                    st.success("Stock actualizado correctamente")
                    st.rerun()

            with tab2:
                st.subheader("Nuevo Producto")
                new_name = st.text_input("Nombre", key="new_name")
                col_n1, col_n2 = st.columns(2)
                with col_n1:
                    new_price = st.number_input("Precio", min_value=0, step=500, key="new_price")
                with col_n2:
                    new_stock = st.number_input("Stock Inicial", min_value=0, step=1, key="new_stock_init")
                
                if st.button("Guardar Nuevo"):
                    if new_name:
                        if new_name in df_productos["Producto"].values:
                            st.error("¡Ese producto ya existe!")
                        else:
                            nuevo_row = pd.DataFrame([{"Producto": new_name, "Precio": new_price, "Stock": new_stock}])
                            df_productos = pd.concat([df_productos, nuevo_row], ignore_index=True)
                            guardar_productos(df_productos)
                            st.success(f"Creado: {new_name}")
                            st.rerun()
                    else:
                        st.warning("Escribe un nombre.")

            with tab3:
                st.subheader("Editar Datos")
                lista_prods = sorted(list(df_productos["Producto"]))
                prod_a_editar = st.selectbox("Producto a editar", ["Seleccionar..."] + lista_prods)
                if prod_a_editar != "Seleccionar...":
                    row_actual = df_productos[df_productos["Producto"] == prod_a_editar].iloc[0]
                    precio_actual = int(row_actual["Precio"])
                    stock_actual = int(row_actual.get("Stock", 0))
                    
                    st.write("Modificar valores:")
                    edit_name = st.text_input("Nombre", value=prod_a_editar)
                    c_e1, c_e2 = st.columns(2)
                    with c_e1:
                        edit_price = st.number_input("Precio", value=precio_actual, step=500)
                    with c_e2:
                        edit_stock = st.number_input("Stock", value=stock_actual, step=1)
                    
                    if st.button("Actualizar Producto"):
                        idx = df_productos.index[df_productos["Producto"] == prod_a_editar][0]
                        df_productos.at[idx, "Producto"] = edit_name
                        df_productos.at[idx, "Precio"] = edit_price
                        df_productos.at[idx, "Stock"] = edit_stock
                        guardar_productos(df_productos)
                        st.success("¡Producto Actualizado!")
                        st.rerun()

            with tab4:
                st.subheader("Eliminar Producto")
                prod_a_borrar = st.selectbox("Selecciona para borrar", ["Seleccionar..."] + sorted(list(df_productos["Producto"])), key="del_select")
                if st.button("🗑️ Eliminar Definitivamente", type="primary"):
                    if prod_a_borrar != "Seleccionar...":
                        df_productos = df_productos[df_productos["Producto"] != prod_a_borrar]
                        guardar_productos(df_productos)
                        st.warning(f"Eliminado: {prod_a_borrar}")
                        st.rerun()

            with tab5:
                st.subheader("📂 Edición Masiva")
                st.markdown("1. **Descarga** tu inventario actual.\n2. Edítalo en Excel.\n3. **Sube** el archivo actualizado.")
                with open(ARCHIVO_DB, "rb") as f:
                    st.download_button(
                        label="⬇️ Descargar Inventario (CSV)",
                        data=f,
                        file_name="inventario_fenix.csv",
                        mime="text/csv"
                    )
                st.divider()
                uploaded_file = st.file_uploader("⬆️ Subir CSV Actualizado", type=["csv"])
                if uploaded_file is not None:
                    try:
                        df_nuevo = pd.read_csv(uploaded_file)
                        required_cols = ["Producto", "Precio", "Stock"]
                        if all(col in df_nuevo.columns for col in required_cols):
                            if st.button("✅ Confirmar y Reemplazar Inventario"):
                                guardar_productos(df_nuevo)
                                st.success("¡Base de datos actualizada!")
                                st.rerun()
                        else:
                            st.error(f"El archivo debe tener las columnas: {required_cols}")
                    except Exception as e:
                        st.error(f"Error al leer el archivo: {e}")

        elif password:
            st.error("Contraseña incorrecta")

# ---------------------------------------------------------
# 5. FUNCIONES DE ENVÍO Y INTERFAZ CLIENTE
# ---------------------------------------------------------
def enviar_a_sheets(data):
    try:
        headers = {"Content-Type": "application/json"}
        resp = requests.post(URL_SHEETS, json=data, headers=headers, timeout=20)
        return resp
    except Exception as e:
        return f"Error de conexión: {e}"

st.title("🔥 Fenix Pedidos")

# --- OBTENER NÚMERO DE FACTURA ---
numero_factura_actual = obtener_siguiente_factura()

with st.expander("👤 Datos del Cliente", expanded=False):
    col_a, col_b = st.columns(2)
    with col_a:
        # CAMPO FACTURA AUTOMÁTICO Y BLOQUEADO
        factura = st.text_input("Factura # (Automático)", value=str(numero_factura_actual), disabled=True)
    with col_b:
        celular = st.text_input("Celular")
    
    domiciliario = st.selectbox("Domiciliario", ["Sin Domicilio", "Juan", "Pedro", "Empresa"])
    col_c, col_d = st.columns(2)
    with col_c:
        barrio = st.text_input("Barrio")
    with col_d:
        direccion = st.text_input("Dirección")
    ubicacion = st.text_input("Ubicación")
    observaciones = st.text_area("Observaciones", height=68)

st.divider()

# ---------------------------------------------------------
# 6. CARRITO Y LÓGICA DE VENTA
# ---------------------------------------------------------
st.subheader("🛒 Realizar Pedido")

if "carrito" not in st.session_state:
    st.session_state.carrito = pd.DataFrame(columns=["Producto","Precio","Cantidad","Total"])
    st.session_state.carrito = st.session_state.carrito.astype({"Producto":"str","Precio":"int","Cantidad":"int","Total":"int"})

# --- BUSCADOR ---
col1, col2, col3 = st.columns([3,1,1])
with col1:
    lista_ordenada = sorted(list(PRODUCTOS_DISPONIBLES.keys()))
    opc = ["Seleccionar..."] + lista_ordenada
    
    # --- FUNCIÓN NUEVA: Formatear lista desplegable ---
    def formato_opcion(opcion):
        if opcion == "Seleccionar...":
            return opcion
        try:
            p = float(PRODUCTOS_DISPONIBLES.get(opcion, 0))
            return f"{opcion} (${p:,.0f})"
        except:
            return opcion

    prod_sel = st.selectbox("Producto", opc, format_func=formato_opcion, label_visibility="collapsed")

with col2:
    cant_sel = st.number_input("Cant.", min_value=1, value=1, label_visibility="collapsed")
with col3:
    add_btn = st.button("➕", type="primary", use_container_width=True)

# --- INFO VISUAL DE PRECIO SELECCIONADO ---
if prod_sel != "Seleccionar...":
    st.info(f"💰 Precio Unitario: **${PRODUCTOS_DISPONIBLES.get(prod_sel, 0):,.0f}**")

if add_btn and prod_sel != "Seleccionar...":
    precio = int(PRODUCTOS_DISPONIBLES[prod_sel])
    cant = int(cant_sel)
    df = st.session_state.carrito.copy()

    if prod_sel in df["Producto"].values:
        idx = df.index[df["Producto"] == prod_sel][0]
        df.loc[idx, "Cantidad"] = int(df.loc[idx, "Cantidad"]) + cant
        df.loc[idx, "Precio"] = precio 
        df.loc[idx, "Total"] = df.loc[idx, "Precio"] * df.loc[idx, "Cantidad"]
    else:
        nuevo = pd.DataFrame([{
            "Producto": prod_sel,
            "Precio": precio,
            "Cantidad": cant,
            "Total": precio * cant
        }])
        df = pd.concat([df, nuevo], ignore_index=True)
    
    st.session_state.carrito = df
    st.rerun()

# ---------------------------------------------------------
# 7. TABLA DE CARRITO Y TOTALES
# ---------------------------------------------------------
st.write("Resumen:")

edited_df = st.data_editor(
    st.session_state.carrito,
    num_rows="dynamic",
    column_config={
        "Producto": st.column_config.TextColumn("Producto", required=True),
        "Precio": st.column_config.NumberColumn("Precio", min_value=0, format="$%d"),
        "Cantidad": st.column_config.NumberColumn("Cantidad", min_value=1),
        "Total": st.column_config.NumberColumn("Total", disabled=True, format="$%d"),
    },
    key="editor_carrito"
)

# Limpieza
clean_df = edited_df.copy()
clean_df["Producto"] = clean_df["Producto"].astype(str)
clean_df = clean_df[clean_df["Producto"].str.strip() != ""]
clean_df = clean_df[clean_df["Producto"].str.lower() != "nan"]

for col in ["Precio", "Cantidad"]:
    clean_df[col] = clean_df[col].astype(str).str.replace("$", "", regex=False).str.replace(",", "", regex=False)
    clean_df[col] = pd.to_numeric(clean_df[col], errors='coerce').fillna(0).astype(int)

clean_df["Total"] = clean_df["Precio"] * clean_df["Cantidad"]
st.session_state.carrito = clean_df

# Totales
st.divider()
suma_productos = int(clean_df["Total"].sum())
st.subheader("💰 Totales")

valor_domicilio = st.number_input("Valor Domicilio", min_value=0, step=1000, value=7000, key="val_domi_input")
medio_pago = st.selectbox("Medio de Pago", ["Efectivo", "Nequi", "DaviPlata", "Datafono"], key="medio_pago_input")

total_final = suma_productos + int(valor_domicilio)

st.markdown(f"""
<div style="text-align:center; font-size:32px; font-weight:700; padding:12px; margin-top:10px; border-radius:10px; background:#e8fff1; color:#004d29;">
TOTAL: ${total_final:,.0f}
</div>
""", unsafe_allow_html=True)

total_datafono = ""
if medio_pago == "Datafono":
    valor_dat_calculado = int(total_final * 1.06)
    st.markdown("""<div style="font-size:16px; font-weight:900; color:#8B0000; background:#FFE4E4; border:2px solid #E57373; padding:12px 5px; border-radius:10px; text-align:center; margin-top:18px; margin-bottom:10px;">💳 Pago con Datafono (6% adicional)</div>""", unsafe_allow_html=True)
    total_datafono = st.number_input("Valor Datafono", value=valor_dat_calculado, step=500, key="datafono_valor")
    st.markdown(f"""<div style="font-size:24px; color:#333; text-align:center; margin-top:6px;">Cálculo automático:<br><b>${total_final:,.0f}</b> × <b>6%</b> = <b style="color:#C62828;">${valor_dat_calculado:,.0f}</b></div>""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 8. BOTÓN DE ENVÍO FINAL
# ---------------------------------------------------------
if st.button("🚀 ENVIAR PEDIDO", type="primary", use_container_width=True):
    productos_envio = []
    
    for _, row in clean_df.iterrows():
        productos_envio.append({
            "Producto": str(row["Producto"]),
            "Precio": str(row["Precio"]),
            "Cantidad": str(row["Cantidad"]),
            "Total": str(row["Total"])
        })
    
    if not productos_envio:
        st.error("⚠️ Carrito vacío")
    else:
        # Aquí usamos la variable 'factura' (que es el número automático)
        data_json = {
            "MedioPago":      medio_pago,
            "ValorTotalV":    str(total_final),
            "ValorDomi":      str(valor_domicilio),
            "TotalData":      total_datafono,
            "Factura":        factura, 
            "Domiciliario":   domiciliario,
            "Celular":        celular,
            "Barrio":         barrio,
            "Direccion":      direccion,
            "Ubicacion":      ubicacion,
            "Observaciones":  observaciones,
            "Productos":      productos_envio
        }
        
        with st.spinner("Enviando..."):
            res = enviar_a_sheets(data_json)
        
        if hasattr(res, 'status_code') and res.status_code == 200:
            st.balloons()
            st.success(f"✅ Pedido #{factura} enviado correctamente")
            
            # 1. ACTUALIZAR STOCK
            for item in productos_envio:
                prod_name = item["Producto"]
                qty = int(item["Cantidad"])
                if prod_name in df_productos["Producto"].values:
                    idx = df_productos.index[df_productos["Producto"] == prod_name][0]
                    current = int(df_productos.at[idx, "Stock"])
                    df_productos.at[idx, "Stock"] = max(0, current - qty)
            guardar_productos(df_productos)
            
            # 2. ACTUALIZAR CONSECUTIVO (+1)
            actualizar_factura_siguiente(numero_factura_actual + 1)
            
            # Limpiar carrito
            st.session_state.carrito = pd.DataFrame(columns=["Producto","Precio","Cantidad","Total"])
            st.rerun()
        else:
            st.error("❌ Error al enviar")
            st.write(res)


