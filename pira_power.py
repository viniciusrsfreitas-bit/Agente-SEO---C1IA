import pandas as pd
from componentes_universais import *
import json

# CLIENTE: PIRA POWER
# Importação da planilha financeira

caminho_arquivo = "Vendas e fluxo.xlsx"

df_original = pd.read_excel(caminho_arquivo, usecols="A:L")

#print(df_original.head(10))

# ============================================================
# CLIENTE: PIRA POWER
# Aplicação do Componente Universal 01
# ============================================================

# Identifica a primeira coluna da planilha, onde estão as contas
coluna_conta = df_original.columns[0]
# Executa a função universal
df_vertical = transformar_vertical(df_original, coluna_conta)

# Visualiza o resultado
#print(df_vertical.head(20))

# Limpa os meses
df_vertical["Mês"] = df_vertical["Mês"].apply(limpar_mes)

# Limpa os valores financeiros
df_vertical["Valor"] = df_vertical["Valor"].apply(limpar_valor)

# Visualiza o resultado
#print(df_vertical.head(20))

# CLIENTE: PIRA POWER
df_vertical = converter_mes_ano(df_vertical, "Mês")

# Visualiza o resultado
#print(df_vertical.head(20))

# ============================================================
# CLIENTE: PIRA POWER
# Aplicação do Componente Universal 05
# ============================================================

# Substitui os valores financeiros nulos por zero
df_vertical = tratar_nulos(
    df_vertical,
    coluna="Valor",
    valor_substituto=0
)

# Visualiza o resultado
#print(df_vertical.head(20))

# Transforma o dicionário em uma tabela de classificação
df_lista = pd.DataFrame.from_dict(
    classificacao_contas,
    orient="index"
).reset_index()

# Renomeia a coluna usada para localizar as contas
df_lista = df_lista.rename(
    columns={
        "index": "Despesa Original",
        "Conta": "Conta Classificada"
    }
)

# Faz o PROCV usando a coluna Conta da Pira Power
df_vertical = componente_universal06(
    df_dados=df_vertical,
    df_lista=df_lista.rename(columns={"Despesa Original": "Conta"}),
    coluna_busca="Conta"
)

#print(df_vertical.head(20))

# CLIENTE: PIRA POWER

df_vertical = excluir_sem_classificacao(
    df_vertical,
    coluna="Conta Classificada",
    valor_vazio="N#A"
)

#print(df_vertical.head(20))

# ============================================================
# CLIENTE: PIRA POWER
# Exclusão da receita consolidada para evitar duplicidade
# ============================================================

# Remove a linha de receita total, mantendo as receitas detalhadas
df_vertical = df_vertical[
    df_vertical["Conta Classificada"] != "Receita de Vendas"
].copy()

# Reorganiza os índices
df_vertical = df_vertical.reset_index(drop=True)

# Confere as contas restantes
#print(
df_vertical[
        ["Conta", "Conta Classificada", "Centro de Custo", "Resultado"]
    ].drop_duplicates()

df_consolidado = df_vertical.groupby(
    ["Conta Classificada", "Mês"]
)["Valor"].sum().unstack(fill_value=0)

#print(df_consolidado)

# ============================================================
# CLIENTE: PIRA POWER
# Preparação dos dados para o Componente Universal 08
# ============================================================

# 1. Selecionar apenas as contas que pertencem à DRE
df_pira_dre = df_vertical[
    df_vertical["Resultado"] == "DRE"
].copy()

# 2. Consolidar os valores por conta e mês
df_dre = df_pira_dre.pivot_table(
    index="Conta Classificada",
    columns="Mês",
    values="Valor",
    aggfunc="sum",
    fill_value=0
)

# 3. Organizar os meses em ordem cronológica
ordem_meses = [
    "dez/25", "jan/26", "fev/26", "mar/26",
    "abr/26", "mai/26", "jun/26", "jul/26",
    "ago/26", "set/26", "out/26"
]

df_dre = df_dre.reindex(columns=ordem_meses)

# 4. Identificar automaticamente as contas de receita
receitas = df_pira_dre.loc[
    df_pira_dre["Centro de Custo"] == "Receita",
    "Conta Classificada"
].drop_duplicates().tolist()

# 5. Identificar automaticamente as contas de custos
despesas = df_pira_dre.loc[
    df_pira_dre["Centro de Custo"].isin(["CF", "CV"]),
    "Conta Classificada"
].drop_duplicates().tolist()

# 6. Preparar o mês de fechamento
mes_fechamento = "jul/26"

# 7. Preparar a quantidade de meses para análise
meses_numero = 3

# 8. Visualizar a base preparada
#print(df_dre)

# CLIENTE: PIRA POWER
# Aplicação do Componente Universal 09
df_vertical = inverter_sinal_despesas(
    df=df_vertical,
    coluna_classificacao="Centro de Custo",
    classificacoes=["CF", "CV"],
    coluna_valor="Valor"
)

# Conferir o resultado (desativado)
# print(
#     df_vertical[
#         ["Conta Classificada", "Centro de Custo", "Valor"]
#     ].head(20)
# )

# CLIENTE: PIRA POWER
# Reconstruir a DRE com os custos negativos

df_pira_dre = df_vertical[
    df_vertical["Resultado"] == "DRE"
].copy()

df_dre = df_pira_dre.pivot_table(
    index="Conta Classificada",
    columns="Mês",
    values="Valor",
    aggfunc="sum",
    fill_value=0
)

# Manter a ordem cronológica dos meses
df_dre = df_dre.reindex(columns=ordem_meses)

#print(df_dre)

# ============================================================
# CLIENTE: PIRA POWER
# Aplicação do Componente Universal 10
# ============================================================

# Define as contas que compõem o faturamento
contas_receita = [
    "Receita de Baterias",
    "Receita de Eletrobike",
    "Receita de Nobreaks",
    "Receita de Serviços"
]

# Calcula os percentuais sem alterar a DRE original
df_pira_percentual = calcular_porcentagem_faturamento(
    df_dre,
    contas_receita
)

# Exibe os resultados
#print(df_pira_percentual.round(2))

# ============================================================
# CLIENTE: PIRA POWER
# Aplicação dos Componentes Universais 11 e 12
# ============================================================

# Define o mês de fechamento
mes_fechamento_pira = "jul/26"

# Identifica os três meses anteriores
meses_anteriores_pira = identificar_meses_anteriores(
    df_dre,
    mes_fechamento_pira
)

# Prepara as classificações para a análise
df_contas_pira = (
    df_vertical[
        ["Conta Classificada", "Centro de Custo"]
    ]
    .drop_duplicates()
)

# Seleciona somente CF e CV
df_contas_pira = df_contas_pira[
    df_contas_pira["Centro de Custo"].isin(["CF", "CV"])
]

# Monta o dicionário no formato esperado pelo componente
classificacao_custos_pira = {
    linha["Conta Classificada"]: {
        "custo": linha["Centro de Custo"]
    }
    for _, linha in df_contas_pira.iterrows()
}

# Executa a análise de variações
df_pira_variacoes = analisar_variacoes(
    df_dre,
    df_pira_percentual,
    classificacao_custos_pira,
    mes_fechamento_pira,
    meses_anteriores_pira
)

# Exibe os meses comparados
print("Meses anteriores:", meses_anteriores_pira)

# Exibe o resultado
print(df_pira_variacoes.round(2))

# ============================================================
# CLIENTE: PIRA POWER
# Aplicação do Componente Universal 13
# ============================================================

# Define as contas patrimoniais que serão analisadas
contas_patrimoniais_pira = ["EF", "A PAGAR"]

# Seleciona as contas e os meses
df_pira_saldos = df_vertical[
    df_vertical["Conta"].isin(contas_patrimoniais_pira)
].pivot_table(
    index="Conta",
    columns="Mês",
    values="Valor",
    aggfunc="sum"
)

# Organiza os meses na ordem cronológica
df_pira_saldos = df_pira_saldos.reindex(
    columns=ordem_meses
)

# Executa a análise dos saldos
df_pira_evolucao_saldos = analisar_evolucao_saldos(
    df_pira_saldos,
    contas_patrimoniais_pira,
    mes_fechamento_pira,
    meses_anteriores_pira
)

# Exibe os saldos mensais
print(df_pira_saldos)

# Exibe a análise de evolução
print(df_pira_evolucao_saldos.round(2))

# ============================================================
# CLIENTE: PIRA POWER
# Aplicação do Componente Universal 14
# Preparação dos Inputs do Agente Financeiro
# ============================================================

# ------------------------------------------------------------
# 1. Consolidar os dados financeiros para o agente de IA
# ------------------------------------------------------------

# Reúne os resultados dos componentes anteriores:
# - DRE mensal
# - Receitas por linha de negócio
# - Custos fixos (R$)
# - Custos variáveis (% do faturamento)
# - Capital de giro (estoques e contas a pagar)

inputs_pira = preparar_inputs_agente_financeiro(
    df_dre=df_dre,
    df_percentual=df_pira_percentual,
    df_variacoes=df_pira_variacoes,
    df_saldos=df_pira_saldos,
    df_evolucao_saldos=df_pira_evolucao_saldos,
    cliente="Pira Power",
    mes_fechamento=mes_fechamento_pira,
    meses_anteriores=meses_anteriores_pira
)


# ------------------------------------------------------------
# 2. Gerar o arquivo JSON
# ------------------------------------------------------------

# Define o arquivo que será utilizado pelo agente financeiro
caminho_json_pira = "inputs_agente_pira.json"

# Salva os dados estruturados em formato JSON
with open(caminho_json_pira, "w", encoding="utf-8") as arquivo:
    json.dump(
        inputs_pira,
        arquivo,
        ensure_ascii=False,
        indent=4,
        allow_nan=False
    )


# ------------------------------------------------------------
# 3. Confirmar a geração dos inputs
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("PIRA POWER - INPUTS DO AGENTE FINANCEIRO")
print("=" * 60)

print(f"Mês de fechamento: {mes_fechamento_pira}")
print(f"Meses anteriores: {', '.join(meses_anteriores_pira)}")
print(f"Arquivo gerado: {caminho_json_pira}")

print("\nInputs financeiros preparados com sucesso.")

# ============================================================
# CLIENTE: PIRA POWER
# Aplicação do Componente Universal 15
# Arredondamento dos Inputs do Agente Financeiro
# ============================================================

# Padroniza os valores numéricos em duas casas decimais.
# Não altera os cálculos dos componentes anteriores.
# O arredondamento ocorre apenas nos dados enviados à IA.

inputs_pira = arredondar_dados(
    inputs_pira,
    casas_decimais=2
)