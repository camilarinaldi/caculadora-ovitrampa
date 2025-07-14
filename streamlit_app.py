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
 
# Configurações da página
st.set_page_config(
    page_title="Ovitrampas",
    page_icon=":bug:",
    layout="wide",
    initial_sidebar_state='collapsed'
) 
col1, col2, col3 = st.columns([1,4,1])

col3.image('logo_cevs (1).png', width=150)
col2.header('Painel de Monitoramento de Aedes aegypti através de Ovitrampas')
col1.image('logo_estado (3).png', width=250)

with aba_qualifica:
 texto_qualifica = """
     ### Ficha 5
     Pelo menos 80% dos ciclos mensais de monitoramento realizados (equivalente a 8 meses de monitoramento), conforme os critérios de avaliação.
 """
 st.markdown(texto_qualifica)

 coluna_filtro, coluna_metrica = st.columns([ 1, 2])
 # Criar uma função para fazer a extração dos dados de um município e retornar um dataframe
 def get_last_counting_public(municipality, page=1):
     # Rodar por todas as páginas até o df vir vazio
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
 
 # IDO - Índice Densidade de Ovos
 def get_ido(df):
     ido = round(df[df['eggs'] > 0]['eggs'].mean(), 1)
     return ido
 
 # IPO - Índice de Positividade de Ovos
 def get_ipo(df):
     ipo = ((df['eggs'] > 0).sum() / len(df)).round(3) * 100
     return ipo
 
 # IMO - Índice Médio de Ovos
 def get_imo(df):
     imo = round(df['eggs'].mean(), 1)
     return imo
 
 # Input com o município e o ano
 with coluna_filtro:
  #municipality = st.text_input(label="Digite o nome do município: ", value="Aceguá")
  municipality = st.selectbox("Selecione o município", options = sorted(dados['municipality'].unique()))
  ano_escolhido = st.text_input("Digite o ano desejado (ex: 2025):")
  processar = st.button("Processar")
 
 if processar:
     #df = get_last_counting_public(municipality)
     df_pre_filtro = dados[['counting_id', 'date', 'date_collect', 'eggs', 'latitude', 'longitude',
       'municipality', 'municipality_code', 'ovitrap_id', 'ovitrap_website_id',
       'state_code', 'state_name', 'time', 'week', 'year']]

    # Filtrando o municipio e o ano
     filtro = (df_pre_filtro['municipality'] == municipality)&(df_pre_filtro['year'] == int(ano_escolhido))
     df = df_pre_filtro[filtro]
     
     # Garantir que a coluna 'date' esteja em formato datetime
     df['date'] = pd.to_datetime(df['date'])
 
     # Criar a coluna do mês (nome em inglês)
     df['month'] = df['date'].dt.strftime('%B')
     
     # Traduzir para português
     meses_traducao = {
         'January': 'Janeiro',
         'February': 'Fevereiro',
         'March': 'Março',
         'April': 'Abril',
         'May': 'Maio',
         'June': 'Junho',
         'July': 'Julho',
         'August': 'Agosto',
         'September': 'Setembro',
         'October': 'Outubro',
         'November': 'Novembro',
         'December': 'Dezembro'
     }
     
     df['month'] = df['month'].map(meses_traducao)
 
 
     # Filtrar o DataFrame pelo ano selecionado
     df_filtrado = df[df['year'] == int(ano_escolhido)]
 
     # Agrupar pelos campos desejados e calcular as agregações
     resumo = df_filtrado.groupby(['week', 'month']).agg(
         armadilhas_instaladas=('ovitrap_id', 'count'),
         total_ovos=('eggs', 'sum')
     ).reset_index()

   
 
     # Calcular os índices
     dados_ipo = df_filtrado.groupby('week').apply(get_ipo).reset_index()
     dados_ipo.columns = ['week', 'ipo']
 
     dados_ido = df_filtrado.groupby('week').apply(get_ido).reset_index()
     dados_ido.columns = ['week', 'ido']
 
     dados_imo = df_filtrado.groupby('week').apply(get_imo).reset_index()
     dados_imo.columns = ['week', 'imo']
 
     # Juntar tudo no resumo
     resumo = pd.merge(resumo, dados_ipo, on='week', how='left')
     resumo = pd.merge(resumo, dados_ido, on='week', how='left')
     resumo = pd.merge(resumo, dados_imo, on='week', how='left')
 
     # Renomear colunas para exibição
     resumo.columns = ['Semana Epidemiológica', 'Ciclo (Mês)', 'Armadilhas Instaladas', 'Total de Ovos', 'IPO', 'IDO', 'IMO']
     # Calcular totais do ano
     total_armadilhas = df_filtrado['ovitrap_id'].count()
     total_ovos = df_filtrado['eggs'].sum()
     ipo_total = round(((df_filtrado['eggs'] > 0).sum() / len(df_filtrado)) * 100, 1)
     ido_total = round(df_filtrado[df_filtrado['eggs'] > 0]['eggs'].mean(), 1)
     imo_total = round(df_filtrado['eggs'].mean(), 1)
     
     # Criar DataFrame com a linha total
     linha_total = pd.DataFrame([{
         'Semana Epidemiológica': 'TOTAL',
         'Ciclo (Mês)': '',
         'Armadilhas Instaladas': total_armadilhas,
         'Total de Ovos': total_ovos,
         'IPO': ipo_total,
         'IDO': ido_total,
         'IMO': imo_total
     }])
     
     # Adicionar a linha ao resumo
     resumo = pd.concat([resumo, linha_total], ignore_index=True)
 
     # Contagem de linhas da tabela
     n_linhas = len(resumo) +1
 
     # Exibir resultado
     st.dataframe(resumo, hide_index=True, row_height=39, height=n_linhas*39,
                 column_config={
         "IPO": st.column_config.ProgressColumn(
             "IPO",
             width="small",
             format="%.1f",
             min_value=0,
             max_value=100,
         ),
     },)
 
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
             total_mes = df_filtrado[df_filtrado['month'] == mes_nome]['ovitrap_id'].count()
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
     with coluna_metrica:
        st.subheader("Mapa de Coletas no Ano Selecionado")
        st.markdown(html, unsafe_allow_html=True)
        
        # Legenda
        st.markdown("""
        **Legenda:**  
        🟩 Coleta realizada  🟥 Sem coleta  ⬜ Ainda não monitorado  ⬛ Mês futuro
        """)
 
css='''
[data-testid="stMetric"] {

    margin: auto;
    background-color: #EEEEEE;
    border: 2px solid #CCCCCC;
    border-radius: 15px;
}

[data-testid="stMetric"] > div {
    width: fit-content;
    margin: auto;
}

[data-testid="stMetricLabel"] {
    width: fit-content;
    margin: auto;
}

[data-testid="StyledLinkIconContainer"] > div {
    width: fit-content;
    margin: auto;
}

'''
st.markdown(f'<style>{css}</style>',unsafe_allow_html=True)

'''
st.markdown(f'<style>{css}</style>',unsafe_allow_html=True)
