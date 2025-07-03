# Importação das bibliotecas
import pandas as pd
import requests
import streamlit as st
from datetime import datetime

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
municipality = st.text_input(label="Digite o nome do município: ", value="Aceguá")
ano_escolhido = st.text_input("Digite o ano desejado (ex: 2025):")
processar = st.button("Processar")

if processar:
    df = get_last_counting_public(municipality)
    
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



##################################################################

    # Gerar lista de meses em português na ordem correta
    meses_ordem = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                   'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    
    # Identificar o primeiro mês com dados
    meses_com_dado = df_filtrado['month'].unique().tolist()
    meses_com_dado = [m for m in meses_ordem if m in meses_com_dado]
    
    # Mês e ano atual
    data_atual = datetime.now()
    ano_atual = data_atual.year
    mes_atual = data_atual.month
    
    # Criar dicionário com cores
    mapa_celulas = {}
    for idx, mes_nome in enumerate(meses_ordem, start=1):
        if int(ano_escolhido) > ano_atual:
            cor = 'gray'  # ano futuro: todos os meses são futuros
        elif int(ano_escolhido) == ano_atual and idx > mes_atual:
            cor = 'gray'  # meses futuros no mesmo ano
        elif mes_nome in meses_com_dado:
            total_mes = df_filtrado[df_filtrado['month'] == mes_nome]['eggs'].sum()
            if total_mes > 0:
                cor = 'green'
            else:
                cor = 'red'
        else:
            cor = 'white'
        mapa_celulas[mes_nome] = cor
    
    # Montar HTML da tabela
    html = "<table style='width:100%; text-align:center; border-collapse:collapse;'>"
    html += "<tr>" + "".join([f"<th style='border:1px solid black;'>{mes}</th>" for mes in meses_ordem]) + "</tr>"
    html += "<tr>" + "".join([f"<td style='background-color:{mapa_celulas[mes]}; border:1px solid black; height:40px;'></td>" for mes in meses_ordem]) + "</tr>"
    html += "</table>"
    
    # Exibir
    st.subheader("Mapa de Coletas no Ano Selecionado")
    st.markdown(html, unsafe_allow_html=True)
    
    # Legenda opcional
    st.markdown("""
    **Legenda:**  
    🟩 Coleta realizada  🟥 Sem coleta  ⬜ Ainda não monitorado  ⬛ Mês futuro
    """)

