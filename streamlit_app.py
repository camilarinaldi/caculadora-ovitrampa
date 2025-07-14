#Importação das bibliotecas 
import requests
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium, folium_static
import streamlit as st
import time
from altair import Chart
import plotly.figure_factory as ff
import geopandas as gpd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
 
from datetime import datetime

# Importação das bibliotecas
import pandas as pd
import requests
import streamlit as st

# Função para extrair dados do município
def get_last_counting_public(municipality, page=1):
    dados = pd.DataFrame()
    while True:
        url = f"https://contaovos.com/pt-br/api/lastcountingpublic?state=RS&municipality={municipality}&page={page}"
        response = requests.get(url)
        data = response.json()
        df = pd.DataFrame(data)
        if df.empty:
            break
        dados = pd.concat([dados, df], ignore_index=True)
        page += 1
    return dados

# Índices
def get_ido(df):
    return round(df[df['eggs'] > 0]['eggs'].mean(), 1)

def get_ipo(df):
    return round(((df['eggs'] > 0).sum() / len(df)) * 100, 1)

def get_imo(df):
    return round(df['eggs'].mean(), 1)

# Interface Streamlit
st.title("Painel de Monitoramento - Ovos de Aedes")
municipality = st.text_input("Digite o nome do município:", value="Aceguá")
ano_escolhido = st.text_input("Digite o ano desejado (ex: 2025):")
processar = st.button("Processar")

if processar:
    df = get_last_counting_public(municipality)
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.strftime('%B')

    # Traduzir meses para português
    meses_traducao = {
        'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março',
        'April': 'Abril', 'May': 'Maio', 'June': 'Junho',
        'July': 'Julho', 'August': 'Agosto', 'September': 'Setembro',
        'October': 'Outubro', 'November': 'Novembro', 'December': 'Dezembro'
    }
    df['month'] = df['month'].map(meses_traducao)

    # Filtrar pelo ano escolhido
    df_filtrado = df[df['year'] == int(ano_escolhido)]

    # Verificação de dados
    if df_filtrado.empty:
        st.warning("Este município/ano não consta no banco de dados.")
        st.stop()

    # Tabela resumo por semana
    resumo = df_filtrado.groupby(['week', 'month']).agg(
        armadilhas_instaladas=('ovitrap_id', 'count'),
        total_ovos=('eggs', 'sum')
    ).reset_index()

    # Cálculo dos índices semanais
    dados_ipo = df_filtrado.groupby('week').apply(get_ipo).reset_index()
    dados_ipo.columns = ['week', 'ipo']

    dados_ido = df_filtrado.groupby('week').apply(get_ido).reset_index()
    dados_ido.columns = ['week', 'ido']

    dados_imo = df_filtrado.groupby('week').apply(get_imo).reset_index()
    dados_imo.columns = ['week', 'imo']

    # Juntar dados ao resumo
    resumo = pd.merge(resumo, dados_ipo, on='week', how='left')
    resumo = pd.merge(resumo, dados_ido, on='week', how='left')
    resumo = pd.merge(resumo, dados_imo, on='week', how='left')

    # Renomear colunas
    resumo.columns = ['Semana Epidemiológica', 'Ciclo (Mês)', 'Armadilhas Instaladas', 'Total de Ovos', 'IPO', 'IDO', 'IMO']

    # Calcular linha total do ano
    total_armadilhas = df_filtrado['ovitrap_id'].count()
    total_ovos = df_filtrado['eggs'].sum()
    ipo_total = round(((df_filtrado['eggs'] > 0).sum() / len(df_filtrado)) * 100, 1)
    ido_total = round(df_filtrado[df_filtrado['eggs'] > 0]['eggs'].mean(), 1)
    imo_total = round(df_filtrado['eggs'].mean(), 1)

    linha_total = pd.DataFrame([{
        'Semana Epidemiológica': 'TOTAL',
        'Ciclo (Mês)': '',
        'Armadilhas Instaladas': total_armadilhas,
        'Total de Ovos': total_ovos,
        'IPO': ipo_total,
        'IDO': ido_total,
        'IMO': imo_total
    }])

    # Adicionar linha total
    resumo = pd.concat([resumo, linha_total], ignore_index=True)

 from datetime import datetime

# Lista de meses em português, na ordem correta
meses_ordem = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
               'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

# Obter mês e ano atual
data_atual = datetime.now()
ano_atual = data_atual.year
mes_atual = data_atual.month

# Obter meses com dados no ano selecionado
meses_com_dado = df_filtrado['month'].unique().tolist()
meses_com_dado = [m for m in meses_ordem if m in meses_com_dado]

# Descobrir o primeiro mês em que houve qualquer tipo de registro (mesmo sem ovos)
if not df_filtrado.empty:
    primeiro_mes_index = df_filtrado['date'].dt.month.min()
else:
    primeiro_mes_index = 13  # valor impossível para garantir "ainda não monitorado"

# Construir a cor de cada célula
mapa_celulas = {}
for idx, mes_nome in enumerate(meses_ordem, start=1):
    if int(ano_escolhido) > ano_atual:
        cor = 'gray'  # ano futuro
    elif int(ano_escolhido) == ano_atual and idx > mes_atual:
        cor = 'gray'  # mês futuro no mesmo ano
    elif idx < primeiro_mes_index:
        cor = 'white'  # ainda não monitorado
    elif mes_nome in meses_com_dado:
        total_mes = df_filtrado[df_filtrado['month'] == mes_nome]['eggs'].sum()
        cor = 'green' if total_mes > 0 else 'red'
    else:
        cor = 'red'  # monitoramento iniciado, mas sem coleta
    mapa_celulas[mes_nome] = cor

# Montar HTML da tabela
html = "<table style='width:100%; text-align:center; border-collapse:collapse;'>"
html += "<tr>" + "".join([f"<th style='border:1px solid black;'>{mes}</th>" for mes in meses_ordem]) + "</tr>"
html += "<tr>" + "".join([f"<td style='background-color:{mapa_celulas[mes]}; border:1px solid black; height:40px;'></td>" for mes in meses_ordem]) + "</tr>"
html += "</table>"

# Exibir
st.subheader("Mapa de Coletas no Ano Selecionado")
st.markdown(html, unsafe_allow_html=True)

# Legenda
st.markdown("""
**Legenda:**  
🟩 Coleta realizada  🟥 Sem coleta  ⬜ Ainda não monitorado  ⬛ Mês futuro
""")

 
    # Exibir tabela
    st.dataframe(resumo)
