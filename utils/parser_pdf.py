import fitz  # PyMuPDF
import pandas as pd
import re
import io
import streamlit as st

def extrair_tabelas_pdf(pdf_file) -> dict:
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    texto_total = "\n".join(p.get_text() for p in doc)
    linhas = texto_total.split('\n')
    dre, bp, dfc = [], [], []

    for linha in linhas:
        l = linha.lower().strip()
        l = re.sub(r"\s{2,}", " ", l)  # Remove espaços em excesso

        # Verifica termos da DRE
        if any(x in l for x in [
            'receita líquida', 'lucro bruto', 'ebitda', 'lucro líquido',
            'resultado antes', 'receitas/despesas operacionais',
            'despesas operacionais', 'custo dos produtos', 'resultado operacional',
            'deduções da receita', 'receita bruta', 'despesas financeiras']):
            dre.append(linha)

        # Verifica termos do Balanço
        elif any(x in l for x in [
            'ativo circulante', 'passivo circulante', 'estoques',
            'patrimônio líquido', 'fornecedores', 'contas a receber',
            'ativo não circulante', 'obrigações', 'capital social',
            'investimentos', 'imobilizado', 'passivo não circulante']):
            bp.append(linha)

        # Verifica termos da DFC
        elif any(x in l for x in [
            'fluxo de caixa', 'fco', 'fluxo operacional',
            'atividades de financiamento', 'variação de caixa',
            'caixa e equivalentes', 'fci', 'fcf']):
            dfc.append(linha)

    if st.sidebar.checkbox("🔍 Ver texto bruto do PDF extraído"):
        st.text_area("Texto extraído do PDF", texto_total, height=300)

    if st.sidebar.checkbox("🔍 Visualizar linhas classificadas"):
        st.write("**🔹 DRE:**", dre)
        st.write("**🔸 Balanço Patrimonial:**", bp)
        st.write("**🔻 DFC:**", dfc)

    return {'dre_raw': dre, 'bp_raw': bp, 'dfc_raw': dfc, 'texto_total': texto_total}

def processar_valores_extracao(lista_raw):
    dados = {}
    for linha in lista_raw:
        linha = re.sub(r"\s{2,}", " ", linha.strip())
        match = re.search(r'([A-Za-zçãéêõáíóúâôûÃÕÊÂÉÍÓÚ\s\(\)\-/]+)[\s:\-–=]+([\d\.\,]+)$', linha)
        if match:
            chave = match.group(1).strip().title()
            try:
                valor = float(match.group(2).replace('.', '').replace(',', '.'))
                dados[chave] = valor
            except ValueError:
                st.warning(f"Não foi possível converter valor da linha: '{linha}'")
    return dados

def aplicar_mapeamento_colunas(df, mapeamento):
    colunas_lower = {col.lower(): col for col in df.columns}
    for col_final, alternativas in mapeamento.items():
        for alt in alternativas:
            alt_lower = alt.lower()
            if alt_lower in colunas_lower:
                df.rename(columns={colunas_lower[alt_lower]: col_final}, inplace=True)
                break

def pdf_para_dataframes(pdf_file):
    raw = extrair_tabelas_pdf(pdf_file)
    ano = 2023
    dre_dict = processar_valores_extracao(raw['dre_raw'])
    bp_dict = processar_valores_extracao(raw['bp_raw'])
    dfc_dict = processar_valores_extracao(raw['dfc_raw'])

    dre_df = pd.DataFrame([{**dre_dict, 'Ano': ano}])
    bp_df = pd.DataFrame([{**bp_dict, 'Ano': ano}])
    dfc_df = pd.DataFrame([{**dfc_dict, 'Ano': ano, 'FCO': dfc_dict.get('FCO', 0)}])

    return dre_df, bp_df, dfc_df
