import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ======== CONFIGURAÇÃO STREAMLIT ========
st.set_page_config(page_title="Registro Transferência", layout="centered")
st.title("🚚 Registro de Transferência de Carga")

# ======== CONEXÃO COM GOOGLE SHEETS ========
def conectar_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credenciais.json", scope)
    client = gspread.authorize(creds)
    planilha = client.open("Controle Transferencia")
    aba = planilha.sheet1  # ou planilha.worksheet("Página1") se a aba tiver outro nome
    return aba

# ======== CAMPOS ========
campos_tempo = [
    "Entrada na Fábrica", "Encostou na doca Fábrica", "Início carregamento", "Fim carregamento",
    "Faturado", "Amarração carga", "Saída do pátio", "Entrada CD", "Encostou na doca CD",
    "Início Descarregamento CD", "Fim Descarregamento CD", "Saída CD"
]

# ======== INICIALIZAR CAMPOS DE SESSÃO ========
for campo in campos_tempo:
    if campo not in st.session_state:
        st.session_state[campo] = ""

# ======== CAMPOS MANUAIS ========
st.subheader("Dados do Veículo")
data = st.date_input("Data", value=datetime.today())
placa = st.text_input("Placa do caminhão")
conferente = st.text_input("Nome do conferente")

# ======== BOTÕES DE REGISTRO DE TEMPO ========
def registrar_tempo(label):
    if st.button(f"Registrar {label}"):
        st.session_state[label] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

st.subheader("Fábrica")
for campo in campos_tempo[:7]:
    registrar_tempo(campo)
    st.text_input(campo, value=st.session_state[campo], disabled=True)

st.subheader("Centro de Distribuição (CD)")
for campo in campos_tempo[7:]:
    registrar_tempo(campo)
    st.text_input(campo, value=st.session_state[campo], disabled=True)

# ======== CÁLCULO DE TEMPOS ========
def calc_tempo(fim, inicio):
    try:
        t1 = datetime.strptime(st.session_state[fim], "%Y-%m-%d %H:%M:%S")
        t0 = datetime.strptime(st.session_state[inicio], "%Y-%m-%d %H:%M:%S")
        return str(t1 - t0)
    except:
        return ""

tempo_carreg = calc_tempo("Fim carregamento", "Início carregamento")
tempo_espera = calc_tempo("Encostou na doca Fábrica", "Entrada na Fábrica")
tempo_total = calc_tempo("Saída do pátio", "Entrada na Fábrica")
tempo_descarga = calc_tempo("Fim Descarregamento CD", "Início Descarregamento CD")
tempo_espera_cd = calc_tempo("Encostou na doca CD", "Entrada CD")
tempo_total_cd = calc_tempo("Saída CD", "Entrada CD")
tempo_percurso = calc_tempo("Entrada CD", "Saída do pátio")

# ======== BOTÃO DE SALVAR ========
if st.button("✅ Salvar Registro"):
    nova_linha = [
        str(data),
        placa,
        conferente,
        *[st.session_state[campo] for campo in campos_tempo],
        tempo_carreg,
        tempo_espera,
        tempo_total,
        tempo_descarga,
        tempo_espera_cd,
        tempo_total_cd,
        tempo_percurso,
    ]

    try:
        aba = conectar_google_sheets()
        aba.append_row(nova_linha)
        st.success("Registro salvo com sucesso!")

        # Resetar campos
        for campo in campos_tempo:
            st.session_state[campo] = ""
    except Exception as e:
        st.error(f"Erro ao salvar na planilha: {e}")
