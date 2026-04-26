import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="POI 2026", layout="centered")

# 🎨 ESTILO
st.markdown("""
<style>
body {background-color: #f4f6f7;}
h1 {color:#003366; text-align:center;}
h3 {text-align:center; color:#555;}
</style>
""", unsafe_allow_html=True)

# 🔐 USUARIOS
usuarios = {
    "juan": {"password": "1234", "oficina": "Comercial"},
    "maria": {"password": "abcd", "oficina": "Mantenimiento"},
    "marco": {"password": "5678", "oficina": "Logistica"}
}

# 🔹 CONEXIÓN GOOGLE SHEETS
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = st.secrets["gcp_service_account"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

client = gspread.authorize(creds)
sheet = client.open_by_key("18NuH5g4L8zp8VUHY2YJGuuegIL9xV73tGiF2hixtOsU").sheet1

# =========================
# 🔐 LOGIN
# =========================
if "login" not in st.session_state:
    st.markdown("""
    <div style='text-align: center;'>
        <img src='logo.png' width='120'>
        <h1>CALIFICACIÓN DEL POI 2026</h1>
        <h3>ELECTRO SUR ESTE S.A.A</h3>
    </div>
    """, unsafe_allow_html=True)

    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        if usuario in usuarios and usuarios[usuario]["password"] == password:
            st.session_state["login"] = True
            st.session_state["usuario"] = usuario
        else:
            st.error("Usuario o contraseña incorrectos")

    st.stop()

# =========================
# 🔹 USUARIO ACTIVO
# =========================
usuario = st.session_state["usuario"]
oficina_usuario = usuarios[usuario]["oficina"]

# =========================
# 🔴 BLOQUEO SI YA EVALUÓ (MEJORADO)
# =========================
data = sheet.get_all_records()
df_res = pd.DataFrame(data)

if not df_res.empty:
    df_res.columns = df_res.columns.str.upper().str.strip()

    if "USUARIO" in df_res.columns and usuario in df_res["USUARIO"].values:
        nota = df_res[df_res["USUARIO"] == usuario]["NOTA_JEFE"].values[0]

        st.success("✅ Evaluación ya realizada")
        st.info(f"Tu nota final fue: {nota:.2f}%")
        st.warning("Acceso bloqueado 🔒")

        st.session_state["evaluado"] = True
        st.stop()

# 🚫 BLOQUEO EXTRA POR SESIÓN
if st.session_state.get("evaluado"):
    st.warning("Ya realizaste la evaluación 🔒")
    st.stop()

# =========================
# 🔹 CARGAR DATOS BASE
# =========================
df = pd.read_excel("datos.xlsx")
df.columns = df.columns.str.upper().str.strip()

df_oficina = df[df['OFICINA'] == oficina_usuario]
jefe = df_oficina['JEFE'].iloc[0]

# =========================
# HEADER
# =========================
st.markdown(f"""
<div style='text-align: center;'>
    <h2>Bienvenido {usuario}</h2>
    <p>🏢 Oficina: {oficina_usuario} | 👨‍💼 Jefe: {jefe}</p>
</div>
<hr>
""", unsafe_allow_html=True)

trabajadores = df_oficina['TRABAJADOR'].unique()

st.markdown("## 📊 Evaluación de trabajadores")

promedios_trabajadores = []

# =========================
# FORMULARIO
# =========================
for trabajador in trabajadores:

    st.markdown(f"""
    <div style='background-color:white;padding:10px;border-radius:10px;margin-bottom:10px;box-shadow:2px 2px 5px #ccc'>
    <h4>👤 {trabajador}</h4>
    </div>
    """, unsafe_allow_html=True)

    actividades = df_oficina[df_oficina['TRABAJADOR'] == trabajador]

    notas = []

    for i, row in actividades.iterrows():
        nota = st.slider(
            f"{row['ACTIVIDAD']}",
            0, 100,
            key=f"{trabajador}_{i}"
        )
        notas.append(nota)

    promedio = sum(notas) / len(notas)
    st.metric("Promedio trabajador (%)", f"{promedio:.2f}")

    promedios_trabajadores.append(promedio)

# =========================
# FINALIZAR
# =========================
if st.button("FINALIZAR CALIFICACIÓN"):

    promedio_jefe = sum(promedios_trabajadores) / len(promedios_trabajadores)

    # GUARDAR EN SHEETS
    sheet.append_row([usuario, oficina_usuario, promedio_jefe])

    st.session_state["evaluado"] = True

    st.markdown("## 🎉 Evaluación completada")
    st.success("Gracias por tu calificación")
    st.markdown(f"### 📊 Nota final: {promedio_jefe:.2f}%")
    st.warning("Acceso cerrado 🔒")

    st.stop()
