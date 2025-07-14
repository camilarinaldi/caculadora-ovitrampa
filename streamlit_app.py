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

'''
st.markdown(f'<style>{css}</style>',unsafe_allow_html=True)
