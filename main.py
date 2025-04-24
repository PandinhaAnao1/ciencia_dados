import streamlit as st
import pandas as pd
import plotly.express as px


def carregar_dados():
    """Carrega os dados dos arquivos CSV."""
    df_localidades = pd.read_csv("./csv/localidades_2022.csv", low_memory=False)
    df_acidentes = pd.read_csv("./csv/acidentes_2022.csv", low_memory=False)
    return df_localidades, df_acidentes


def filtrar_acidentes_por_estado(df_acidentes, df_localidades, estado):
    """Filtra os dados de acidentes e localidades com base no estado selecionado."""
    if estado != "Todos os Estados":
        df_localidades = df_localidades[df_localidades['uf'] == estado]
        df_acidentes = df_acidentes[df_acidentes['uf_acidente'] == estado]
    return df_acidentes, df_localidades


def gerar_mapa_acidentes(df_acidentes):
    """Gera um mapa com a localização dos acidentes."""
    df_acidentes_mapa = df_acidentes.copy()
    df_acidentes_mapa.rename(columns={"latitude_acidente": "latitude", "longitude_acidente": "longitude"}, inplace=True)
    df_acidentes_mapa.dropna(subset=['latitude', 'longitude'], inplace=True)
    st.map(df_acidentes_mapa, zoom=4, use_container_width=True)


def gerar_top5_acidentes(df_acidentes_por_cidade):
    """Gera o gráfico de barras com os top 5 municípios com mais acidentes."""
    top5 = df_acidentes_por_cidade.sort_values(by='total_acidentes', ascending=False).head(5)
    fig = px.bar(
        top5,
        x='municipio',
        y='total_acidentes',
        labels={'municipio': 'Município', 'total_acidentes': 'Acidentes'},
    )
    st.plotly_chart(fig)


def gerar_acidentes_por_mil_habitantes(df_acidentes_por_cidade, df_localidades):
    """Calcula e gera o gráfico de acidentes por 1.000 habitantes."""
    populacao_unica = df_localidades[['codigo_ibge', 'municipio', 'qtde_habitantes']].drop_duplicates(subset='codigo_ibge')
    df_relativo = pd.merge(df_acidentes_por_cidade, populacao_unica, on=['codigo_ibge', 'municipio'], how='left')
    df_relativo = df_relativo[df_relativo['qtde_habitantes'] > 0].copy()
    df_relativo['acidentes_por_mil_hab'] = (df_relativo['total_acidentes'] / df_relativo['qtde_habitantes']) * 1000
    top5_relativo = df_relativo.sort_values(by='acidentes_por_mil_hab', ascending=False).head(5)

    fig = px.bar(
        top5_relativo,
        x='municipio',
        y='acidentes_por_mil_hab',
        labels={'municipio': 'Município', 'acidentes_por_mil_hab': 'Acidentes por 1.000 Habitantes'},
    )
    st.plotly_chart(fig)


def gerar_acidentes_por_mil_veiculos(df_acidentes_por_cidade, df_localidades):
    """Calcula e gera o gráfico de acidentes por 1.000 veículos."""
    frota_unica = df_localidades[['codigo_ibge', 'municipio', 'frota_total']].drop_duplicates(subset='codigo_ibge')
    df_veiculos = pd.merge(df_acidentes_por_cidade, frota_unica, on=['codigo_ibge', 'municipio'], how='left')
    df_veiculos = df_veiculos[df_veiculos['frota_total'] > 0].copy()
    df_veiculos['acidentes_por_mil_veic'] = (df_veiculos['total_acidentes'] / df_veiculos['frota_total']) * 1000
    top5_veiculos = df_veiculos.sort_values(by='acidentes_por_mil_veic', ascending=False).head(5)

    fig = px.bar(
        top5_veiculos,
        x='municipio',
        y='acidentes_por_mil_veic',
        labels={'municipio': 'Município', 'acidentes_por_mil_veic': 'Acidentes por 1.000 Veículos'},
    )
    st.plotly_chart(fig)

import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

def carregar_dados():
    """Carrega os dados dos arquivos CSV."""
    df_localidades = pd.read_csv("../localidades.csv", low_memory=False)
    df_acidentes = pd.read_csv("../acidentes.csv", low_memory=False)
    return df_localidades, df_acidentes


def filtrar_acidentes_por_estado(df_acidentes, df_localidades, estado):
    """Filtra os dados de acidentes e localidades com base no estado selecionado."""
    if estado != "Todos os Estados":
        df_localidades = df_localidades[df_localidades['uf'] == estado]
        df_acidentes = df_acidentes[df_acidentes['uf_acidente'] == estado]
    return df_acidentes, df_localidades


def distribuicao_temporal(df_acidentes, periodo="mensal"):
    """Gera um gráfico de distribuição de acidentes por mês ou semana."""
    # Convertendo para datetime
    df_acidentes['data_acidente'] = pd.to_datetime(df_acidentes['data_acidente'])

    # Agrupando por mês ou semana
    if periodo == "mensal":
        df_temporal = df_acidentes.groupby(df_acidentes['data_acidente'].dt.to_period('M')).size().reset_index(name='total_acidentes')
        title = "Distribuição de Acidentes por Mês"
    elif periodo == "semanal":
        df_temporal = df_acidentes.groupby(df_acidentes['data_acidente'].dt.to_period('W')).size().reset_index(name='total_acidentes')
        title = "Distribuição de Acidentes por Semana"

    fig = px.line(df_temporal, x='data_acidente', y='total_acidentes', title=title)
    st.plotly_chart(fig)


def heatmap_acidentes(df_acidentes):
    """Gera um heatmap de acidentes por dia da semana e hora."""
    df_acidentes['dia_semana'] = df_acidentes['data_acidente'].dt.day_name()
    df_acidentes['hora_acidente'] = df_acidentes['hora_acidente'].apply(lambda x: int(x.split(':')[0]) if isinstance(x, str) else np.nan)

    # Agrupando os dados
    df_heatmap = df_acidentes.groupby(['dia_semana', 'hora_acidente']).size().unstack(fill_value=0)

    # Ordenando os dias da semana
    order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    df_heatmap = df_heatmap.loc[order]

    # Criando o gráfico de calor
    plt.figure(figsize=(10, 6))
    sns.heatmap(df_heatmap, annot=True, cmap="YlGnBu", fmt="d", cbar=True)
    st.pyplot()


def correlacao_variaveis(df_acidentes, df_localidades):
    """Calcula e exibe a matriz de correlação entre variáveis relevantes."""
    # Agrupando os dados de acidentes por município
    df_acidentes_por_municipio = df_acidentes.groupby('codigo_ibge').size().reset_index(name='total_acidentes')

    # Pegando dados de população e frota
    populacao_frota = df_localidades[['codigo_ibge', 'qtde_habitantes', 'frota_total']].drop_duplicates(subset='codigo_ibge')

    # Combinando dados
    df_combined = pd.merge(df_acidentes_por_municipio, populacao_frota, on='codigo_ibge', how='left')

    # Calculando os índices
    df_combined['acidentes_por_mil_hab'] = (df_combined['total_acidentes'] / df_combined['qtde_habitantes']) * 1000
    df_combined['acidentes_por_mil_veic'] = (df_combined['total_acidentes'] / df_combined['frota_total']) * 1000

    # Matriz de correlação
    correlation_matrix = df_combined[['total_acidentes', 'qtde_habitantes', 'frota_total', 'acidentes_por_mil_hab', 'acidentes_por_mil_veic']].corr()

    # Exibindo a matriz de correlação
    plt.figure(figsize=(8, 6))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f')
    st.pyplot()






if __name__ == "__main__":
    
    df_localidades, df_acidentes = carregar_dados()

    st.sidebar.title("🚦 Análise de Acidentes dos Estados Brasileiros")
    estado = st.sidebar.selectbox(
        "Selecione o estado", ["Todos os Estados"] + df_localidades['uf'].unique().tolist()
    )

    df_acidentes, df_localidades = filtrar_acidentes_por_estado(df_acidentes, df_localidades, estado)

    st.header("Mapa de Acidentes")
    gerar_mapa_acidentes(df_acidentes)

    df_acidentes_por_cidade = df_acidentes.groupby('codigo_ibge').size().reset_index(name='total_acidentes')
    municipios_unicos = df_localidades[['codigo_ibge', 'municipio']].drop_duplicates(subset='codigo_ibge')
    df_acidentes_por_cidade = pd.merge(df_acidentes_por_cidade, municipios_unicos, on='codigo_ibge', how='left')

    st.header("Top 5 Municípios com Mais Acidentes")
    gerar_top5_acidentes(df_acidentes_por_cidade)

    st.header("Top 5 Municípios com Mais Acidentes por 1.000 Habitantes")
    gerar_acidentes_por_mil_habitantes(df_acidentes_por_cidade, df_localidades)

    st.header("Top 5 Municípios com Mais Acidentes por 1.000 Veículos")
    gerar_acidentes_por_mil_veiculos(df_acidentes_por_cidade, df_localidades)
    # Carregar os dados
    df_localidades, df_acidentes = carregar_dados()

    # Título e seleção do estado
    st.sidebar.title("🚦 Análise de Acidentes dos Estados Brasileiros")
    estado = st.sidebar.selectbox(
        "Selecione o estado", ["Todos os Estados"] + df_localidades['uf'].unique().tolist()
    )

    # Filtrar os dados conforme o estado
    df_acidentes, df_localidades = filtrar_acidentes_por_estado(df_acidentes, df_localidades, estado)

    # Distribuição Temporal dos Acidentes
    st.header("Distribuição Temporal dos Acidentes")
    periodo = st.selectbox("Selecione o intervalo:", ["mensal", "semanal"])
    distribuicao_temporal(df_acidentes, periodo)

    # Heatmap de acidentes por dia da semana e hora
    st.header("Heatmap de Acidentes por Dia da Semana e Hora")
    heatmap_acidentes(df_acidentes)

    # Correlação entre Variáveis
    st.header("Correlação entre Variáveis")
    correlacao_variaveis(df_acidentes, df_localidades)

