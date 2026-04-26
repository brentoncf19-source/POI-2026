import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="POI 2026", layout="centered")

# 🎨 ESTILO
st.markdown("""
<style>
body {background-color: #ffc107;}
h1, h2, h3 {text-align: center;}
</style>
""", unsafe_allow_html=True)

# 🔐 USUARIOS
usuarios = {
    "juan": {"password": "1234", "oficina": "Comercial"},
    "maria": {"password": "abcd", "oficina": "Mantenimiento"},
    "marco": {"password": "5678", "oficina": "Logistica"}
}

archivo_resultados = "resultados.xlsx"

# 🔹 LOGIN
if "login" not in st.session_state:
    st.markdown("""
<div style='text-align: center;'>
    <img src='logo.png' width='200'>
    <h1 style='color:#003366;'>CALIFICACIÓN DEL POI 2026</h1>
    <h3>ELECTRO SUR ESTE S.A.A</h3>
</div>
<hr>
""", unsafe_allow_html=True)
    st.markdown("<h3>ELECTRO SUR ESTE S.A.A</h2>", unsafe_allow_html=True)
    st.markdown("### 🔐 Iniciar acceso")

    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        if usuario in usuarios and usuarios[usuario]["password"] == password:
            st.session_state["login"] = True
            st.session_state["usuario"] = usuario
        else:
            st.error("Usuario o contraseña incorrectos")

    st.stop()

# 🔹 USUARIO
usuario = st.session_state["usuario"]
oficina_usuario = usuarios[usuario]["oficina"]

archivo_progreso = f"progreso_{usuario}.xlsx"

# 🔒 BLOQUEO
if os.path.exists(archivo_resultados):
    df_res = pd.read_excel(archivo_resultados)
    if usuario in df_res['USUARIO'].values:
        nota = df_res[df_res['USUARIO'] == usuario]['NOTA_JEFE'].values[0]
        st.success("✅ Evaluación ya realizada")
        st.info(f"Tu nota final fue: {nota:.2f}%")
        st.warning("Acceso bloqueado 🔒")
        st.stop()

# 🔹 CARGAR DATOS
df = pd.read_excel("datos.xlsx")
df.columns = df.columns.str.upper().str.strip()

df_oficina = df[df['OFICINA'] == oficina_usuario]
jefe = df_oficina['JEFE'].iloc[0]

# 🔹 HEADER
st.markdown("## 📊 Evaluación de Desempeño")
col1, col2 = st.columns(2)
col1.metric("👤 Usuario", usuario)
col2.metric("🏢 Oficina", oficina_usuario)

st.info(f"Jefe responsable: {jefe}")

trabajadores = df_oficina['TRABAJADOR'].unique()

# 🔹 CARGAR PROGRESO
progreso = {}
if os.path.exists(archivo_progreso):
    df_prog = pd.read_excel(archivo_progreso)
    for _, row in df_prog.iterrows():
        key = f"{row['TRABAJADOR']}_{row['ACTIVIDAD']}"
        progreso[key] = row['NOTA']

promedios_trabajadores = []
datos_guardar = []

st.markdown("## 📋 Calificación de trabajadores")

total = len(trabajadores)
contador = 0

# 🔹 FORMULARIO
for trabajador in trabajadores:
    contador += 1

    with st.container():
        st.markdown(f"""
        <div style='background-blue:blue;padding:15px;border-radius:10px;margin-bottom:10px;box-shadow:2px 2px 5px #ccc'>
        <h4>👤 {trabajador}</h4>
        </div>
        """, unsafe_allow_html=True)

        actividades = df_oficina[df_oficina['TRABAJADOR'] == trabajador]

        notas = []

        for i, row in actividades.iterrows():
            key = f"{trabajador}_{row['ACTIVIDAD']}"
            valor = progreso.get(key, 0)

            nota = st.slider(
                f"{row['ACTIVIDAD']}",
                0, 100,
                value=int(valor),
                key=key
            )

            notas.append(nota)

            datos_guardar.append({
                "TRABAJADOR": trabajador,
                "ACTIVIDAD": row['ACTIVIDAD'],
                "NOTA": nota
            })

        promedio = sum(notas) / len(notas)
        st.metric("Promedio trabajador (%)", f"{promedio:.2f}")

        promedios_trabajadores.append(promedio)

    # Barra de progreso
    st.progress(contador / total)

# 🔹 GUARDADO AUTOMÁTICO
df_prog = pd.DataFrame(datos_guardar)
df_prog.to_excel(archivo_progreso, index=False)

# 🔥 FINALIZAR
if st.button("FINALIZAR CALIFICACIÓN"):

    promedio_jefe = sum(promedios_trabajadores) / len(promedios_trabajadores)

    nuevo = pd.DataFrame({
        "USUARIO": [usuario],
        "OFICINA": [oficina_usuario],
        "NOTA_JEFE": [promedio_jefe]
    })

    if os.path.exists(archivo_resultados):
        df_res = pd.read_excel(archivo_resultados)
        df_res = pd.concat([df_res, nuevo], ignore_index=True)
    else:
        df_res = nuevo

    df_res.to_excel(archivo_resultados, index=False)

    # borrar progreso
    if os.path.exists(archivo_progreso):
        os.remove(archivo_progreso)

    st.markdown("## 🎉 Evaluación completada")
    st.success(f"Gracias por tu calificación")
    st.markdown(f"### 📊 Nota final: {promedio_jefe:.2f}%")
    st.warning("Acceso cerrado 🔒")

    st.stop()