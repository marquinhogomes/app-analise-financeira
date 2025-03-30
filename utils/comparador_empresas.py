import pandas as pd
from utils.calculadora_indicadores import calcular_indicadores

def comparar_empresas(lista_arquivos):
    resultados = []

    for nome, arquivo in lista_arquivos:
        try:
            df_dre = pd.read_excel(arquivo, sheet_name="DRE")
            df_bp = pd.read_excel(arquivo, sheet_name="BP")
            df_dfc = pd.read_excel(arquivo, sheet_name="DFC")

            indicadores = calcular_indicadores(df_dre, df_bp, df_dfc)
            ult = indicadores.iloc[-1].copy()
            ult['Empresa'] = nome
            resultados.append(ult)

        except Exception as e:
            print(f"Erro ao processar {nome}: {e}")

    df_comparativo = pd.DataFrame(resultados)
    colunas_ordem = ['Empresa', 'Ano', 'Receita Líquida', 'Lucro Líquido', 'EBITDA',
                     'ROE (%)', 'ROA (%)', 'Margem Bruta (%)', 'Margem EBITDA (%)', 'Margem Líquida (%)',
                     'Dívida/PL', 'Liquidez Corrente', 'Liquidez Seca']

    return df_comparativo[[col for col in colunas_ordem if col in df_comparativo.columns]]
