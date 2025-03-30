import pandas as pd

def calcular_indicadores(dre: pd.DataFrame, bp: pd.DataFrame, dfc: pd.DataFrame) -> pd.DataFrame:
    anos = dre['Ano']
    indicadores = pd.DataFrame({"Ano": anos})

    indicadores['Liquidez Corrente'] = bp['Ativo Circulante'] / bp['Passivo Circulante']
    indicadores['Liquidez Seca'] = (bp['Ativo Circulante'] - bp['Estoques']) / bp['Passivo Circulante']
    indicadores['Margem Bruta (%)'] = (dre['Lucro Bruto'] / dre['Receita Líquida']) * 100
    indicadores['Margem EBITDA (%)'] = (dre['EBITDA'] / dre['Receita Líquida']) * 100
    indicadores['Margem Líquida (%)'] = (dre['Lucro Líquido'] / dre['Receita Líquida']) * 100
    indicadores['ROE (%)'] = (dre['Lucro Líquido'] / bp['Patrimônio Líquido']) * 100
    indicadores['ROA (%)'] = (dre['Lucro Líquido'] / bp['Ativo Total']) * 100
    indicadores['Dívida/PL'] = bp['Dívida Bruta'] / bp['Patrimônio Líquido']
    indicadores['Cobertura de Juros'] = dre['EBIT'] / dre['Despesa Financeira']
    indicadores['Capital de Giro'] = bp['Ativo Circulante'] - bp['Passivo Circulante']
    indicadores['NCG'] = bp['Contas a Receber'] + bp['Estoques'] - bp['Fornecedores']
    indicadores['Folga/Déficit de Caixa'] = indicadores['Capital de Giro'] - indicadores['NCG']
    indicadores['FCO'] = dfc['FCO']

    return indicadores.round(2)
