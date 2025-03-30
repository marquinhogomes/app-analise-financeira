import pandas as pd

def calcular_fcd(receita_atual, margem_ebitda, wacc, g, anos=5):
    fluxo_caixa = []
    receita = receita_atual
    margem = margem_ebitda / 100
    taxa_wacc = wacc / 100
    taxa_g = g / 100

    for i in range(1, anos + 1):
        receita *= (1 + taxa_g)
        fco = receita * margem
        fluxo_caixa.append(fco / ((1 + taxa_wacc) ** i))

    valor_terminal = (fluxo_caixa[-1] * (1 + taxa_g)) / (taxa_wacc - taxa_g)
    valor_terminal_presente = valor_terminal / ((1 + taxa_wacc) ** anos)

    valor_empresa = sum(fluxo_caixa) + valor_terminal_presente

    df_fluxo = pd.DataFrame({
        "Ano": list(range(1, anos + 1)) + ["Valor Terminal"],
        "Fluxo de Caixa": fluxo_caixa + [valor_terminal_presente]
    })

    return valor_empresa, df_fluxo
