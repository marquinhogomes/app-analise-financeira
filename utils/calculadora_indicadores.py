import pandas as pd

def calcular_indicadores(dre: pd.DataFrame, bp: pd.DataFrame, dfc: pd.DataFrame) -> pd.DataFrame:
    anos = dre['Ano'].tolist() if 'Ano' in dre.columns else [2023]
    indicadores = pd.DataFrame({"Ano": anos})

    def safe_div(num, den):
        try:
            return num / den if den != 0 else 0
        except:
            return 0

    def get(df, col):
        import streamlit as st
        if col in df.columns:
            return df[col]
        else:
            st.warning(f"⚠️ Atenção: coluna '{col}' não encontrada. Assumindo valor 0.")
            return pd.Series([0] * len(df))

    indicadores['Liquidez Corrente'] = safe_div(get(bp, 'Ativo Circulante'), get(bp, 'Passivo Circulante'))
    indicadores['Liquidez Seca'] = safe_div(get(bp, 'Ativo Circulante') - get(bp, 'Estoques'), get(bp, 'Passivo Circulante'))
    indicadores['Margem Bruta (%)'] = safe_div(get(dre, 'Lucro Bruto'), get(dre, 'Receita Líquida')) * 100
    indicadores['Margem EBITDA (%)'] = safe_div(get(dre, 'EBITDA'), get(dre, 'Receita Líquida')) * 100
    indicadores['Margem Líquida (%)'] = safe_div(get(dre, 'Lucro Líquido'), get(dre, 'Receita Líquida')) * 100
    indicadores['ROE (%)'] = safe_div(get(dre, 'Lucro Líquido'), get(bp, 'Patrimônio Líquido')) * 100
    indicadores['ROA (%)'] = safe_div(get(dre, 'Lucro Líquido'), get(bp, 'Ativo Total') if 'Ativo Total' in bp.columns else get(bp, 'Ativo Circulante') + get(bp, 'Ativo Não Circulante')) * 100
    indicadores['Dívida/PL'] = safe_div(get(bp, 'Passivo Circulante') + get(bp, 'Passivo Não Circulante'), get(bp, 'Patrimônio Líquido'))
    indicadores['Cobertura de Juros'] = safe_div(get(dre, 'EBIT'), get(dre, 'Despesas Financeiras'))
    indicadores['Capital de Giro (CG)'] = get(bp, 'Ativo Circulante') - get(bp, 'Passivo Circulante')
    indicadores['Necessidade de Capital de Giro (NCG)'] = get(bp, 'Contas a Receber de Clientes') + get(bp, 'Estoques') - get(bp, 'Fornecedores')
    indicadores['Folga ou Déficit de Caixa'] = indicadores['Capital de Giro (CG)'] - indicadores['Necessidade de Capital de Giro (NCG)']
    indicadores['Geração de Caixa Operacional (FCO)'] = get(dfc, 'FCO')

    return indicadores
