
import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# Caminho para o arquivo de credenciais JSON da conta de serviço
CREDENTIALS_FILE = "streamlit-transferencias-255ce73fd8a1.json"
SPREADSHEET_NAME = "Transferencias"
SHEET_NAME = "Página1"

# Autenticação com Google Sheets (usando google-auth)
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scope)
client = gspread.authorize(credentials)
sheet = client.open(SPREADSHEET_NAME).worksheet(SHEET_NAME)

st.set_page_config(page_title="Registro Transferência", layout="centered")
st.title("🚚 Registro de Transferência de Carga")

# Função para registrar timestamp atual
def registrar_tempo(label):
    if st.button(f"Registrar {label}"):
        st.session_state[label] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Inicializar variáveis de sessão
campos_tempo = [
    "Entrada na Fábrica", "Encostou na doca Fábrica", "Início carregamento", "Fim carregamento",
    "Faturado", "Amarração carga", "Saída do pátio", "Entrada CD", "Encostou na doca CD",
    "Início Descarregamento CD", "Fim Descarregamento CD", "Saída CD"
]

for campo in campos_tempo:
    if campo not in st.session_state:
        st.session_state[campo] = ""

# Campos manuais
st.subheader("Dados do Veículo")
data = st.date_input("Data", value=datetime.today())
placa = st.text_input("Placa do caminhão")
conferente = st.text_input("Nome do conferente")

# Campos com botoes
st.subheader("Fábrica")
for campo in campos_tempo[:7]:
    registrar_tempo(campo)
    st.text_input(campo, value=st.session_state[campo], disabled=True)

st.subheader("Centro de Distribuição (CD)")
for campo in campos_tempo[7:]:
    registrar_tempo(campo)
    st.text_input(campo, value=st.session_state[campo], disabled=True)

# Calcular tempos automáticos
def calc_tempo(fim, inicio):
    try:
        t1 = datetime.strptime(st.session_state[fim], "%Y-%m-%d %H:%M:%S")
        t0 = datetime.strptime(st.session_state[inicio], "%Y-%m-%d %H:%M:%S")
        return str(t1 - t0)
    except:
        return ""

# Campos calculados
tempo_carreg = calc_tempo("Fim carregamento", "Início carregamento")
tempo_espera = calc_tempo("Encostou na doca Fábrica", "Entrada na Fábrica")
tempo_total = calc_tempo("Saída do pátio", "Entrada na Fábrica")
tempo_descarga = calc_tempo("Fim Descarregamento CD", "Início Descarregamento CD")
tempo_espera_cd = calc_tempo("Encostou na doca CD", "Entrada CD")
tempo_total_cd = calc_tempo("Saída CD", "Entrada CD")
tempo_percurso = calc_tempo("Entrada CD", "Saída do pátio")

# Botão para salvar
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
        tempo_percurso
    ]

    try:
        sheet.append_row(nova_linha)
        st.success("Registro salvo com sucesso no Google Sheets!")
        for campo in campos_tempo:
            st.session_state[campo] = ""
    except Exception as e:
        st.error(f"Erro ao salvar no Google Sheets: {e}")


