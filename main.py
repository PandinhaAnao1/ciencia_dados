import streamlit as st
import pandas as pd


acidentes = pd.read_csv('./csv/acidentes_2022.csv')
localidades  = pd.read_csv('./csv/localidades_2022.csv')
tipo_veiculos = pd.read_csv('./csv/tipo_veiculo.csv')
vitimas = pd.read_csv('./csv/vitimas_2022.csv')

# Coletando os estados e plotando a side bar
estados_disponiveis = sorted(acidentes['uf_acidente'].unique()) 
estado_selecionado = st.sidebar.selectbox("Selecione o estado:", estados_disponiveis)

acidentes_filtrados = acidentes[acidentes['uf_acidente'] == estado_selecionado]
localidades_filtradas = localidades[localidades['uf'] == estado_selecionado]

df_acidentes_por_cidade = acidentes_filtrados.\
    groupby('codigo_ibge').\
    size().\
    reset_index(name='total_acidentes')

municipios_unicos = localidades_filtradas[['codigo_ibge', 'municipio']].\
    drop_duplicates(subset='codigo_ibge')

df_acidentes_por_cidade = pd.merge(
    df_acidentes_por_cidade,
    municipios_unicos,
    on='codigo_ibge'
)

df_acidentes_por_cidade.sort_values(
    by='total_acidentes', 
    ascending=False,
    inplace=True
)

st.title(f"Total de Acidentes - {estado_selecionado}")
st.dataframe(df_acidentes_por_cidade)
