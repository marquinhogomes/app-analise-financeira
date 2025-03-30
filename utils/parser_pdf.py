import fitz
import pandas as pd
import re

def extrair_tabelas_pdf(path_pdf: str) -> dict:
    doc = fitz.open(path_pdf)
    texto_total = "".join(p.get_text() for p in doc)
    linhas = texto_total.split('\n')
    dre, bp, dfc = [], [], []

    for linha in linhas:
        l = linha.lower()
        if 'receita líquida' in l or 'lucro bruto' in l or 'ebitda' in l:
            dre.append(linha)
        elif 'ativo circulante' in l or 'passivo circulante' in l or 'estoques' in l:
            bp.append(linha)
        elif 'fluxo de caixa operacional' in l or 'fco' in l:
            dfc.append(linha)

    return {'dre_raw': dre, 'bp_raw': bp, 'dfc_raw': dfc, 'texto_total': texto_total}

def processar_valores_extracao(lista_raw):
    dados = {}
    for linha in lista_raw:
        partes = re.split(r':|-', linha)
        if len(partes) >= 2:
            chave = partes[0].strip().title()
            valor = re.findall(r"[\d\.\,]+", partes[-1])
            if valor:
                valor_limpo = float(valor[0].replace('.', '').replace(',', '.'))
                dados[chave] = valor_limpo
    return dados

def pdf_para_dataframes(path_pdf: str):
    raw = extrair_tabelas_pdf(path_pdf)
    ano = 2023
    dre_dict = processar_valores_extracao(raw['dre_raw'])
    bp_dict = processar_valores_extracao(raw['bp_raw'])
    dfc_dict = processar_valores_extracao(raw['dfc_raw'])

    dre_df = pd.DataFrame([{**dre_dict, 'Ano': ano}])
    bp_df = pd.DataFrame([{**bp_dict, 'Ano': ano}])
    dfc_df = pd.DataFrame([{**dfc_dict, 'Ano': ano, 'FCO': dfc_dict.get('FCO', 0)}])
    return dre_df, bp_df, dfc_df
