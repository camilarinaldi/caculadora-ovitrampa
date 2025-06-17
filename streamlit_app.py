# Importação das bibliotecas
import pandas as pd
import requests

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

# colocar um input com o municipio
municipality = st.text_input(label="Digite o nome do município: ")

get_last_counting_public(municipality)
