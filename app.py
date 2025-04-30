import streamlit as st
import pywhatkit
import datetime

# ---------------------- FUNCIONES DE LA CALCULADORA ----------------------
def calcular_tmb(peso, altura_cm, edad, genero):
    if genero.lower() == "m":
        return (10 * peso) + (6.25 * altura_cm) - (5 * edad) + 5
    else:
        return (10 * peso) + (6.25 * altura_cm) - (5 * edad) - 161

def calcular_imc(peso, altura_cm):
    altura_m = altura_cm / 100
    return peso / (altura_m ** 2)

def calcular_get(tmb, actividad):
    return tmb * actividad

# ---------------------- CONFIGURACIÓN STREAMLIT ----------------------
st.title("📊 Calculadora Nutricional")

# Entrada de datos del usuario
nombre = st.text_input("Ingrese su nombre:", value=st.session_state.get("nombre", ""))
edad = st.number_input("Ingrese su edad (años):", min_value=1, max_value=120, step=1,
                       value=st.session_state.get("edad", 25))
peso = st.number_input("Ingrese su peso (kg):", min_value=1.0, max_value=300.0, step=0.1,
                       value=st.session_state.get("peso", 70.0))
altura_cm = st.number_input("Ingrese su altura (cm):", min_value=50, max_value=250, step=1,
                            value=st.session_state.get("altura", 170))
genero = st.radio("Seleccione su género:", ["M", "F"], index=0 if st.session_state.get("genero", "M") == "M" else 1)

# Guardar valores en session_state
st.session_state["nombre"] = nombre
st.session_state["edad"] = edad
st.session_state["peso"] = peso
st.session_state["altura"] = altura_cm
st.session_state["genero"] = genero

# Selección de actividad física
actividad_opciones = {
    "Poco o ningún ejercicio": 1.2,
    "Ligero": 1.375,
    "Moderado": 1.55,
    "Fuerte": 1.725,
    "Muy fuerte": 1.9
}
actividad = st.selectbox("Seleccione su nivel de actividad física:", list(actividad_opciones.keys()), index=2)
factor_actividad = actividad_opciones[actividad]

if st.button("Calcular"):
    tmb = calcular_tmb(peso, altura_cm, edad, genero)
    imc = calcular_imc(peso, altura_cm)
    get = calcular_get(tmb, factor_actividad)

    st.session_state["tmb"] = tmb
    st.session_state["imc"] = imc
    st.session_state["get"] = get

    st.write(f"**{nombre}, aquí están sus resultados:**")
    st.write(f"✅ **IMC:** {imc:.2f}")

    if imc < 18.5:
        st.warning("Clasificación: Bajo peso")
    elif imc < 25:
        st.success("Clasificación: Peso normal")
    elif imc < 30:
        st.warning("Clasificación: Sobrepeso")
    else:
        st.error("Clasificación: Obesidad")

    st.write(f"🔥 **TMB:** {tmb:.2f} kcal")
    st.write(f"⚡ **GET:** {get:.2f} kcal")

# Distribución calórica de macronutrientes
if "get" in st.session_state:
    st.subheader("📌 Distribución calórica de macronutrientes (en %)")

    if "porc_carbs" not in st.session_state:
        st.session_state["porc_carbs"] = 50.0
    if "porc_prot" not in st.session_state:
        st.session_state["porc_prot"] = 25.0
    if "porc_lipidos" not in st.session_state:
        st.session_state["porc_lipidos"] = 25.0

    porc_carbs = st.number_input("Carbohidratos (%):", min_value=0.0, max_value=100.0, step=1.0,
                                 value=st.session_state["porc_carbs"])
    porc_prot = st.number_input("Proteínas (%):", min_value=0.0, max_value=100.0, step=1.0,
                                value=st.session_state["porc_prot"])
    porc_lipidos = st.number_input("Lípidos (%):", min_value=0.0, max_value=100.0, step=1.0,
                                   value=st.session_state["porc_lipidos"])

    st.session_state["porc_carbs"] = porc_carbs
    st.session_state["porc_prot"] = porc_prot
    st.session_state["porc_lipidos"] = porc_lipidos

    suma_porcentajes = porc_carbs + porc_prot + porc_lipidos

    if suma_porcentajes != 100:
        st.warning("⚠️ Los porcentajes deben sumar exactamente 100%. Ajuste los valores.")
    else:
        cal_carbs = (st.session_state["get"] * porc_carbs) / 100
        cal_prot = (st.session_state["get"] * porc_prot) / 100
        cal_lipidos = (st.session_state["get"] * porc_lipidos) / 100

        g_carbs = cal_carbs / 4
        g_prot = cal_prot / 4
        g_lipidos = cal_lipidos / 9

        st.success("✅ Distribución calórica válida.")

        st.write("### 🍽️ Distribución de macronutrientes")
        st.table({
            "Macronutriente": ["Carbohidratos", "Proteínas", "Lípidos", "Total"],
            "Gramos": [f"{g_carbs:.2f} g", f"{g_prot:.2f} g", f"{g_lipidos:.2f} g",
                       f"{(g_carbs + g_prot + g_lipidos):.2f} g"],
            "Kcal": [f"{cal_carbs:.2f} kcal", f"{cal_prot:.2f} kcal", f"{cal_lipidos:.2f} kcal",
                     f"{st.session_state['get']:.2f} kcal"],
            "Porcentaje": [f"{porc_carbs}%", f"{porc_prot}%", f"{porc_lipidos}%", "100%"],
            "Gramos por kg de peso": [f"{g_carbs / peso:.2f} g/kg", f"{g_prot / peso:.2f} g/kg", f"{g_lipidos / peso:.2f} g/kg", "-"]
        })

# ---------------------- MÓDULO WHATSAPP ----------------------
st.header("📱 Enviar Mensaje de WhatsApp")

st.info("Puedes ingresar hasta 15 números de teléfono con su código de país, sin espacios.")

numeros = st.text_area("Números de WhatsApp (uno por línea, formato: +1234567890)")
mensaje = st.text_area("Mensaje que quieres enviar:")

if st.button("Enviar Mensaje(s)"):
    lista_numeros = [n.strip() for n in numeros.split("\n") if n.strip()]
    if len(lista_numeros) > 15:
        st.error("⚠️ Solo puedes enviar a un máximo de 15 números.")
    elif not mensaje:
        st.error("⚠️ El mensaje no puede estar vacío.")
    else:
        hora_actual = datetime.datetime.now()
        minutos = hora_actual.minute + 2

        st.success(f"Preparando para enviar {len(lista_numeros)} mensaje(s)...")

        for numero in lista_numeros:
            try:
                pywhatkit.sendwhatmsg(numero, mensaje, hora_actual.hour, minutos, wait_time=10, tab_close=True)
                minutos += 1  # Para que no se sobrepongan los envíos
                st.write(f"✅ Mensaje programado para {numero}")
            except Exception as e:
                st.error(f"❌ Error enviando a {numero}: {e}")
