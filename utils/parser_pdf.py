import fitz  # PyMuPDF
import pandas as pd
import re
import io

def extrair_tabelas_pdf(pdf_file) -> dict:
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    texto_total = "\n".join(p.get_text() for p in doc)
    linhas = texto_total.split('\n')
    dre, bp, dfc = [], [], []

    for linha in linhas:
        l = linha.lower()
        if any(x in l for x in ['receita líquida', 'lucro bruto', 'ebitda', 'resultado financeiro', 'lucro líquido']):
            dre.append(linha)
        elif any(x in l for x in ['ativo circulante', 'passivo circulante', 'estoques', 'patrimônio líquido', 'fornecedores', 'contas a receber']):
            bp.append(linha)
        elif any(x in l for x in ['fluxo de caixa operacional', 'fco', 'atividades de financiamento']):
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

def pdf_para_dataframes(pdf_file):
    raw = extrair_tabelas_pdf(pdf_file)
    ano = 2023
    dre_dict = processar_valores_extracao(raw['dre_raw'])
    bp_dict = processar_valores_extracao(raw['bp_raw'])
    dfc_dict = processar_valores_extracao(raw['dfc_raw'])

    dre_df = pd.DataFrame([{**dre_dict, 'Ano': ano}])
    bp_df = pd.DataFrame([{**bp_dict, 'Ano': ano}])
    dfc_df = pd.DataFrame([{**dfc_dict, 'Ano': ano, 'FCO': dfc_dict.get('FCO', 0)}])

    # Mapas de renomeação
    renomear_bp = {
        'Ativo Circulante': ['Ativo Circulante', 'Total Ativo Circulante'],
        'Passivo Circulante': ['Passivo Circulante', 'Total Passivo Circulante'],
        'Patrimônio Líquido': ['Patrimônio Líquido', 'PL', 'Patrimonio Liquido'],
        'Fornecedores': ['Fornecedores'],
        'Contas a Receber': ['Contas a Receber'],
        'Estoques': ['Estoques']
    }

    # Renomear colunas do bp_df conforme mapeamento
    for col_final, alternativas in renomear_bp.items():
        for alt in alternativas:
            if alt in bp_df.columns:
                bp_df.rename(columns={alt: col_final}, inplace=True)
                
    return dre_df, bp_df, dfc_df
