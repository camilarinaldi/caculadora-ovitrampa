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

@st.cache_data
def buscar_dados(ttl=60):
 dados = pd.read_csv('https://drive.google.com/uc?export=download&id=1BYTwzHDITp-VA-6K8lqziIiJl9PCdXqJ', sep=';', compression = 'zip')
 dados_todo_periodo = pd.read_excel('https://drive.google.com/uc?export=download&id=1BcxH8L2NxlAJPyFW7o6Qcj3wvKpOZSvB')
 df_resultados = pd.read_excel('https://drive.google.com/uc?export=download&id=1-tLO7Q3bDHsSBRg85XdRGbkhZGFfcmyC')
 dados['municipality'] = dados['municipality'].replace({'Westfália':'Westfalia','Vespasiano Corrêa':'Vespasiano Correa'})
 dados['week_year'] = dados['week_year'].astype(str)
 return dados, dados_todo_periodo, df_resultados

dados, df_periodo_todo, df_resultados = buscar_dados()
#buscando dados regiao saúde
dados_municipios = pd.read_csv('https://raw.githubusercontent.com/andrejarenkow/csv/master/Munic%C3%ADpios%20RS%20IBGE6%20Popula%C3%A7%C3%A3o%20CRS%20Regional%20-%20P%C3%A1gina1.csv')
municipios_nome = dados_municipios[['Município', 'Região_saude', 'CRS']]
municipios_nome = municipios_nome.set_index('Município')
dicionario_municipios =  municipios_nome.to_dict()['Região_saude']
# Inserindo Aldeia Km 10 no dicionario_municipios como "Aldeia indígena"
dicionario_municipios['Aldeia KM 10'] = 'Aldeias indígenas'

dicionario_municipios_crs =  municipios_nome.to_dict()['CRS']
# Inserindo Aldeia Km 10 no dicionario_municipios como "Aldeia indígena"
dicionario_municipios_crs['Aldeia KM 10'] = 'Aldeias indígenas'

dicionario_crs_texto = {
    1:'01ª CRS',
    2:'02ª CRS',
    3:'03ª CRS',
    4:'04ª CRS',
    5:'05ª CRS',
    6:'06ª CRS',
    7:'07ª CRS',
    8:'08ª CRS',
    9:'09ª CRS',
    10:'10ª CRS',
    11:'11ª CRS',
    12:'12ª CRS',
    13:'13ª CRS',
    14:'14ª CRS',
    15:'15ª CRS',
    16:'16ª CRS',
    17:'17ª CRS',
    18:'18ª CRS',
 'Aldeias indígenas':'Aldeias indígenas'
    }

macros = {'Sul':9,
          'Vales':18,
          'Missioneira':16,
          'Norte':29,
          'Serra':10,
          'Metropolitana':6,
          'Centro-Oeste':12}
# Dicionário com os resultados das regiões e anos
resultados_por_regiao_ano = {
    'Região 01 - Verdes Campos': {2024: 4, 2025: 7, 2026: 9, 2027: 11},
    'Região 02 - Entre Rios': {2024: 2, 2025: 3, 2026: 4, 2027: 6},
    'Região 03 - Fronteira Oeste': {2024: 2, 2025: 3, 2026: 4, 2027: 6},
    'Região 04 - Belas Praias': {2024: 2, 2025: 4, 2026: 5, 2027: 6},
    'Região 05 - Bons Ventos': {2024: 2, 2025: 3, 2026: 4, 2027: 6},
    'Região 06 - Vale do Paranhana e Costa Serra': {2024: 2, 2025: 2, 2026: 3, 2027: 4},
    'Região 07 - Vale dos Sinos': {2024: 3, 2025: 5, 2026: 6, 2027: 8},
    'Região 08 - Vale do Caí e Metropolitana': {2024: 4, 2025: 5, 2026: 7, 2027: 9},
    'Região 09 - Carbonífera/Costa Doce': {2024: 4, 2025: 6, 2026: 8, 2027: 10},
    'Região 10 - Capital e Vale do Gravataí': {2024: 1, 2025: 2, 2026: 2, 2027: 3},
    'Região 11 - Sete Povos das Missões': {2024: 5, 2025: 7, 2026: 10, 2027: 12},
    'Região 12 - Portal das Missões': {2024: 2, 2025: 4, 2026: 5, 2027: 6},
    'Região 13 - Diversidade': {2024: 5, 2025: 7, 2026: 9, 2027: 11},
    'Região 14 - Fronteira Noroeste': {2024: 4, 2025: 7, 2026: 9, 2027: 11},
    'Região 15 - Caminho das Águas': {2024: 5, 2025: 8, 2026: 10, 2027: 13},
    'Região 16 - Alto Uruguai Gaúcho': {2024: 7, 2025: 9, 2026: 13, 2027: 15},
    'Região 17 - Planalto': {2024: 6, 2025: 8, 2026: 11, 2027: 13},
    'Região 18 - Araucárias': {2024: 4, 2025: 6, 2026: 8, 2027: 10},
    'Região 19 - Botucaraí': {2024: 3, 2025: 4, 2026: 6, 2027: 7},
    'Região 20 - Rota da Produção': {2024: 5, 2025: 8, 2026: 10, 2027: 13},
    'Região 21 - Sul': {2024: 4, 2025: 7, 2026: 9, 2027: 11},
    'Região 22 - Pampa': {2024: 1, 2025: 2, 2026: 2, 2027: 3},
    'Região 23 - Caxias e Hortênsias': {2024: 1, 2025: 2, 2026: 2, 2027: 3},
    'Região 24 - Campos de Cima da Serra': {2024: 2, 2025: 3, 2026: 4, 2027: 5},
    'Região 25 - Vinhedos e Basalto': {2024: 4, 2025: 6, 2026: 8, 2027: 11},
    'Região 26 - Uva Vale': {2024: 2, 2025: 4, 2026: 5, 2027: 6},
    'Região 27 - Jacuí Centro': {2024: 2, 2025: 4, 2026: 5, 2027: 6},
    'Região 28 - Vale do Rio Pardo': {2024: 2, 2025: 3, 2026: 4, 2027: 5},
    'Região 29 - Vales e Montanhas': {2024: 8, 2025: 8, 2026: 14, 2027: 14},
    'Região 30 - Vale da Luz': {2024: 2, 2025: 3, 2026: 4, 2027: 6}
}

macros = {
    'Centro-Oeste': {2024: 9, 2025: 14, 2026: 18, 2027: 22},
    'Metropolitana': {2024: 18, 2025: 27, 2026: 36, 2027: 45},
    'Missioneira': {2024: 16, 2025: 23, 2026: 31, 2027: 39},
    'Norte': {2024: 29, 2025: 44, 2026: 59, 2027: 74},
    'Serra': {2024: 10, 2025: 15, 2026: 20, 2027: 25},
    'Sul': {2024: 6, 2025: 8, 2026: 11, 2027: 14},
    'Vales': {2024: 12, 2025: 19, 2026: 25, 2027: 31}
}

#criando a nova coluna para região de saúde
dados['regiao_saude'] = dados['municipality'].map(dicionario_municipios)
dados['CRS'] = dados['municipality'].map(dicionario_municipios_crs)
dados['CRS'] = dados['CRS'].map(dicionario_crs_texto)
aba_painel,aba_analise, aba_sobre, aba_indicador,aba_qualifica, aba_referencias,  = st.tabs(['Painel','Análise', 'Sobre','Pactuação - Indicador 9','Qualifica Vigilância RS', 'Documentos de Referência'])
#dados
with aba_painel:
 
 filtros, metricas, novas_metricas = st.columns([3,4,2])
 
 with filtros:
  container = st.container(border=True)
  with container:
   #st.write('Filtros')
   col1, col2 = st.columns(2)
   
   with col1:
    #Criando filtros
    ano = st.selectbox('Selecione o ano', options=sorted(dados['year'].unique()), index=3)
    # Filtrar por um ou outro
    filtro_regional = st.radio('Filtro regional', options=['Região de saúde','CRS'], horizontal=True)
    dicionario_filtro_regional = {'Região de saúde':'regiao_saude', 'CRS':'CRS'}
    coluna_selecionada = dicionario_filtro_regional[filtro_regional]
    lista_regioes_saude = sorted(dados[dicionario_filtro_regional[filtro_regional]].dropna().astype(str).unique())

    
    lista_regioes_saude.append('Todas')
    regiao_saude = st.selectbox(f'Selecione a {filtro_regional}', options=lista_regioes_saude, index=len(lista_regioes_saude)-1)
    
    
    lista_municipios = sorted(dados[(dados['year']==ano)&(dados[coluna_selecionada]==regiao_saude)]['municipality'].unique())
    lista_municipios.append('Todos')
    municipio = st.selectbox('Selecione o município', options=lista_municipios, index=len(lista_municipios)-1)
   
    if municipio != 'Todos':
     mes = st.selectbox('Selecione o mês', options=sorted(dados[(dados['municipality']==municipio)&(dados['year']==ano)]['mes'].unique()))
     semana_epidemiologica = dados[(dados['municipality']==municipio)&(dados['year']==ano)&(dados['mes']==mes)]['week'].values[0]
     st.write(f'Semana epidemiológica {semana_epidemiologica}')
  
    else:
     mes = st.selectbox('Selecione o mês', options=sorted(dados[(dados['year']==ano)]['mes'].unique()))

   with col2:
    st.write('### Quantidade de ovos')
    lista_filtro_faixa = []
    
    # Nenhum
    colA, colB = st.columns([9, 1])
    with colA:
        filtro_faixa_0 = st.toggle('Nenhum', value=True)
        if filtro_faixa_0:
            lista_filtro_faixa.append('lightgray')
    with colB:
        st.markdown('<span style="font-size: 24px; color: lightgray;">●</span>', unsafe_allow_html=True)
    
    # 1 a 50
    colA, colB = st.columns([9, 1])
    with colA:
        filtro_faixa_1_a_50 = st.toggle('1 a 50', value=True)
        if filtro_faixa_1_a_50:
            lista_filtro_faixa.append('limegreen')
    with colB:
        st.markdown('<span style="font-size: 24px; color: limegreen;">●</span>', unsafe_allow_html=True)
    
    # 51 a 100
    colA, colB = st.columns([9, 1])
    with colA:
        filtro_faixa_50_a_100 = st.toggle('51 a 100', value=True)
        if filtro_faixa_50_a_100:
            lista_filtro_faixa.append('gold')
    with colB:
        st.markdown('<span style="font-size: 24px; color: gold;">●</span>', unsafe_allow_html=True)
    
    # 101 a 200
    colA, colB = st.columns([9, 1])
    with colA:
        filtro_faixa_100_a_200 = st.toggle('101 a 200', value=True)
        if filtro_faixa_100_a_200:
            lista_filtro_faixa.append('orange')
    with colB:
        st.markdown('<span style="font-size: 24px; color: orange;">●</span>', unsafe_allow_html=True)
    
    # Mais de 200
    colA, colB = st.columns([9, 1])
    with colA:
        filtro_faixa_200_ou_mais = st.toggle('Mais de 200', value=True)
        if filtro_faixa_200_ou_mais:
            lista_filtro_faixa.append('red')
    with colB:
        st.markdown('<span style="font-size: 24px; color: red;">●</span>', unsafe_allow_html=True)
 
 #Criar novo dataframe com os valores médios de cada ovitrampa
 if municipio == 'Todos':
  dados_mapa_geral = dados[(dados['year']==ano)]
 
 else:
  filtro = (dados['municipality']==municipio)&(dados['week']==semana_epidemiologica)&(dados['year']==ano)
  dados_mapa_geral = pd.pivot_table(dados[filtro], index=['latitude','longitude', 'municipality', 'ovitrap_id', 'regiao_saude','CRS'], values='eggs', aggfunc='mean').reset_index()

 #IPO IDO IMO
 #IDO - Índice Densidade de Ovos
 def get_ido(df):
     ido = (df[df['eggs']>0]['eggs'].mean())
 
     return ido
 #IPO - Índice de Positividade de Ovos
 def get_ipo(df):
     ipo = ((df['eggs']>0).sum()/len(df)).round(4)
 
     return ipo
 
 #IMO - Índice Médio de Ovos
 def get_imo(df):
     imo = df['eggs'].mean()
 
     return imo
 

 
 if municipio == 'Todos':
  if regiao_saude == 'Todas':
   dados_grafico = dados.copy()

  else:
   st.write(f'{dicionario_filtro_regional[filtro_regional]}')
   st.write(f'{regiao_saude}')
   dados_grafico = dados[dados[coluna_selecionada]==regiao_saude]
 
 else:
  dados_grafico = dados[dados['municipality']==municipio]

 
 dados_ipo = dados_grafico.groupby('mes_ano').apply(get_ipo).reset_index()
 dados_ipo['Métrica'] = 'IPO'
 dados_ido = dados_grafico.groupby('mes_ano').apply(get_ido).reset_index()
 dados_ido['Métrica'] = 'IDO'
 dados_imo = dados_grafico.groupby('mes_ano').apply(get_imo).reset_index()
 dados_imo['Métrica'] = 'IMO'
 
 # Create figure with secondary y-axis
 fig = make_subplots(specs=[[{"secondary_y": True}]])
 
 # Add traces
 fig.add_trace(
     go.Scatter(x=dados_ipo['mes_ano'].astype(str), y=dados_ipo[0], name="IPO"),
     secondary_y=False,
 )
 
 fig.add_trace(
     go.Scatter(x=dados_ido['mes_ano'].astype(str), y=dados_ido[0], name="IDO"),
     secondary_y=True,
 )
 
 fig.add_trace(
     go.Scatter(x=dados_imo['mes_ano'].astype(str), y=dados_imo[0], name="IMO"),
     secondary_y=True,
 )
 
 # Add figure title
 fig.update_layout(
     title_text=f"Série Histórica de IDO, IPO, IMO - {municipio}"
 )
 
 # Set x-axis title
 fig.update_xaxes(title_text="Data", tickangle=-90)
 
 # Set y-axes titles
 fig.update_yaxes(title_text="IPO", secondary_y=False, tickformat=".2%", range=[0, 1])
 fig.update_yaxes(title_text="IDO - IMO", secondary_y=True, range=[0, 200])
 
 #Criação do mapa
 #definição das cores
 if municipio != 'Todos': 
  dados_mapa_geral['cor'] = pd.cut(dados_mapa_geral['eggs'], bins=[-1,0,50,100,200,10000], labels=[ 'lightgray',#zero
                                                                                                      'limegreen', # 1 a 50
                                                                                                      'gold', #50 a 100
                                                                                                      'orange', #100 a 200
                                                                                                      'red' #mais de 200
                                                                                                         ])

  dados_mapa_geral = dados_mapa_geral[dados_mapa_geral['cor'].isin(lista_filtro_faixa)]
  attr = ('Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community')
  tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
  #token = 'pk.eyJ1IjoiYW5kcmUtamFyZW5rb3ciLCJhIjoiY2xkdzZ2eDdxMDRmMzN1bnV6MnlpNnNweSJ9.4_9fi6bcTxgy5mGaTmE4Pw'
  #mapbox_tile_URL = f"https://api.mapbox.com/styles/v1/mapbox/satellite-streets-v11/tiles/{{z}}/{{x}}/{{y}}@2x?access_token={token}"
  
  m = folium.Map(location=[dados_mapa_geral[dados_mapa_geral[coluna_selecionada]==regiao_saude].latitude.mean(), dados_mapa_geral[dados_mapa_geral[coluna_selecionada]==regiao_saude].longitude.mean()],
                 zoom_start=13,
                 tiles=tiles,
                 attr=attr,
                 )
  
  folium.GeoJson('https://raw.githubusercontent.com/andrejarenkow/geodata/main/municipios_rs_CRS/RS_Municipios_2021.json',
      style_function=lambda feature: {
          "fillColor": "rgba(0,0,0,0)",
          "color": "white",
          "weight": 0.5,
      },).add_to(m)
  
  for linha in dados_mapa_geral.itertuples():
  
      ovi_chart = dados[(dados['municipality']==linha.municipality)&(dados['ovitrap_id']==linha.ovitrap_id)]
  
      scatter = (
        Chart(ovi_chart, width=200, height=100, title='Histórico')
        .mark_bar()
        .encode(
          x=dict(field="week_year", title='Semana Epidemiológica'),
          y=dict(field="eggs", title='Quantidade Ovos', type='quantitative')))
      label_grafico = scatter.mark_text(align='center', baseline='bottom').encode(text='eggs')
      vega_lite = folium.VegaLite(
        (scatter+label_grafico),
        width='100%',
        height='100%',
        )
      
        #popup = folium.Popup()
      marker = folium.Circle(
          location=[linha.latitude, linha.longitude],
          popup = folium.Popup().add_child(vega_lite),
          tooltip= 'Armadilha %s - Ovos %s' % (linha.ovitrap_id, linha.eggs),
          radius=150,
          color=linha.cor,
          fill=True,
          fill_color=linha.cor
                      )
        
        #vega_lite.add_to(popup)
        #popup.add_to(marker)
      marker.add_to(m)
  
  
  with metricas:
   tab0, tab1, tab2 = st.tabs(['Mapa de positividade','Mapa de intensidade','Mapa de calor'])

   with tab0:
    st.subheader('Mapa de positividade')
    dados_mapa_geral['positividade'] = dados_mapa_geral['eggs'].apply(lambda x: 'positivo' if x > 0 else 'negativo')
    map_plotly_fig_positividade = px.scatter_mapbox(dados_mapa_geral, lat="latitude", lon="longitude", mapbox_style="open-street-map", color='positividade',
                    zoom=11,color_discrete_sequence=["gold",'red'],category_orders = {'positividade':['negativo','positivo']}, height=600, size_max=500, center=dict(lat=dados_mapa_geral['latitude'].mean(), lon= dados_mapa_geral['longitude'].mean()))
    map_plotly_fig_positividade.update_layout( margin=go.layout.Margin(l=10, r=10, t=10, b=10),paper_bgcolor='rgba(0,0,0,0)',
                               mapbox_accesstoken= 'pk.eyJ1IjoiYW5kcmUtamFyZW5rb3ciLCJhIjoiY2xkdzZ2eDdxMDRmMzN1bnV6MnlpNnNweSJ9.4_9fi6bcTxgy5mGaTmE4Pw',
                              )
    map_plotly_fig_positividade.update_traces(marker={"size": 20, 'opacity':0.8})
 
    st.plotly_chart(map_plotly_fig_positividade, use_container_width=True)
   
   with tab1:
     # call to render Folium map in Streamlit
     st.subheader('Mapa de intensidade')
     st_data = folium_static(m, height=600)
  
   with tab2:
     st.subheader('Mapa de calor')
     map_plotly_fig_calor = px.density_mapbox(dados_mapa_geral, lat="latitude", lon="longitude", z="eggs", mapbox_style="open-street-map",
                    color_continuous_scale='Reds', zoom=13, center=dict(lat=dados_mapa_geral['latitude'].mean(), lon=dados_mapa_geral['longitude'].mean()), height=600, radius=75)
     map_plotly_fig_calor.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
                                  margin=go.layout.Margin(l=10, r=10, t=10, b=10),
                                #mapbox_accesstoken= 'pk.eyJ1IjoiYW5kcmUtamFyZW5rb3ciLCJhIjoiY2xkdzZ2eDdxMDRmMzN1bnV6MnlpNnNweSJ9.4_9fi6bcTxgy5mGaTmE4Pw',
                               )
  
     st.plotly_chart(map_plotly_fig_calor, use_container_width=True)
    
 
 else:
  if regiao_saude =='Todas':
   dados_mapa_geral = dados_mapa_geral

  else:
   dados_mapa_geral = dados_mapa_geral[dados_mapa_geral[coluna_selecionada]==regiao_saude]
   
  dados_mapa_todos = pd.pivot_table(dados_mapa_geral, index=['latitude','longitude','municipality', 'ovitrap_id'],values='eggs', aggfunc='mean').reset_index()
  dados_mapa_todos = dados_mapa_todos.rename(columns={'municipality':'Município', 'ovitrap_id':'Nº da Ovitrampa'})
    # Supondo que 'dados' seja o seu DataFrame e 'latitude' seja a coluna com as coordenadas
  # Defina os limites da faixa de latitude do Rio Grande do Sul
  limite_inferior = -33.75
  limite_superior = -27.0
  
  # Filtrar o DataFrame para manter apenas as linhas dentro da faixa de latitude desejada
  dados_filtrados = dados_mapa_todos[(dados_mapa_todos['latitude'] >= limite_inferior) & (dados_mapa_todos['latitude'] <= limite_superior)]
  
  # Exibir o DataFrame filtrado
  dados_mapa_todos_mapa = dados_filtrados.drop_duplicates(subset=['latitude','longitude','Município'])
 
  with metricas:
   # call to render Folium map in Streamlit
   tab1, tab2 = st.tabs(['Mapa com pontos','Mapa de calor'])
   with tab1:
    st.write('Mapa com pontos de todo estado do RS')
    map_plotly_fig_calor = px.scatter_mapbox(dados_mapa_todos_mapa, lat="latitude", lon="longitude", mapbox_style="open-street-map", 
                    zoom=5, center=dict(lat=-30.456877333125696, lon= -53.01906610604057), height=600, size_max=500, hover_name='Município', hover_data='Nº da Ovitrampa')

    map_plotly_fig_calor.update_layout( margin=go.layout.Margin(l=10, r=10, t=10, b=10),paper_bgcolor='rgba(0,0,0,0)',
                               mapbox_accesstoken= 'pk.eyJ1IjoiYW5kcmUtamFyZW5rb3ciLCJhIjoiY2xkdzZ2eDdxMDRmMzN1bnV6MnlpNnNweSJ9.4_9fi6bcTxgy5mGaTmE4Pw',
                              )
 
    st.plotly_chart(map_plotly_fig_calor, use_container_width=True)
    
    
   with tab2:
    
    st.write('Mapa de calor de todo estado do RS')
    map_plotly_fig = px.density_mapbox(dados_mapa_todos, lat="latitude", lon="longitude", mapbox_style="satellite-streets", #z="eggs",
                   color_continuous_scale='Reds', zoom=5, center=dict(lat=-30.456877333125696, lon= -53.01906610604057), height=600, radius=20)
 
    map_plotly_fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',margin=go.layout.Margin(l=10, r=10, t=10, b=10),
                               mapbox_accesstoken= 'pk.eyJ1IjoiYW5kcmUtamFyZW5rb3ciLCJhIjoiY2xkdzZ2eDdxMDRmMzN1bnV6MnlpNnNweSJ9.4_9fi6bcTxgy5mGaTmE4Pw',
                              )
    st.plotly_chart(map_plotly_fig, use_container_width=True)
  
 #tabela com as ovitrampas
 with filtros:
  dados_ovitrampas_municipio = pd.pivot_table(dados_grafico, index='ovitrap_id', columns='week_year', values='eggs', aggfunc='sum').fillna('-')
  dados_ovitrampas_municipio.index.names = ['Nº Ovitr']
  #st.dataframe(dados_ovitrampas_municipio, height=300, use_container_width=False,)
 
  # Plot!
  st.plotly_chart(fig, use_container_width=True)
  with st.expander('Explicação sobre as métricas'):
 
    st.latex(r'''
     Índice\:de\:Densidade\:de\:Ovos\:(IDO) =  \frac{Nº\:de\:ovos}{Nº\:de\:armadilhas\:positivas}
     ''')
    st.divider()
    st.latex(r'''
     Índice\:de\:Positividade\:de\:Ovitrampas\:(IPO) =  \frac{Nº\:de\:armadilhas\:positivas\times 100}{Nº\:de\:armadilhas\:examinadas}
     ''')
    st.divider()
    st.latex(r'''
     Índice\:Médio\:de\:Ovos\:(IMO) =  \frac{Nº\:de\:ovos}{Nº\:de\:armadilhas\:examinadas}
     ''')
    def limpar_cache():
     st.cache_data.clear()
     
    st.button('Atualizar', on_click=limpar_cache )
    
 
 
 with novas_metricas:
  if regiao_saude == 'Todas':
   st.metric(f'Municípios com ovitrampas em {ano}', value = len(dados_mapa_geral['municipality'].dropna().unique()))
   #st.metric('Municípios com ovitrampas no mês', value = len(dados[(dados['week']==semana_epidemiologica)&(dados['year']==ano)]['municipality'].unique()))
   st.metric(f'Ovitrampas inspecionadas em {ano}', value = dados_mapa_geral['ovitrap_id'].count())
   st.metric(f'Total de ovos coletados em {ano}', value = dados_mapa_geral['eggs'].sum())
   st.metric(f'IPO - Índice de Positividade de Ovos em {ano}', value = str((get_ipo(dados_mapa_geral)*100).round(1))+'%')  
   st.metric(f'IDO - Índice de Densidade de Ovos em {ano}', value = (get_ido(dados_mapa_geral)).round(1))   
   st.metric(f'IMO - Índice de Média de Ovos em {ano}', value = (get_imo(dados_mapa_geral)).round(1))

  else:
   st.metric(f'Municípios com ovitrampas na {regiao_saude}', value = len(dados[(dados[coluna_selecionada]==regiao_saude)&(dados['year']==ano)]['municipality'].unique()))
   st.metric('Ovitrampas inspecionadas', value = dados_mapa_geral[dados_mapa_geral[coluna_selecionada]==regiao_saude]['ovitrap_id'].count())
   st.metric('Total de ovos coletados', value = dados_mapa_geral[dados_mapa_geral[coluna_selecionada]==regiao_saude]['eggs'].sum())
   st.metric('IPO - Índice de Positividade de Ovos', value = str((get_ipo(dados_mapa_geral[dados_mapa_geral[coluna_selecionada]==regiao_saude])*100).round(1))+'%')  
   st.metric('IDO - Índice de Densidade de Ovos', value = (get_ido(dados_mapa_geral[dados_mapa_geral[coluna_selecionada]==regiao_saude])).round(1))   
   st.metric('IMO - Índice de Média de Ovos', value = (get_imo(dados_mapa_geral[dados_mapa_geral[coluna_selecionada]==regiao_saude])).round(1))

with aba_sobre:
 st.header('O que são as ovitrampas?')
 coluna_texto, coluna_imagens = st.columns([2,3])
 with coluna_texto:
  st.markdown(
   """
 As ovitrampas são armadilhas que simulam um criadouro de Aedes aegypti utilizadas para detectar a presença e abundância do vetor por meio dos ovos depositados na mesma. 
 Consiste em um pote escuro com uma palheta de madeira (Eucatex®) presa na parede lateral com um clipe metálico. 
 Se adiciona 300 ml de água para atrair as fêmeas de Aedes spp. para realizar a postura dos ovos.  
 Se utiliza levedura de cerveja como atrativo, adicionado na água na concentração de 0,04%, para aumentar a atração das fêmeas de Aedes spp.
 
 
 A partir delas, pode-se calcular a densidade da população do mosquito naquele município e quais os locais de maior proliferação. 
 Com isso, a gestão pode providenciar outras estratégias mecânicas de combate à dengue, como mutirões de limpeza, educação em saúde, entre outras.
 
 
 Cada município irá instalar entre 50 a 100 armadilhas, que consiste em um vaso de planta sem furo e uma palheta de eucatex,
 onde é colocado levedo de cerveja afim de atrair a fêmea do mosquito a depositar os ovos no local. 
 A equipe retorna em cinco dias para recolher a armadilha e levá-la ao laboratório para fazer a contagem dos ovos.
   """
  )

with coluna_imagens:
 col1, col2 = st.columns(2)
 col1.image('WhatsApp Image 2023-10-02 at 14.27.35.jpeg', width=350, caption='Ovos de Aedes aegypti na palheta')
 col2.image('fiocruz_20210512_mauro_campello_00029 (2).jpg', width=350, caption='Ilustração digital de ovos de Aedes aegypti - Imagem Fundação Oswaldo Cruz')
 col1.image('fiocruz_20180220_raquel_portugal_01096.jpg', width=350, caption='Preparação de armadilha - Imagem Fundação Oswaldo Cruz')
 
 
with aba_referencias:
 col1, col2, col3 = st.columns([1,1,1])
 col2.write('Contagem de ovos de Aedes aegypti em ovitrampas')
 col2.video('https://www.youtube.com/watch?v=8OCSZHd47Zs')
 col3.write('Metodologia para coleta de ovos Aedes aegypti')
 col3.video('https://www.youtube.com/watch?v=aWBtdSYdXVQ')

 with col1:
  st.markdown(
"""
   * [01 - Roteiro de Adesão Ovitrampas](https://drive.google.com/file/d/1JeLoIqQExsm7LajeAJ5zlnUdOv1N_do9/view?usp=sharing)
   * [02 - POP Ovitrampas](https://drive.google.com/file/d/15IsJnLWiyeaNkqUG7L4r3LjUQb8TxR8W/view?usp=drive_link)
   * [03 - Nota Técnica MS nº 33-2022 - Ovitrampas](https://drive.google.com/file/d/1_NeaWP3a4XqA0jYBlW1z9P2FGKAVD_Em/view?usp=sharing)
   * [04 - Modelo do termo de Adesão às Ovitrampas - Prefeituras](https://drive.google.com/file/d/1wniRUgRlwBeT-hVoqGXUXLvNAo9GCWVC/view?usp=sharing)
   * [05 - Termo de Autorização - Moradores](https://drive.google.com/file/d/1p2fKbsDG-FHYloo4pR4B65ZAFvMYYvLy/view?usp=sharing)
   * [06 - Manual_Ovitrampas_Fiocruz](https://drive.google.com/file/d/1LqkQPCCUGuwi7YM9zKqRhXoy77f19veN/view?usp=sharing)
   * [07 - Conta Ovos - Manual](https://drive.google.com/file/d/1CSNd0Xpjv6Weix4NZMJsOtuGrBfQqcPa/view?usp=sharing)
   * [08 - MODELO Etiquetas OVITRAMPAS](https://drive.google.com/file/d/1m1ciA_M0xouSx0X846JFgYktaAYgDXpT/view?usp=sharing)
   * [09 - Boletim Ovitrampas RS](https://drive.google.com/file/d/1aAcGfRSPi3RJkeAs7SghQxrAgeSHeo2k/view?usp=sharing)
   * [10 - Grade contagem ovos](https://drive.google.com/file/d/14iD9gBY8GTyPtIxLbSNv_LKMM5Hl_usM/view?usp=sharing)
   * [11 - Tutorial Aplicativo Minhas Coordenadas](https://drive.google.com/file/d/1a-YXzQw0KepQtXZoDt5L9PR4b6JvDlWv/view?usp=sharing)
"""   
  )
 
with aba_analise:

 #Tabela de mapa de calor, de IDO por semana epidemiológica (ou mês)
 coluna='mes_ano'
 dados_ipo = dados.groupby([coluna, 'municipality']).apply(get_ipo).reset_index()
 dados_ipo.columns=[coluna, 'municipality', 'IPO']
 dados_ipo['IPO'] = dados_ipo['IPO']*100
 tabela_final = dados_ipo.pivot(index='municipality', columns=coluna, values='IPO')
 altura_heatmap_dinamica = len(tabela_final)*20
 tab_heatmap = px.imshow(tabela_final, aspect="auto", title='Índice de Positividade de Ovitrampas ao longo do tempo',
                         color_continuous_scale='Reds',
                         height=altura_heatmap_dinamica, width=1000, text_auto=True,
                         labels=dict(x="Data",y="Município", color="IPO"))
 tab_heatmap.layout.coloraxis.showscale = False
 tab_heatmap.update_layout(
    xaxis_title='Mês/Ano',
    yaxis_title='Município'
)
 #Tabela de mapa de calor, de IDO por semana epidemiológica (ou mês)
 coluna='mes_ano'
 
 dados_ipo_regiao = dados.groupby([coluna, 'regiao_saude']).apply(get_ipo).reset_index()
 dados_ipo_regiao.columns=[coluna, 'regiao_saude', 'IPO']
 dados_ipo_regiao['IPO'] = dados_ipo_regiao['IPO']*100
 
 tabela_final_regiao_saude = dados_ipo_regiao.pivot(index='regiao_saude', columns=coluna, values='IPO')
 
 index_regiao_saude = pd.DataFrame(sorted(dados_municipios['Região_saude'].unique())).set_index(0)
 
 
 tabela_final_regiao_saude = index_regiao_saude.join(tabela_final_regiao_saude)

 tab_heatmap_regiao_saude = px.imshow(tabela_final_regiao_saude, aspect="auto", title='Índice de Positividade de Ovitrampas ao longo do tempo',
                          color_continuous_scale='Reds',
                          height=1200, width=1000, text_auto=True,
                          labels=dict(x="Data",y="Região de Saúde", color="IPO"))
 tab_heatmap_regiao_saude.layout.coloraxis.showscale = False
 tab_heatmap_regiao_saude.update_layout(
     xaxis_title='Mês/Ano',
     yaxis_title='Região de Saúde'
 )
 
#Gráfico com médias e desviosa padrões
 dados_medidas_ipo = pd.pivot_table(dados_ipo, index='mes_ano', values='IPO', aggfunc=['mean','std','median']).droplevel(1, axis=1).reset_index()
 
 fig_medidas = go.Figure()
 
 fig_medidas.add_trace(go.Scatter(
         name='Measurement',
         x=dados_medidas_ipo['mes_ano'],
         y=dados_medidas_ipo['mean'],
         mode='lines+markers',
         line=dict(color='rgb(31, 119, 180)'),
         showlegend=False
     ))
 
 
 fig_medidas.add_trace(go.Scatter(
         name='Upper Bound',
         x=dados_medidas_ipo['mes_ano'],
         y=dados_medidas_ipo['mean']+dados_medidas_ipo['std'],
         mode='lines',
         marker=dict(color="#444"),
         line=dict(width=0),
         showlegend=False
     ))
 
 
 fig_medidas.add_trace(go.Scatter(
         name='Lower Bound',
         x=dados_medidas_ipo['mes_ano'],
         y=dados_medidas_ipo['mean']-dados_medidas_ipo['std'],
         marker=dict(color="#444"),
         line=dict(width=0),
         mode='lines',
         fillcolor='rgba(68, 68, 68, 0.3)',
         fill='tonexty',
         showlegend=False
     ))
 
 fig_medidas.add_trace(go.Scatter(
         x=dados_ipo['mes_ano'],
         y=dados_ipo['IPO'],
         mode='markers',
         text=dados_ipo['municipality'],
         marker_color='indianred',
         showlegend=False
     ))
 fig_medidas.update_layout(
     yaxis_title='IPO',
     title='Curva com média e desvio padrão',
     
 )

#Gráfico com médias e desviosa padrões
 #Tabela de mapa de calor, de IDO por semana epidemiológica (ou mês)

 dados_medidas_ipo_regioes = pd.pivot_table(dados_ipo_regiao, index='mes_ano', values='IPO', aggfunc=['mean','std','median']).droplevel(1, axis=1).reset_index()
 
 fig_medidas_regioes = go.Figure()
 
 fig_medidas_regioes.add_trace(go.Scatter(
         name='Measurement',
         x=dados_medidas_ipo_regioes['mes_ano'],
         y=dados_medidas_ipo_regioes['mean'],
         mode='lines+markers',
         line=dict(color='rgb(31, 119, 180)'),
         showlegend=False
     ))
 
 
 fig_medidas_regioes.add_trace(go.Scatter(
         name='Upper Bound',
         x=dados_medidas_ipo_regioes['mes_ano'],
         y=dados_medidas_ipo_regioes['mean']+dados_medidas_ipo_regioes['std'],
         mode='lines',
         marker=dict(color="#444"),
         line=dict(width=0),
         showlegend=False
     ))
 
 
 fig_medidas_regioes.add_trace(go.Scatter(
         name='Lower Bound',
         x=dados_medidas_ipo_regioes['mes_ano'],
         y=dados_medidas_ipo_regioes['mean']-dados_medidas_ipo_regioes['std'],
         marker=dict(color="#444"),
         line=dict(width=0),
         mode='lines',
         fillcolor='rgba(68, 68, 68, 0.3)',
         fill='tonexty',
         showlegend=False
     ))
 
 fig_medidas_regioes.add_trace(go.Scatter(
         x=dados_ipo_regiao['mes_ano'],
         y=dados_ipo_regiao['IPO'],
         mode='markers',
         text=dados_ipo_regiao['regiao_saude'],
         marker_color='indianred',
         showlegend=False
     ))
 fig_medidas_regioes.update_layout(
     yaxis_title='IPO',
     title='Curva com média e desvio padrão',
     
 )
 #Criando uma tabela para identificar os municípios acima, em cada mês
 #contar quantas vezes o município ficou fora da curva durante todo o período
 
 dados_ipo_comparativo = pd.DataFrame()
 
 for i in sorted(dados_ipo['mes_ano'].unique())[-4:]:
   dados_ipo_mes = dados_ipo[dados_ipo['mes_ano'] == i].reset_index(drop=True)
   dados_ipo_mes['comparativo_curva'] = dados_ipo_mes['IPO']>(dados_ipo_mes['IPO'].mean()+dados_ipo_mes['IPO'].std())
   dados_ipo_mes = dados_ipo_mes[dados_ipo_mes['comparativo_curva']>0]
   dados_ipo_comparativo = pd.concat([dados_ipo_comparativo ,dados_ipo_mes])
 
 dados_ipo_comparativo = pd.pivot_table(dados_ipo_comparativo, index='municipality', values='comparativo_curva', aggfunc='sum').sort_values('comparativo_curva', ascending=False)
 dados_ipo_comparativo['porcentagem_de_vezes_acima'] = round((dados_ipo_comparativo['comparativo_curva']/4)*100, 1)
 
  # Encontrando os municípios que ficaram acima da média
 municipios_acima_media = dados_ipo_comparativo[dados_ipo_comparativo['comparativo_curva'] > 0]
 
 
 # Gerando a mensagem
 if not municipios_acima_media.empty:
     mensagem = ", ".join(f"{municipio} ({comparativo['comparativo_curva'].astype(int)})" for municipio, comparativo in municipios_acima_media.iterrows())
     mensagem = f"Ficaram mais de um desvio padrão acima da média, nos últimos 4 meses, os municípios {mensagem} "
 else:
     mensagem = "Nenhum município ficou acima da média nos últimos 4 meses."

#Criando uma tabela para identificar as regioes acima, em cada mês
 #contar quantas vezes o município ficou fora da curva durante todo o período
 
 dados_ipo_comparativo_regioes = pd.DataFrame()
 
 for i in sorted(dados_ipo_regiao['mes_ano'].unique())[-4:]:
   dados_ipo_mes_regiao = dados_ipo_regiao[dados_ipo_regiao['mes_ano'] == i].reset_index(drop=True)
   dados_ipo_mes_regiao['comparativo_curva'] = dados_ipo_mes_regiao['IPO']>(dados_ipo_mes_regiao['IPO'].mean()+dados_ipo_mes_regiao['IPO'].std())
   dados_ipo_mes_regiao = dados_ipo_mes_regiao[dados_ipo_mes_regiao['comparativo_curva']>0]
   dados_ipo_comparativo_regioes = pd.concat([dados_ipo_comparativo_regioes ,dados_ipo_mes_regiao])
 
 dados_ipo_comparativo_regioes = pd.pivot_table(dados_ipo_comparativo_regioes, index='regiao_saude', values='comparativo_curva', aggfunc='sum').sort_values('comparativo_curva', ascending=False)
 dados_ipo_comparativo_regioes['porcentagem_de_vezes_acima'] = round((dados_ipo_comparativo_regioes['comparativo_curva']/4)*100, 1)
 
  # Encontrando os municípios que ficaram acima da média
 regioes_acima_media = dados_ipo_comparativo_regioes[dados_ipo_comparativo_regioes['comparativo_curva'] > 0]
 
 
 # Gerando a mensagem
 if not regioes_acima_media.empty:
     mensagem = ", ".join(f"{regiao} ({comparativo['comparativo_curva'].astype(int)})" for regiao, comparativo in regioes_acima_media.iterrows())
     mensagem = f"Ficaram mais de um desvio padrão acima da média, nos últimos 4 meses, as regioes {mensagem} "
 else:
     mensagem = "Nenhuma região ficou acima da média nos últimos 4 meses."
 
 tab_municipios, tab_regiao_saude = st.tabs(['Municipio', 'Região de Saúde'])

 with tab_municipios:
  col_analise_1, col_analise_2 = st.columns([1,1])

 with tab_regiao_saude:
  col_analise_3, col_analise_4 = st.columns([1,1])
  
 
 with col_analise_1:
   st.plotly_chart(tab_heatmap, use_container_width=True)

 with col_analise_2:
  st.plotly_chart(fig_medidas, use_container_width=True)
  texto = """
   Ao lado, é possível verificar uma tabela com o Índice de Positividade de Ovitrampas (IPO) para os municípios que possuem as armadilhas instaladas em seu território. 
   Verifica-se que os meses de inverno costumam ter índices menores do que nos meses mais quentes do ano.

   Acima, verifica-se uma curva com o IPO ao longo do tempo, onde a linha azul indica a média do índice para aquele mês no RS, as zonas sombreadas são a área equivalente a um desvio padrão,
   tanto para mais quanto para menos, e os pontos vermelhos são os valores pontuais de cada município. Passando o mouse por cima, é possível ver o nome do município que representa cada ponto.

  """
  st.markdown(texto)
  st.markdown(mensagem)

 with col_analise_3:
  st.plotly_chart(tab_heatmap_regiao_saude, use_container_width=True)
  
 with col_analise_4:
  st.plotly_chart(fig_medidas_regioes, use_container_width=True)
  texto = """
   Ao lado, é possível verificar uma tabela com o Índice de Positividade de Ovitrampas (IPO) para os municípios que possuem as armadilhas instaladas em seu território. 
   Verifica-se que os meses de inverno costumam ter índices menores do que nos meses mais quentes do ano.

   Acima, verifica-se uma curva com o IPO ao longo do tempo, onde a linha azul indica a média do índice para aquele mês no RS, as zonas sombreadas são a área equivalente a um desvio padrão,
   tanto para mais quanto para menos, e os pontos vermelhos são os valores pontuais de cada município. Passando o mouse por cima, é possível ver o nome do município que representa cada ponto.

  """
  st.markdown(texto)
  st.markdown(mensagem)

  




with aba_indicador:
 # Encontrando a primeira coluna com valor diferente de NaN
 def primeira_coluna_com_valor_diferente_de_nan(df):
     for col in df.columns:
         if df[col].notna().any():
             return col

 # função para indicador por municipio e por ano
 def valor_indicador(municipio, ano):
    try:
        # Filtro do município
        dados_municipio = df_periodo_todo[df_periodo_todo['municipality'] == municipio].set_index(['Macro','regiao_saude', 'crs', 'municipality'])
        
        # Aplicando função para achar o início do monitoramento
        inicio_monitoramento = primeira_coluna_com_valor_diferente_de_nan(dados_municipio)
        
        # Filtrando o DataFrame da coluna encontrada para frente
        dados_municipio = dados_municipio.loc[:, inicio_monitoramento:]
        
        # Filtrar colunas pelo ano (mais preciso)
        ano_colunas = [col for col in dados_municipio.columns if str(ano) == col.split('-')[-1] or str(ano) == col.split('/')[-1]]
        
        if not ano_colunas:
            return 0, 0, 0, 0  # Retorna valores padrão em vez de string
            
        dados_municipio = dados_municipio[ano_colunas]
        
        # Quantos meses não foram feitas coletas
        meses_sem_coleta = dados_municipio.isna().sum().sum()
        
        # Total de meses
        total_meses = len(dados_municipio.columns)
        
        # Meses com coleta
        meses_com_coleta = total_meses - meses_sem_coleta
        
        # Indicador
        indicador = round(meses_com_coleta / total_meses * 100, 1) if total_meses > 0 else 0
        
        return indicador, meses_sem_coleta, meses_com_coleta, total_meses
        
    except Exception as e:
        print(f"Erro ao calcular indicador: {e}")
        return 0, 0, 0, 0


 #st.subheader('Resultados da Pactuação - Indicador 9')
 col_filtros_indicador, col_indicadores = st.columns([1,4])

 def resultado_por_macro(macro, ano):
  # Criando função para somar os que atingiram a meta de a cordo com a Macro e ano escolhido
  df_macro = df_resultados[(df_resultados['macro'] == macro)&(df_resultados['ano'] == ano)].reset_index()

  # Filtrar apenas os valores booleanos (True/False) e ignorar os valores de string
  df_booleanos = df_macro[df_macro['meta_atingida'].apply(lambda x: isinstance(x, bool))]

  # Somar os valores booleanos, onde True é tratado como 1 e False como 0
  soma_meta_atingida = df_booleanos['meta_atingida'].sum()

  return soma_meta_atingida

def resultado_por_regiao_saude(regiao_saude, ano):
  # Criando função para somar os que atingiram a meta de a cordo com a Macro e ano escolhido
  df_regiao_saude = df_resultados[(df_resultados['regiao_saude'] == regiao_saude)&(df_resultados['ano'] == ano)].reset_index()

  # Filtrar apenas os valores booleanos (True/False) e ignorar os valores de string
  df_booleanos = df_regiao_saude[df_regiao_saude['meta_atingida'].apply(lambda x: isinstance(x, bool))]

  # Somar os valores booleanos, onde True é tratado como 1 e False como 0
  soma_meta_atingida = df_booleanos['meta_atingida'].sum()

  return soma_meta_atingida

def resultado_por_crs(crs, ano):
  # Criando função para somar os que atingiram a meta de a cordo com a Macro e ano escolhido
  df_crs = df_resultados[(df_resultados['crs'] == crs)&(df_resultados['ano'] == ano)].reset_index()

  # Filtrar apenas os valores booleanos (True/False) e ignorar os valores de string
  df_booleanos = df_crs[df_crs['meta_atingida'].apply(lambda x: isinstance(x, bool))]

  # Somar os valores booleanos, onde True é tratado como 1 e False como 0
  soma_meta_atingida = df_booleanos['meta_atingida'].sum()

  return soma_meta_atingida

def resultado_por_municipio(municipio, ano):
  # Criando função para somar os que atingiram a meta de a cordo com a Macro e ano escolhido
  df_municipio = df_resultados[(df_resultados['municipio'] == municipio)&(df_resultados['ano'] == ano)].reset_index()
  resultado_municipio = df_municipio['indicador'].values[0]

  return resultado_municipio
  

#df_periodo_todo = pd.read_excel('https://drive.google.com/uc?export=download&id=1BcxH8L2NxlAJPyFW7o6Qcj3wvKpOZSvB')

#Seleção do ano
with col_filtros_indicador:
 ano_indicador = st.selectbox('Selecione o ano', options=sorted(df_resultados[~df_resultados['ano'].isin([2022,2023])]['ano'].unique()), index = 1)

 df_resultados_ano_filtrado = df_resultados[df_resultados['ano']==ano_indicador].reset_index(drop=True)
 df_resultados_ano_crs_filtrado = df_resultados_ano_filtrado.reset_index(drop=True)
 
 # Seleção da Macro
 #macro_indicador = st.selectbox('Selecione a Macro', options=sorted(df_resultados_ano_crs_filtrado['macro'].unique()))
 # Seleção da Região de saúde
 #regiao_de_saude_indicador = st.selectbox('Selecione a Região de Saúde', options=sorted(df_resultados_ano_crs_filtrado['regiao_saude'].unique()))
 #Seleção da CRS
 #crs_indicador = st.selectbox('Selecione a CRS', options=sorted(df_resultados_ano_filtrado['crs'].unique()))

# Seleção de município
 municipio_indicador = st.selectbox('Selecione o município', options=sorted(df_resultados_ano_filtrado['municipio'].unique()))

# Métricas
with col_indicadores:
 col1, col2, col3 = st.columns(3)
 # Metricas estaduais
 #col1.subheader('')
 #col2.subheader('Resultados da Pactuação Estadual')
 #col3.subheader('')
 #col1.metric(f'Resultado da Macro {macro_indicador}',resultado_por_macro(macro_indicador, ano_indicador))
 #col2.metric(f'Resultado da {regiao_de_saude_indicador}',resultado_por_regiao_saude(regiao_de_saude_indicador, ano_indicador))
 #col3.metric(f'Resultado da {crs_indicador}ª CRS',resultado_por_crs(crs_indicador, ano_indicador))
 #st.divider()

 col1, col2, col3 = st.columns(3)
 col2.subheader('Resultados da Pactuação Municipal')
 # Metricas municipais
 col2.metric(f'Indicador municipal - {municipio_indicador}', f'{resultado_por_municipio(municipio_indicador, ano_indicador)} %')
 df_municipio = df_periodo_todo[df_periodo_todo['municipality']==municipio_indicador].set_index('municipality').drop(['Macro','regiao_saude','crs'], axis=1).replace({'X':1}).fillna(0)
 # Filtrar colunas pelo ano
 ano_colunas = [col for col in df_municipio.columns if f'{ano_indicador}' in col]
 df_municipio = df_municipio[ano_colunas]

 heat_map = px.imshow(df_municipio, aspect="auto", 
                      color_continuous_scale='Greens',
                      text_auto=True,
                      height=200,
                      labels=dict(x="Data",y="Região de Saúde", color="IPO"))
 heat_map.layout.coloraxis.showscale = False
 heat_map.update_layout(
     xaxis_title='Mês/Ano',
     yaxis_title='Município'
 )
 st.plotly_chart(heat_map)

 ano_selecionado = ano_indicador
 
 # Inicializa o dicionário para armazenar os resultados
 resultados = {}
 
 # Loop para preencher o dicionário
 for regiao in resultados_por_regiao_ano.keys():
     resultados[regiao] = {}
     try:
         resultados[regiao][ano_selecionado] = resultado_por_regiao_saude(regiao, ano_selecionado)
         if resultados[regiao][ano_selecionado] == True:
             resultados[regiao][ano_selecionado] = 1
         if resultados[regiao][ano_selecionado] == False:
             resultados[regiao][ano_selecionado] = 0
     except:
         resultados[regiao][ano_selecionado] = 0
 
 # Converte o dicionário em um DataFrame
 df_regiao = pd.DataFrame(resultados).T
 
 # Adiciona a coluna de valor da meta e a porcentagem de atingimento
 meta_coluna = f'Meta {ano_selecionado}'
 porcentagem_coluna = f'Resultado em {ano_selecionado} (%)'
 
 df_regiao[meta_coluna] = df_regiao.index.map(lambda regiao: resultados_por_regiao_ano.get(regiao, {}).get(ano_selecionado, 0))
 df_regiao[porcentagem_coluna] = df_regiao.apply(
     lambda row: (row[ano_selecionado] / row[meta_coluna] * 100) if row[meta_coluna] > 0 else 0, axis=1
 )
 
 #arredondar com uma casa depois da virgula a coluna do atingimento da meta
 df_regiao[porcentagem_coluna] = df_regiao[porcentagem_coluna].round(1)

 # Renomeando o índice
 df_regiao.index.name = 'Região de Saúde'
 
 

 # Inicializa o dicionário para armazenar os resultados
 resultados = {}
 
 # Loop para preencher o dicionário
 for regiao in macros.keys():
     resultados[regiao] = {}
     try:
         resultados[regiao][ano_selecionado] = resultado_por_macro(regiao, ano_selecionado)
         if resultados[regiao][ano_selecionado] == True:
             resultados[regiao][ano_selecionado] = 1
         if resultados[regiao][ano_selecionado] == False:
             resultados[regiao][ano_selecionado] = 0
     except:
         resultados[regiao][ano_selecionado] = 0
 
 # Converte o dicionário em um DataFrame
 df_macro = pd.DataFrame(resultados).T
 
 # Adiciona a coluna de valor da meta e a porcentagem de atingimento
 meta_coluna = f'Meta {ano_selecionado}'
 porcentagem_coluna = f'Resultado em {ano_selecionado} (%)'
 
 df_macro[meta_coluna] = df_macro.index.map(lambda regiao: macros.get(regiao, {}).get(ano_selecionado, 0))
 df_macro[porcentagem_coluna] = df_macro.apply(
     lambda row: (row[ano_selecionado] / row[meta_coluna] * 100) if row[meta_coluna] > 0 else 0, axis=1
 )
 
 #arredondar com uma casa depois da virgula a coluna do atingimento da meta
 df_macro[porcentagem_coluna] = df_macro[porcentagem_coluna].round(1)
 new_row = pd.DataFrame([[df_macro[ano_selecionado].sum(), df_macro[meta_coluna].sum(), 100*df_macro[ano_selecionado].sum() / df_macro[meta_coluna].sum()]], columns=df_macro.columns, index=['Total'])
 df_macro = pd.concat([df_macro, new_row])
 df_macro.index.name = 'Macrorregião de Saúde'


 # função para criar tabela de resultado por municipio
 dados_municipais = pd.DataFrame()
 ano = ano_selecionado
 
 for i in df_periodo_todo['municipality'].unique():
   dados_municipio_indicador_municipal = pd.DataFrame([valor_indicador(i, ano)], columns = ['Indicador', 'Meses_sem_coleta', 'Meses_com_coleta','Total_meses'])
   dados_municipio_indicador_municipal['Municipio'] = i
   dados_municipais = pd.concat([dados_municipais, dados_municipio_indicador_municipal])
 
 dados_municipais = dados_municipais.set_index('Municipio')[['Meses_com_coleta','Total_meses', 'Indicador']]
 
with aba_indicador:
  # divisão para ver tudo
 col_regiao, col_macro, col_municipio = st.columns(3)
 col_regiao.dataframe(df_regiao, height=1090,
                      column_config={
             porcentagem_coluna: st.column_config.ProgressColumn(
             porcentagem_coluna,
             format="%.1f",
             min_value=0,
             max_value=100,
         ),
     })
 col_macro.dataframe(df_macro,
                     column_config={
             porcentagem_coluna: st.column_config.ProgressColumn(
             porcentagem_coluna,
             format="%.1f",
             min_value=0,
             max_value=100,
         ),
     })
 col_municipio.dataframe(dados_municipais, height=1100,
                      column_config={
             'Indicador': st.column_config.ProgressColumn(
             'Indicador',
             format="%.1f",
             min_value=0,
             max_value=100,
         ),
     })

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
