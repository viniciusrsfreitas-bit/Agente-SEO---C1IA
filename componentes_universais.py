import pandas as pd
import json
 

# COMPONENTE UNIVERSAL 01
# Transformação de planilhas horizontais em verticais
# ============================================================

def transformar_vertical(df, coluna_conta):

    """
    Objetivo:
    Transformar uma tabela horizontal em vertical.

    Parâmetros:
    df: DataFrame do Pandas contendo os dados originais.
    coluna_conta: nome da coluna que identifica as contas.

    Retorno:
    DataFrame com três colunas:
    Conta, Mês e Valor.

    Aplicação:
    Reutilizável para diferentes clientes com dados
    organizados em colunas mensais.
    """

    # Cria uma cópia para preservar o DataFrame original
    df_vertical = df.copy()

    # Transforma as colunas dos meses em linhas
    # Mantém a coluna que identifica cada conta
    df_vertical = df_vertical.melt(
        id_vars=[coluna_conta],
        var_name="Mês",
        value_name="Valor"
    )

    # Padroniza o nome da coluna de identificação
    df_vertical = df_vertical.rename(
        columns={coluna_conta: "Conta"}
    )

    # Devolve o DataFrame transformado
    return df_vertical


# ============================================================
# COMPONENTE UNIVERSAL 02
# Dicionário de Classificação de Contas Financeiras
# ============================================================

# OBJETIVO:
# Padronizar a classificação das contas financeiras recebidas
# de diferentes clientes.
#
# ESTRUTURA:
# A chave principal representa o nome original da conta.
#
# Cada conta possui quatro classificações:
#
# Despesa:
#   Identificação específica da despesa (salários, aluguel etc.).
#
# Conta:
#   Classificação contábil ou gerencial da movimentação.
#
# Centro de Custo:
#   Receita = Receita operacional
#   CF      = Custo fixo
#   CV      = Custo variável
#   N#A     = Classificação ainda não definida
#
# Resultado:
#   DRE     = Conta relacionada ao resultado econômico
#   Estoque = Conta relacionada ao controle de estoque
#   N#A     = Classificação ainda não definida
#
# OBSERVAÇÃO:
# Os campos N#A serão classificados posteriormente.
# O dicionário poderá ser ampliado com novas contas.
# ============================================================

classificacao_contas = {

    # CONTROLE DE ESTOQUE

    "EI": {
        "Despesa": "N#A",
        "Conta": "Estoque Inicial",
        "Centro de Custo": "N#A",
        "Resultado": "Estoque"
    },

    "COMPRA": {
        "Despesa": "N#A",
        "Conta": "Compras de Mercadorias",
        "Centro de Custo": "N#A",
        "Resultado": "Estoque"
    },

    "EF": {
        "Despesa": "N#A",
        "Conta": "Estoque Final",
        "Centro de Custo": "N#A",
        "Resultado": "Estoque"
    },

    # CUSTOS E RECEITAS OPERACIONAIS

    "CUSTO VENDA": {
        "Despesa": "N#A",
        "Conta": "Custo das Mercadorias Vendidas",
        "Centro de Custo": "CV",
        "Resultado": "DRE"
    },

    "RECEITA VENDA": {
        "Despesa": "N#A",
        "Conta": "Receita de Vendas",
        "Centro de Custo": "Receita",
        "Resultado": "DRE"
    },

    "A PAGAR": {
        "Despesa": "N#A",
        "Conta": "Fornecedores a Pagar",
        "Centro de Custo": "N#A",
        "Resultado": "Obrigações Terceiros"
    },

    "CUSTOS FIXOS": {
        "Despesa": "N#A",
        "Conta": "Custo Fixo",
        "Centro de Custo": "CF",
        "Resultado": "DRE"
    },

    # CONTAS AINDA NÃO CLASSIFICADAS

    "SD": {
        "Despesa": "N#A",
        "Conta": "N#A",
        "Centro de Custo": "N#A",
        "Resultado": "N#A"
    },

    "PR": {
        "Despesa": "N#A",
        "Conta": "N#A",
        "Centro de Custo": "N#A",
        "Resultado": "N#A"
    },

    # RECEITAS POR CATEGORIA DE PRODUTO OU SERVIÇO

    "Baterias": {
        "Despesa": "N#A",
        "Conta": "Receita de Baterias",
        "Centro de Custo": "Receita",
        "Resultado": "DRE"
    },

    "Eletrobike": {
        "Despesa": "N#A",
        "Conta": "Receita de Eletrobike",
        "Centro de Custo": "Receita",
        "Resultado": "DRE"
    },

    "Nobreaks": {
        "Despesa": "N#A",
        "Conta": "Receita de Nobreaks",
        "Centro de Custo": "Receita",
        "Resultado": "DRE"
    },

    "Serviços": {
        "Despesa": "N#A",
        "Conta": "Receita de Serviços",
        "Centro de Custo": "Receita",
        "Resultado": "DRE"
    },

    # INFORMAÇÕES DE NOTAS FISCAIS

    "NF PRODUTOS": {
        "Despesa": "N#A",
        "Conta": "N#A",
        "Centro de Custo": "N#A",
        "Resultado": "N#A"
    },

    "NF SERVIÇOS": {
        "Despesa": "N#A",
        "Conta": "N#A",
        "Centro de Custo": "N#A",
        "Resultado": "N#A"
    }
}


# ============================================================
# COMPONENTE UNIVERSAL 03
# Limpeza e Padronização de Meses e Valores
# ============================================================

import pandas as pd
import re

# ------------------------------------------------------------
# FUNÇÃO 01 - PADRONIZAÇÃO DOS MESES
# ------------------------------------------------------------

def limpar_mes(valor):

    # Se o valor estiver vazio, retorna uma data ausente
    if pd.isna(valor):
        return pd.NaT

    # Dicionário de meses em português
    meses = {
        "jan": "01", "fev": "02", "mar": "03",
        "abr": "04", "mai": "05", "jun": "06",
        "jul": "07", "ago": "08", "set": "09",
        "out": "10", "nov": "11", "dez": "12"
    }

    # Se já for uma data, padroniza para o primeiro dia do mês
    if isinstance(valor, (pd.Timestamp, __import__("datetime").datetime)):
        return pd.Timestamp(valor).replace(day=1).normalize()

    # Padroniza o texto recebido
    texto = str(valor).strip().lower()

    # Identifica formatos como jan/26 ou jan/2026
    resultado = re.fullmatch(r"([a-zç]{3})/(\d{2}|\d{4})", texto)

    if resultado:
        mes, ano = resultado.groups()

        if mes in meses:
            if len(ano) == 2:
                ano = "20" + ano

            return pd.Timestamp(f"{ano}-{meses[mes]}-01")

    # Outros formatos não reconhecidos ficam como ausentes
    return pd.NaT


# ------------------------------------------------------------
# FUNÇÃO 02 - PADRONIZAÇÃO DOS VALORES FINANCEIROS
# ------------------------------------------------------------

def limpar_valor(valor):

    # Preserva valores ausentes
    if pd.isna(valor):
        return float("nan")

    # Valores já numéricos não precisam de conversão
    if isinstance(valor, (int, float)):
        return float(valor)

    # Remove espaços e símbolo monetário
    texto = str(valor).strip().replace("R$", "").replace(" ", "")

    # Trata células vazias ou marcadores sem valor
    if texto in ["", "-", "N#A", "#DIV/0!", "EF"]:
        return float("nan")

    # Trata formato brasileiro:
    # 12.690,50 -> 12690.50
    # 265.788   -> 265788
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    elif re.fullmatch(r"-?\d{1,3}(\.\d{3})+", texto):
        texto = texto.replace(".", "")

    # Converte o resultado em número
    return pd.to_numeric(texto, errors="coerce")

# ============================================================
# COMPONENTE UNIVERSAL 04
# Conversão de datas para o formato mês/ano
# ============================================================

def converter_mes_ano(df, coluna_mes):

    # Cria uma cópia para preservar o DataFrame recebido
    df_tratado = df.copy()

    # Dicionário dos meses em português
    meses = {
        1: "jan", 2: "fev", 3: "mar",
        4: "abr", 5: "mai", 6: "jun",
        7: "jul", 8: "ago", 9: "set",
        10: "out", 11: "nov", 12: "dez"
    }

    # Converte cada data para o formato mês/ano
    # Exemplo: 2026-01-01 -> jan/26
    df_tratado[coluna_mes] = df_tratado[coluna_mes].apply(
        lambda data: f"{meses[data.month]}/{str(data.year)[-2:]}"
        if pd.notna(data) else "N#A"
    )

    # Retorna o DataFrame com os meses formatados
    return df_tratado

# ============================================================
# COMPONENTE UNIVERSAL 05
# Tratamento de Valores Nulos
# ============================================================

def tratar_nulos(df, coluna, valor_substituto=0):

    """
    Objetivo:
    Substituir valores nulos em uma coluna do DataFrame.

    Parâmetros:
    df: DataFrame que será tratado.
    coluna: coluna em que será aplicada a substituição.
    valor_substituto: valor utilizado para substituir os nulos.

    Retorno:
    DataFrame com os valores nulos tratados.
    """

    # Cria uma cópia para preservar o DataFrame original
    df_tratado = df.copy()

    # Substitui os valores nulos pelo valor definido
    df_tratado[coluna] = df_tratado[coluna].fillna(valor_substituto)

    # Retorna o DataFrame tratado
    return df_tratado

# ============================================================
# COMPONENTE UNIVERSAL 05
# Tratamento de Valores Nulos
# ============================================================

def tratar_nulos(df, coluna, valor_substituto=0):

    """
    Objetivo:
    Substituir valores nulos em uma coluna do DataFrame.

    Parâmetros:
    df: DataFrame que será tratado.
    coluna: coluna em que será aplicada a substituição.
    valor_substituto: valor utilizado para substituir os nulos.

    Retorno:
    DataFrame com os valores nulos tratados.
    """

    # Cria uma cópia para preservar o DataFrame original
    df_tratado = df.copy()

    # Substitui os valores nulos pelo valor definido
    df_tratado[coluna] = df_tratado[coluna].fillna(valor_substituto)

    # Retorna o DataFrame tratado
    return df_tratado

# ============================================================
# COMPONENTE UNIVERSAL 06
# PROCV - Classificação automática pelo dicionário
# ============================================================

def componente_universal06(df_dados, df_lista, coluna_busca):

    # Cruza os dados com a lista de classificações
    df_resultado = df_dados.merge(
        df_lista,
        on=coluna_busca,
        how="left",
        validate="many_to_one"
    )

    # Retorna os dados com as classificações encontradas
    return df_resultado

# ============================================================
# COMPONENTE UNIVERSAL 07
# Exclusão de registros sem classificação
# ============================================================

def excluir_sem_classificacao(df, coluna, valor_vazio=None):

    # Cria uma cópia para preservar os dados originais
    df_tratado = df.copy()

    # Remove registros com valores nulos (NaN ou None)
    df_tratado = df_tratado.dropna(subset=[coluna])

    # Remove registros com texto vazio ou somente espaços
    df_tratado = df_tratado[
        df_tratado[coluna].astype(str).str.strip() != ""
    ]

    # Remove um marcador adicional, caso seja informado
    if valor_vazio is not None:
        df_tratado = df_tratado[
            df_tratado[coluna] != valor_vazio
        ]

    # Reorganiza os índices
    df_tratado = df_tratado.reset_index(drop=True)

    return df_tratado

# ============================================================
# COMPONENTE UNIVERSAL 08
# Processamento da DRE e Análise Financeira
#
# Código original do mercadinho, sem alterações na lógica.
# ============================================================

import json
import pandas as pd


def processamento_financeiro(
    df_dre,
    receitas,
    despesas,
    classificacao_contas,
    mes_fechamento,
    meses_numero,
    dados,
    mapeamento
):

    # Calcular o total das receitas
    df_dre.loc["Total Receitas"] = (
        df_dre.reindex(receitas).fillna(0).sum(axis=0)
    )

    # Calcular o total das despesas
    df_dre.loc["Total Despesas"] = (
        df_dre.reindex(despesas).fillna(0).sum(axis=0)
    )

    # Calcular o resultado mensal
    df_dre.loc["Resultado"] = (
        df_dre.loc["Total Receitas"] +
        df_dre.loc["Total Despesas"]
    )

    # Organizar a apresentação da DRE
    ordem_dre = (
        ["Receitas"]
        + receitas
        + ["Total Receitas"]
        + ["Despesas"]
        + despesas
        + ["Total Despesas", "Resultado"]
    )

    df_dre = df_dre.reindex(ordem_dre)

    # Exportação Excel mantida como comentário
    # with pd.ExcelWriter("DRE_Final.xlsx", engine="openpyxl") as writer:
    #
    #     df_dre.to_excel(writer, sheet_name="DRE")
    #
    #     aba = writer.sheets["DRE"]
    #
    #     for linha in aba.iter_rows(min_row=2, min_col=2):
    #         for celula in linha:
    #             celula.number_format = '#,##0.00'

    porcentagem_faturamento = calcular_porcentagem_faturamento(df_dre)

    meses_anteriores = identificar_meses_anteriores(
        df_dre,
        mes_fechamento,
        meses_numero
    )

    analise_variacoes = analisar_variacoes(
        df_dre,
        porcentagem_faturamento,
        classificacao_contas,
        mes_fechamento,
        meses_anteriores
    )

    df_lancamentos = padronizar_lancamentos(
        dados,
        mapeamento
    )

    json_analise = gerar_json_analise(
        analise_variacoes,
        df_lancamentos,
        mes_fechamento,
        meses_anteriores,
        meses_numero
    )

    print(
        json.dumps(
            json_analise,
            ensure_ascii=False,
            indent=4
        )
    )

    print(
        json.dumps(
            json_analise["Juros pagamento atrasado"],
            ensure_ascii=False,
            indent=4,
            allow_nan=False
        )
    )

    return df_dre, porcentagem_faturamento, analise_variacoes, json_analise

    # ============================================================
# COMPONENTE UNIVERSAL 09
# Inversão de Sinais de Despesas
# ============================================================

def inverter_sinal_despesas(df, coluna_classificacao, classificacoes, coluna_valor):

    """
    Objetivo:
    Padronizar despesas e custos como valores negativos.

    Parâmetros:
    df: DataFrame financeiro.
    coluna_classificacao: coluna que identifica os tipos de conta.
    classificacoes: lista de classificações consideradas despesas.
    coluna_valor: coluna que contém os valores financeiros.

    Retorno:
    DataFrame com despesas negativas e receitas preservadas.
    """

    # Cria uma cópia para preservar os dados originais
    df_tratado = df.copy()

    # Identifica as linhas pertencentes às classificações informadas
    filtro = df_tratado[coluna_classificacao].isin(classificacoes)

    # Garante que os valores dessas linhas sejam negativos
    # abs() evita inverter novamente um valor já negativo
    df_tratado.loc[filtro, coluna_valor] = (
        -df_tratado.loc[filtro, coluna_valor].abs()
    )

    # Retorna o DataFrame tratado
    return df_tratado

# ============================================================
# COMPONENTE UNIVERSAL 10
# Cálculo da Participação Percentual sobre o Faturamento
# ============================================================

def calcular_porcentagem_faturamento(df, contas_receita):

    """
    Objetivo:
    Calcular a participação percentual de cada conta financeira
    sobre o faturamento total de cada mês.

    Parâmetros:
    df: DataFrame financeiro consolidado, com contas nas linhas
        e meses nas colunas.
    contas_receita: lista das contas que compõem o faturamento.

    Retorno:
    DataFrame com a participação percentual de cada conta
    sobre o faturamento mensal, preservando o original.
    """

    # Cria uma cópia para preservar os dados originais
    df_percentual = df.copy()

    # Calcula o faturamento total de cada mês
    faturamento = df_percentual.loc[contas_receita].sum(axis=0)

    # Evita divisão por zero em meses sem faturamento
    faturamento = faturamento.replace(0, float("nan"))

    # Calcula a participação percentual de cada conta
    df_percentual = df_percentual.div(faturamento, axis=1) * 100

    # Retorna o DataFrame com os percentuais calculados
    return df_percentual

# ============================================================
# COMPONENTE UNIVERSAL 11
# Identificação dos Três Meses Anteriores
# ============================================================

def identificar_meses_anteriores(df, mes_fechamento):

    """
    Objetivo:
    Identificar os três meses anteriores ao mês de fechamento,
    considerando a mudança de ano.

    Parâmetros:
    df: DataFrame financeiro com meses nas colunas.
    mes_fechamento: mês que será analisado, no formato "set/26".

    Retorno:
    Lista com os três meses anteriores disponíveis no DataFrame.
    """

    # Converte o mês de fechamento para uma data
    data_fechamento = pd.to_datetime(
        mes_fechamento,
        format="%b/%y"
    ) if False else None

    # Dicionário dos meses em português
    meses_numero = {
        "jan": 1, "fev": 2, "mar": 3,
        "abr": 4, "mai": 5, "jun": 6,
        "jul": 7, "ago": 8, "set": 9,
        "out": 10, "nov": 11, "dez": 12
    }

    # Converte o fechamento para Timestamp
    mes, ano = mes_fechamento.split("/")

    data_fechamento = pd.Timestamp(
        year=2000 + int(ano),
        month=meses_numero[mes.lower()],
        day=1
    )

    # Identifica as três datas anteriores
    datas_anteriores = [
        data_fechamento - pd.DateOffset(months=i)
        for i in range(1, 4)
    ]

    # Converte os nomes das colunas em datas
    datas_colunas = {}

    for coluna in df.columns:

        mes_coluna, ano_coluna = coluna.split("/")

        datas_colunas[coluna] = pd.Timestamp(
            year=2000 + int(ano_coluna),
            month=meses_numero[mes_coluna.lower()],
            day=1
        )

    # Seleciona os meses existentes no DataFrame
    meses_anteriores = [
        coluna
        for coluna, data in datas_colunas.items()
        if data in datas_anteriores
    ]

    # Verifica se existem os três meses necessários
    if len(meses_anteriores) != 3:
        raise ValueError(
            "Não existem três meses completos para comparação."
        )

    # Retorna os meses em ordem cronológica
    return meses_anteriores

# ============================================================
# COMPONENTE UNIVERSAL 12
# Análise de Variações Financeiras
# ============================================================

def analisar_variacoes(
    df_dre,
    df_percentual,
    classificacao_contas,
    mes_fechamento,
    meses_anteriores
):

    """
    Objetivo:
    Comparar os custos do mês de fechamento com a média
    dos três meses anteriores.

    Parâmetros:
    df_dre: DataFrame com valores financeiros mensais.
    df_percentual: DataFrame com percentuais sobre faturamento.
    classificacao_contas: dicionário que relaciona contas a CF ou CV.
    mes_fechamento: mês atual da análise.
    meses_anteriores: lista dos três meses anteriores.

    Retorno:
    DataFrame com conta, classificação, média anterior,
    mês atual, diferença e variação percentual.
    """

    # Lista para armazenar os resultados
    analise = []

    # Percorre as contas e suas classificações
    for conta, classificacao in classificacao_contas.items():

        tipo_custo = classificacao["custo"]

        # Analisa somente custos fixos e variáveis
        if tipo_custo not in ["CF", "CV"]:
            continue

        # Seleciona a base de comparação
        if tipo_custo == "CF":
            dados = df_dre.abs()
        else:
            dados = df_percentual.abs()

        # Calcula a média dos três meses anteriores
        media_anterior = (
            dados.loc[conta, meses_anteriores]
            .fillna(0)
            .mean()
        )

        # Obtém o valor do mês de fechamento
        valor_atual = dados.loc[conta, mes_fechamento]

        # Trata valores ausentes de custo fixo
        if pd.isna(valor_atual) and tipo_custo == "CF":
            valor_atual = 0

        # Calcula a diferença
        diferenca = valor_atual - media_anterior

        # Calcula a variação percentual
        if media_anterior != 0:
            variacao_percentual = (
                diferenca / media_anterior
            ) * 100
        else:
            variacao_percentual = float("nan")

        # Armazena o resultado da conta
        analise.append({
            "Conta": conta,
            "Classificação": tipo_custo,
            "Média Anterior": media_anterior,
            "Mês Atual": valor_atual,
            "Diferença": diferenca,
            "Variação %": variacao_percentual
        })

    # Retorna os resultados em DataFrame
    return pd.DataFrame(analise)

# ============================================================
# COMPONENTE UNIVERSAL 13
# Análise de Evolução de Saldos Patrimoniais
# ============================================================

def analisar_evolucao_saldos(
    df,
    contas_analisar,
    mes_fechamento,
    meses_anteriores
):

    """
    Objetivo:
    Comparar o saldo do mês de fechamento com a média
    dos três meses anteriores.

    Parâmetros:
    df: DataFrame com contas nas linhas e meses nas colunas.
    contas_analisar: lista das contas que serão analisadas.
    mes_fechamento: mês atual da análise.
    meses_anteriores: lista dos três meses anteriores.

    Retorno:
    DataFrame com conta, média histórica, saldo atual,
    diferença e variação percentual.
    """

    # Cria uma lista para armazenar os resultados
    analise = []

    # Percorre as contas selecionadas
    for conta in contas_analisar:

        # Calcula a média dos três meses anteriores
        media_anterior = (
            df.loc[conta, meses_anteriores]
            .mean()
        )

        # Identifica o saldo do mês de fechamento
        saldo_atual = df.loc[conta, mes_fechamento]

        # Calcula a diferença em reais
        diferenca = saldo_atual - media_anterior

        # Calcula a variação percentual
        if pd.notna(media_anterior) and media_anterior != 0:
            variacao_percentual = (
                diferenca / abs(media_anterior)
            ) * 100
        else:
            variacao_percentual = float("nan")

        # Armazena o resultado
        analise.append({
            "Conta": conta,
            "Média Anterior": media_anterior,
            "Mês Atual": saldo_atual,
            "Diferença": diferenca,
            "Variação %": variacao_percentual
        })

    # Retorna o DataFrame consolidado
    return pd.DataFrame(analise)


# ============================================================
# COMPONENTE UNIVERSAL 14
# Preparação dos Inputs do Agente Financeiro
# ============================================================

def preparar_inputs_agente_financeiro(
    df_dre,
    df_percentual,
    df_variacoes,
    df_saldos,
    df_evolucao_saldos,
    cliente,
    mes_fechamento,
    meses_anteriores
):
    """
    Objetivo:
    Organizar os resultados financeiros já calculados
    em uma estrutura JSON para o agente de IA.

    Parâmetros:
    df_dre: DRE mensal com valores em reais.
    df_percentual: percentuais sobre faturamento.
    df_variacoes: resultado do Componente Universal 12.
    df_saldos: evolução mensal de estoque e obrigações.
    df_evolucao_saldos: resultado do Componente Universal 13.
    cliente: nome do cliente.
    mes_fechamento: mês utilizado na análise.
    meses_anteriores: meses utilizados na comparação.

    Retorno:
    Dicionário Python compatível com JSON.
    """


    # Converte valores do Pandas e NumPy para tipos
    # compatíveis com JSON, preservando dados ausentes.
    def converter_valor(valor):
        if isinstance(valor, dict):
            return {
                str(chave): converter_valor(item)
                for chave, item in valor.items()
            }

        if isinstance(valor, (list, tuple)):
            return [converter_valor(item) for item in valor]

        if pd.isna(valor):
            return None

        if hasattr(valor, "item"):
            return valor.item()

        return valor

    # Converte DataFrames em listas de registros.
    def converter_dataframe(df):
        if df is None:
            return []

        df_saida = df.copy()

        # Preserva o nome das contas que estão no índice.
        if not isinstance(df_saida.index, pd.RangeIndex):
            df_saida = df_saida.reset_index()

        registros = df_saida.to_dict(orient="records")

        return converter_valor(registros)

    # Separa as análises de custos fixos e variáveis.
    variacoes_cf = df_variacoes[
        df_variacoes["Classificação"] == "CF"
    ].copy()

    variacoes_cv = df_variacoes[
        df_variacoes["Classificação"] == "CV"
    ].copy()

    # Seleciona as contas de receita.
    contas_receita = [
        conta for conta in df_dre.index
        if str(conta).startswith("Receita de ")
    ]

    df_receitas = df_dre.loc[contas_receita].copy()

    # Seleciona somente os percentuais de receita e CV.
    contas_percentuais = [
        conta for conta in df_percentual.index
        if (
            str(conta).startswith("Receita de ")
            or conta in variacoes_cv["Conta"].values
        )
    ]

    df_percentuais_agente = df_percentual.loc[
        contas_percentuais
    ].copy()

    # Monta os inputs do agente.
    inputs_agente = {
        "contexto": {
            "cliente": cliente,
            "mes_fechamento": mes_fechamento,
            "meses_anteriores": meses_anteriores,
            "observacao": (
                "A análise utiliza o mês de fechamento "
                "informado. Meses posteriores podem conter "
                "dados incompletos."
            )
        },

        "dre": {
            "unidade": "BRL",
            "dados_mensais": converter_dataframe(df_dre)
        },

        "receitas": {
            "unidade": "BRL",
            "valores_mensais": converter_dataframe(df_receitas),
            "participacao_percentual": converter_dataframe(
                df_percentuais_agente.loc[
                    [
                        conta for conta in contas_receita
                        if conta in df_percentuais_agente.index
                    ]
                ]
            )
        },

        "custos_fixos": {
            "unidade": "BRL",
            "regra": (
                "Comparar custos fixos em valores absolutos, "
                "não em percentual do faturamento."
            ),
            "analise_variacoes": converter_dataframe(
                variacoes_cf
            )
        },

        "custos_variaveis": {
            "unidade": "percentual_do_faturamento",
            "regra": (
                "Comparar custos variáveis pela participação "
                "no faturamento. A diferença é expressa "
                "em pontos percentuais."
            ),
            "percentuais_mensais": converter_dataframe(
                df_percentuais_agente.loc[
                    [
                        conta for conta in df_percentuais_agente.index
                        if conta in variacoes_cv["Conta"].values
                    ]
                ]
            ),
            "analise_variacoes": converter_dataframe(
                variacoes_cv
            )
        },

        "capital_de_giro": {
            "unidade": "BRL",
            "saldos_mensais": converter_dataframe(df_saldos),
            "analise_variacoes": converter_dataframe(
                df_evolucao_saldos
            )
        }
    }

    # Verifica se a estrutura pode ser serializada em JSON.
    json.dumps(inputs_agente, ensure_ascii=False, allow_nan=False)

    return inputs_agente

# ============================================================
# COMPONENTE UNIVERSAL 15
# Arredondamento de Dados Numéricos
# ============================================================

def arredondar_dados(dados, casas_decimais=2):
    """
    Objetivo:
    Arredondar valores numéricos de estruturas de dados
    antes do envio para agentes de IA.

    Aceita:
    - Dicionários
    - Listas
    - Números

    Preserva:
    - Textos
    - Valores nulos
    - Valores booleanos
    - Estrutura original dos dados

    Retorno:
    Estrutura com valores numéricos arredondados.
    """

    # Percorre os dicionários
    if isinstance(dados, dict):
        return {
            chave: arredondar_dados(valor, casas_decimais)
            for chave, valor in dados.items()
        }

    # Percorre as listas
    if isinstance(dados, list):
        return [
            arredondar_dados(valor, casas_decimais)
            for valor in dados
        ]

    # Arredonda números decimais
    if isinstance(dados, float):
        return round(dados, casas_decimais)

    # Preserva os demais tipos
    return dados