# Importação das bibliotecas
import pandas as pd
import requests
import streamlit as st
# Não precisamos mais do módulo 'locale' se fizermos o mapeamento manual
# import locale

# --- Mapeamento Manual de Meses para Português ---
meses_ingles_para_portugues = {
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
# --- Fim do Mapeamento ---


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

#IDO - Índice Densidade de Ovos
def get_ido(df):
    ido = round(df[df['eggs']>0]['eggs'].mean(),1)

    return ido
#IPO - Índice de Positividade de Ovos
def get_ipo(df):
    ipo = ((df['eggs']>0).sum()/len(df)).round(3)*100

    return ipo

#IMO - Índice Médio de Ovos
def get_imo(df):
    imo = round(df['eggs'].mean(),1)

    return imo

# colocar um input com o municipio
municipality = st.text_input(label="Digite o nome do município: ", value="Aceguá")
# Receber input do ano
ano_escolhido = st.text_input("Digite o ano desejado (ex: 2025): ")

processar = st.button("Processar")
if processar:

    df = get_last_counting_public(municipality)
    # Supondo que seu DataFrame se chame df
    df['date'] = pd.to_datetime(df['date'])

    # Criar a coluna do mês (o nome ainda virá em inglês primeiro)
    df['month'] = df['date'].dt.strftime('%B')

    # --- Aplicar o mapeamento para traduzir os nomes dos meses ---
    df['month'] = df['month'].map(meses_ingles_para_portugues)
    # --- Fim da Aplicação do Mapeamento ---

    # Filtrar o DataFrame pelo ano selecionado
    df_filtrado = df[df['year'] == int(ano_escolhido)]

    # Agrupar pelos campos desejados e calcular as agregações
    # Certifique-se de que 'month' seja uma categoria ordenada se a ordem dos meses importar
    # Para garantir a ordem correta, podemos criar uma categoria:
    meses_ordenados = list(meses_ingles_para_portugues.values())
    df_filtrado['month'] = pd.Categorical(df_filtrado['month'], categories=meses_ordenados, ordered=True)

    resumo = df_filtrado.groupby(['week', 'month']).agg(
        armadilhas_instaladas=('ovitrap_id', 'count'),
        total_ovos=('eggs', 'sum')
    ).reset_index()

    dados_ipo = df_filtrado.groupby('week').apply(get_ipo).reset_index()
    dados_ipo.columns = ['week', 'ipo']
    dados_ido = df_filtrado.groupby('week').apply(get_ido).reset_index()
    dados_ido.columns = ['week', 'ido']
    dados_imo = df_filtrado.groupby('week').apply(get_imo).reset_index()
    dados_imo.columns = ['week', 'imo']

    resumo = pd.merge(resumo, dados_ipo, on='week', how='left')
    resumo = pd.merge(resumo, dados_ido, on='week', how='left')
    resumo = pd.merge(resumo, dados_imo, on='week', how='left')

    # Exibir o resultado
    resumo.columns = ['Semana Epidemiológica', 'Ciclo (Mês)', 'Armadilhas Instaladas', 'Total de Ovos', 'IPO', 'IDO', 'IMO']
    resumo
