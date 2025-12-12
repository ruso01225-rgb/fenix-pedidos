import streamlit as st
import requests
import pandas as pd
import os
import time  # <--- Necesario para la pausa de las bombitas
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from streamlit_js_eval import get_geolocation

# ---------------------------------------------------------
# 1. CONFIGURACIÓN
# ---------------------------------------------------------
st.set_page_config(page_title="Ibaguiar Venta de Licor", page_icon="🔥", layout="centered")

# =========================================================
# ⚙️ VARIABLES
# =========================================================
UBICACION_BASE = (4.4440508, -75.208976)
URL_SHEETS = "https://script.google.com/macros/s/AKfycbzEa9UwrBhOVaA1QR6ui5VRUTz1oGSzV-WZ7MIN5YbdJUsBrZRUv9l80Jl1kqAbheNDlw/exec"
ARCHIVO_DB = "productos_db.csv"
ARCHIVO_CONSECUTIVO = "consecutivo.txt"
PASSWORD_ADMIN = "1234"

# ---------------------------------------------------------
# 2. LISTA MAESTRA DE PRECIOS
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
    "Cerveza Six Heineken": [22000, 20],
    "Cerveza Six Corona 355": [30000, 20],
    "Cerveza Six Costeña": [17000, 20],
    "Cerveza Six Costeñita": [18000, 20],
    "Cerveza Six 330 Aguila": [23000, 20],
    "Cerveza Six Poker": [23000, 20],
    "Cerveza Sixpack Andina": [16000, 20],
    "Cerveza Six Light Aguila": [24000, 20],
    "Cerveza Sixpack Club Colombia": [25000, 20],
    "Cerveza Six Budweiser": [18000, 20],
    # --- Otros Licores / Bebidas ---
    "Four Loco Sandia": [15000, 20],
    "Four Loco Purple": [15000, 20],
    "Four Loco Blue": [15000, 20],
    "Four Loco Gold": [15000, 20],
    # --- Cigarrillos ---
    "Cigarrillo Mustang": [8500, 20],
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
    "Tequila Jimador Botella": [130000, 20],
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
    "Detodito Natural 165gr": [9500, 20],
    "Detodito BBQ 165gr": [9500, 20],
    "Detodito Mix 165gr": [9500, 20],
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
# 3. FUNCIONES
# ---------------------------------------------------------
def cargar_productos():
    if not os.path.exists(ARCHIVO_DB):
        data_list = [{"Producto": p, "Precio": v[0], "Stock": v[1]} for p, v in PRODUCTOS_INICIALES_DICT.items()]
        df = pd.DataFrame(data_list)
        df.to_csv(ARCHIVO_DB, index=False)
        return df
    else:
        try:
            return pd.read_csv(ARCHIVO_DB)
        except:
            return pd.DataFrame(columns=["Producto","Precio","Stock"])

def guardar_productos(df):
    df.to_csv(ARCHIVO_DB, index=False)

def obtener_siguiente_factura():
    if not os.path.exists(ARCHIVO_CONSECUTIVO): return 3001
    try:
        with open(ARCHIVO_CONSECUTIVO, "r") as f: return int(f.read().strip())
    except: return 3001

def actualizar_factura_siguiente(nuevo_numero):
    with open(ARCHIVO_CONSECUTIVO, "w") as f: f.write(str(nuevo_numero))

def calcular_tarifa_domicilio(direccion_texto=None, coordenadas_gps=None):
    geolocator = Nominatim(user_agent="fenix_app_v4")
    coords_destino = None
    direccion_detectada = direccion_texto

    try:
        if coordenadas_gps:
            coords_destino = coordenadas_gps
            try:
                location = geolocator.reverse(f"{coords_destino[0]}, {coords_destino[1]}", timeout=5)
                if location:
                    direccion_detectada = location.address.split(",")[0]
            except:
                direccion_detectada = "Ubicación GPS"

        elif direccion_texto and len(direccion_texto) > 3:
            busqueda = f"{direccion_texto}, Ibagué, Tolima, Colombia"
            location = geolocator.geocode(busqueda, timeout=5)
            if location:
                coords_destino = (location.latitude, location.longitude)
        
        if coords_destino:
            distancia_km = geodesic(UBICACION_BASE, coords_destino).kilometers
            # Tarifa: 4000 base + 1500 x km
            tarifa = 4000 + (distancia_km * 1500)
            tarifa = round(tarifa / 100) * 100
            if tarifa < 5000: tarifa = 5000
            return int(tarifa), round(distancia_km, 2), direccion_detectada
        else:
            return None, 0, direccion_texto
    except:
        return None, 0, direccion_texto

def enviar_a_sheets(data):
    try:
        headers = {"Content-Type": "application/json"}
        resp = requests.post(URL_SHEETS, json=data, headers=headers, timeout=15)
        return resp
    except Exception as e: return f"Error: {e}"

# INICIALIZACIÓN
df_productos = cargar_productos()
PRODUCTOS_DISPONIBLES = dict(zip(df_productos["Producto"], df_productos["Precio"]))

# ---------------------------------------------------------
# 4. INTERFAZ
# ---------------------------------------------------------

# --- SIDEBAR DE ADMIN ---
with st.sidebar:
    st.header("⚙️ Admin")
    if st.checkbox("Opciones Avanzadas"):
        pwd = st.text_input("Contraseña", type="password")
        if pwd == PASSWORD_ADMIN:
            st.success("Admin Autorizado")
            if st.button("🔄 Restaurar Precios de Fábrica"):
                data_list = [{"Producto": p, "Precio": v[0], "Stock": v[1]} for p, v in PRODUCTOS_INICIALES_DICT.items()]
                df_new = pd.DataFrame(data_list)
                guardar_productos(df_new)
                st.success("¡Precios Actualizados! Recargando...")
                time.sleep(1)
                st.rerun()

st.title("🔥 Venta de Licores Ibague")
numero_factura_actual = obtener_siguiente_factura()

# Estados de sesión
if 'direccion_final' not in st.session_state: st.session_state['direccion_final'] = ""
if 'link_ubicacion' not in st.session_state: st.session_state['link_ubicacion'] = ""
if 'valor_domi_calculado' not in st.session_state: st.session_state['valor_domi_calculado'] = 7000
if 'gps_temporal' not in st.session_state: st.session_state['gps_temporal'] = None

# --- DATOS CLIENTE (FORMULARIO) ---
with st.expander("👤 Datos del Cliente", expanded=True):
    c_f, c_t = st.columns(2)
    with c_f: st.text_input("Factura #", value=str(numero_factura_actual), disabled=True)
    
    # IMPORTANTE: Usamos key para poder borrarlos luego
    with c_t: celular = st.text_input("Celular", key="input_celular") 
    
    st.markdown("---")
    st.write("📍 **Ubicación GPS:**")
    
    col_detect, col_status = st.columns([1, 2])
    with col_detect:
        gps_data = get_geolocation(component_key='get_gps')
    
    with col_status:
        if gps_data:
            lat = gps_data['coords']['latitude']
            lon = gps_data['coords']['longitude']
            st.session_state['gps_temporal'] = (lat, lon)
            st.success(f"✅ Señal: {lat:.4f}, {lon:.4f}")
        else:
            st.info("Presiona 'Find my location' 📡")

    if st.session_state['gps_temporal']:
        if st.button("⬇️ USAR ESTA UBICACIÓN", use_container_width=True, type="primary"):
            coords = st.session_state['gps_temporal']
            link_maps = f"http://googleusercontent.com/maps.google.com/?q={coords[0]},{coords[1]}"
            st.session_state['link_ubicacion'] = link_maps
            
            with st.spinner("Calculando..."):
                t, d, dir_txt = calcular_tarifa_domicilio(coordenadas_gps=coords)
                if t:
                    st.session_state['valor_domi_calculado'] = t
                    st.session_state['direccion_final'] = dir_txt
                    st.toast("Datos actualizados", icon="📝")
                st.session_state['gps_temporal'] = None
                st.rerun()

    col_in_dir, col_in_link = st.columns(2)
    with col_in_dir:
        dir_val = st.text_input("Dirección (Calle)", value=st.session_state['direccion_final'])
        if dir_val != st.session_state['direccion_final']: st.session_state['direccion_final'] = dir_val

    with col_in_link:
        link_val = st.text_input("Link Maps", value=st.session_state['link_ubicacion'])
        if link_val != st.session_state['link_ubicacion']: st.session_state['link_ubicacion'] = link_val

    st.markdown("---")
    domiciliario = st.selectbox("Domiciliario", ["Sin Domicilio", "Juan", "Pedro", "Empresa"])
    
    # IMPORTANTE: Usamos key para poder borrarlos luego
    barrio = st.text_input("Barrio", key="input_barrio")
    observaciones = st.text_area("Notas", key="input_notas")

st.divider()

# ---------------------------------------------------------
# 5. CARRITO
# ---------------------------------------------------------
st.subheader("🛒 Carrito")

if "carrito" not in st.session_state:
    st.session_state.carrito = pd.DataFrame(columns=["Producto","Precio","Cantidad","Total"])
    st.session_state.carrito = st.session_state.carrito.astype({"Producto":"str","Precio":"int","Cantidad":"int","Total":"int"})

lista_ordenada = sorted(list(PRODUCTOS_DISPONIBLES.keys()))
opc = ["Seleccionar..."] + lista_ordenada
def fmt(x):
    if x == "Seleccionar...": return x
    try: return f"{x} (${float(PRODUCTOS_DISPONIBLES.get(x,0)):,.0f})"
    except: return x

prod_sel = st.selectbox("Buscar Producto", opc, format_func=fmt)

c_cant, c_add = st.columns([1, 1])
with c_cant: cant_sel = st.number_input("Cantidad", min_value=1, value=1)
with c_add: 
    st.write("")
    st.write("")
    if st.button("➕ AGREGAR", use_container_width=True) and prod_sel != "Seleccionar...":
        precio = int(PRODUCTOS_DISPONIBLES[prod_sel])
        df = st.session_state.carrito.copy()
        if prod_sel in df["Producto"].values:
            idx = df.index[df["Producto"] == prod_sel][0]
            df.loc[idx, "Cantidad"] = int(df.loc[idx, "Cantidad"]) + cant_sel
            df.loc[idx, "Total"] = df.loc[idx, "Precio"] * df.loc[idx, "Cantidad"]
        else:
            nuevo = pd.DataFrame([{"Producto": prod_sel, "Precio": precio, "Cantidad": cant_sel, "Total": precio * cant_sel}])
            df = pd.concat([df, nuevo], ignore_index=True)
        st.session_state.carrito = df
        st.rerun()

if not st.session_state.carrito.empty:
    idx_borrar = None
    for i, row in st.session_state.carrito.iterrows():
        with st.container():
            st.markdown(f"**{row['Producto']}**")
            c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
            c1.write(f"${row['Precio']:,.0f}")
            nc = c2.number_input("Cant", min_value=1, value=int(row["Cantidad"]), key=f"q_{i}", label_visibility="collapsed")
            if nc != row["Cantidad"]:
                st.session_state.carrito.at[i, "Cantidad"] = nc
                st.session_state.carrito.at[i, "Total"] = nc * row["Precio"]
                st.rerun()
            c3.write(f"**${nc*row['Precio']:,.0f}**")
            if c4.button("🗑️", key=f"d_{i}"): idx_borrar = i
        st.divider()
    if idx_borrar is not None:
        st.session_state.carrito = st.session_state.carrito.drop(idx_borrar).reset_index(drop=True)
        st.rerun()

# ---------------------------------------------------------
# 6. TOTALES Y ENVÍO
# ---------------------------------------------------------
clean_df = st.session_state.carrito.copy()
suma_productos = int(clean_df["Total"].sum()) if not clean_df.empty else 0

st.subheader("🛵 Envío y Totales")

c_geo1, c_geo2 = st.columns([2, 1])
with c_geo2:
    st.write("")
    if st.button("📍 Recalcular Manual", use_container_width=True):
        if st.session_state['direccion_final']:
             t, d, _ = calcular_tarifa_domicilio(direccion_texto=st.session_state['direccion_final'])
             if t:
                 st.session_state['valor_domi_calculado'] = t
                 st.toast(f"Distancia aprox: {d}km")

with c_geo1:
    valor_domicilio = st.number_input("Costo Domicilio", value=st.session_state['valor_domi_calculado'], step=500)

medio_pago = st.selectbox("💳 Medio de Pago", ["Efectivo", "Nequi", "DaviPlata", "Datafono"])
total_final = suma_productos + int(valor_domicilio)

st.markdown(f"""
<div style="text-align:center; font-size:32px; font-weight:700; padding:15px; border-radius:12px; background:#e8fff1; color:#004d29; margin-bottom: 20px;">
TOTAL: ${total_final:,.0f}
</div>
""", unsafe_allow_html=True)

total_datafono = ""
if medio_pago == "Datafono":
    v_dat = int(total_final * 1.06)
    st.warning(f"Con Datafono (+6%): ${v_dat:,.0f}")
    total_datafono = st.number_input("Cobrar:", value=v_dat)

if st.button("🚀 ENVIAR PEDIDO", type="primary", use_container_width=True):
    if clean_df.empty:
        st.error("Carrito vacío")
    else:
        prods = []
        for _, row in clean_df.iterrows():
            prods.append({"Producto": str(row["Producto"]), "Cantidad": str(row["Cantidad"]), "Total": str(row["Total"])})
        
        data_json = {
            "MedioPago": medio_pago,
            "ValorTotalV": str(total_final),
            "ValorDomi": str(valor_domicilio),
            "TotalData": str(total_datafono),
            "Factura": str(numero_factura_actual),
            "Domiciliario": domiciliario,
            "Celular": celular,
            "Barrio": barrio,
            "Direccion": st.session_state['direccion_final'],
            "Ubicacion": st.session_state['link_ubicacion'],
            "Observaciones": observaciones,
            "Productos": prods
        }
        
        with st.spinner("Enviando..."):
            res = enviar_a_sheets(data_json)
        
        if hasattr(res, 'status_code') and res.status_code == 200:
            st.balloons()                       # 1. MOSTRAR FIESTA
            st.success("✅ Pedido Enviado!")    # 2. MOSTRAR MENSAJE
            time.sleep(2.5)                     # 3. ESPERAR 2.5 SEGUNDOS PARA QUE SE VEA
            
            # Stock update
            for item in prods:
                pn = item["Producto"]
                cant = int(item["Cantidad"])
                if pn in df_productos["Producto"].values:
                    idx = df_productos.index[df_productos["Producto"] == pn][0]
                    curr = int(df_productos.at[idx, "Stock"])
                    df_productos.at[idx, "Stock"] = max(0, curr - cant)
            guardar_productos(df_productos)
            actualizar_factura_siguiente(numero_factura_actual + 1)
            
            # RESET TOTAL DEL FORMULARIO
            st.session_state.carrito = pd.DataFrame(columns=["Producto","Precio","Cantidad","Total"])
            st.session_state['direccion_final'] = ""
            st.session_state['link_ubicacion'] = ""
            st.session_state['valor_domi_calculado'] = 7000
            st.session_state['gps_temporal'] = None
            
            # Limpiamos los campos del cliente usando sus KEYS
            st.session_state['input_celular'] = "" 
            st.session_state['input_barrio'] = ""
            st.session_state['input_notas'] = ""
            
            st.rerun() # 4. RECARGAR AHORA SÍ
        else:
            st.error("Error al enviar")







