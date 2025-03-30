import streamlit as st
import pandas as pd
import plotly.express as px
from utils.calculadora_indicadores import calcular_indicadores
from utils.interpretador import gerar_diagnostico
from utils.parser_pdf import pdf_para_dataframes
from utils.valuation import calcular_fcd
from utils.comparador_empresas import comparar_empresas
from utils.simulador_impacto import simular_impacto
from utils.exportador_pdf import gerar_html_relatorio

st.set_page_config(page_title="Análise Financeira Automatizada", layout="wide")

# Sidebar
st.sidebar.title("Menu")
modo_entrada = st.sidebar.radio("Modo de Entrada", ["Exemplo", "Upload de Excel", "Upload de PDF", "Manual"])

# Dados de exemplo ou upload
if modo_entrada == "Exemplo":
    df_dre = pd.read_excel("data/exemplo_dre_bp_dfc.xlsx", sheet_name="DRE")
    df_bp = pd.read_excel("data/exemplo_dre_bp_dfc.xlsx", sheet_name="BP")
    df_dfc = pd.read_excel("data/exemplo_dre_bp_dfc.xlsx", sheet_name="DFC")
    nome_empresa = "Empresa Exemplo"

elif modo_entrada == "Upload de Excel":
    uploaded_file = st.sidebar.file_uploader("Faça upload do arquivo Excel", type="xlsx")
    if uploaded_file:
        df_dre = pd.read_excel(uploaded_file, sheet_name="DRE")
        df_bp = pd.read_excel(uploaded_file, sheet_name="BP")
        df_dfc = pd.read_excel(uploaded_file, sheet_name="DFC")
        nome_empresa = uploaded_file.name.split(".")[0]

elif modo_entrada == "Upload de PDF":
    pdf_file = st.sidebar.file_uploader("Faça upload do PDF", type="pdf")
    if pdf_file:
        df_dre, df_bp, df_dfc = pdf_para_dataframes(pdf_file)
        nome_empresa = pdf_file.name.split(".")[0]

elif modo_entrada == "Manual":
    st.warning("Modo manual em desenvolvimento.")
    st.stop()

# Exibir dados
with st.expander("Demonstrações Financeiras - Visualização", expanded=False):
    st.subheader("DRE")
    st.dataframe(df_dre)
    st.subheader("Balanço Patrimonial")
    st.dataframe(df_bp)
    st.subheader("DFC")
    st.dataframe(df_dfc)

# Cálculo de Indicadores
st.markdown("## Indicadores Financeiros")
indicadores = calcular_indicadores(df_dre, df_bp, df_dfc)
st.dataframe(indicadores.style.background_gradient(cmap='RdYlGn'))

# Gráficos
st.markdown("## Gráficos Interativos")
fig_receita = px.line(df_dre, x="Ano", y="Receita Líquida", title="Evolução da Receita Líquida")
st.plotly_chart(fig_receita, use_container_width=True)

fig_lucro = px.bar(df_dre, x="Ano", y="Lucro Líquido", title="Lucro Líquido por Ano")
st.plotly_chart(fig_lucro, use_container_width=True)

# Diagnóstico
st.markdown("## Diagnóstico Automático")
diag = gerar_diagnostico(indicadores, df_dre)
st.write(diag['texto'])
st.info(diag['alertas'])

# Valuation
st.markdown("## Valuation FCD")
valuation = None
with st.expander("Simulador de Valuation", expanded=False):
    receita_atual = st.number_input("Receita Atual", value=float(df_dre['Receita Líquida'].iloc[-1]), step=10000.0)
    margem_ebitda = st.slider("Margem EBITDA (%)", 5.0, 50.0, 20.0)
    wacc = st.slider("WACC (%)", 5.0, 20.0, 10.0)
    g = st.slider("Crescimento Perpétuo (g) (%)", 1.0, 10.0, 3.0)

    if st.button("Calcular Valuation"):
        valuation = calcular_fcd(receita_atual, margem_ebitda, wacc, g)
        valor, df_fluxo = valuation
        st.success(f"Valuation estimado da empresa: R$ {valor:,.2f}")
        st.dataframe(df_fluxo)

# Dashboard Executivo
st.markdown("## Dashboard Executivo")
with st.container():
    col1, col2, col3 = st.columns(3)
    col1.metric("Receita Líquida (Último Ano)", f"R$ {df_dre['Receita Líquida'].iloc[-1]:,.0f}")
    col2.metric("Lucro Líquido (Último Ano)", f"R$ {df_dre['Lucro Líquido'].iloc[-1]:,.0f}")
    col3.metric("EBITDA (Último Ano)", f"R$ {df_dre['EBITDA'].iloc[-1]:,.0f}")

    col4, col5, col6 = st.columns(3)
    col4.metric("ROE (%)", f"{indicadores['ROE (%)'].iloc[-1]:.2f}%")
    col5.metric("Dívida / PL", f"{indicadores['Dívida/PL'].iloc[-1]:.2f}")
    col6.metric("Liquidez Corrente", f"{indicadores['Liquidez Corrente'].iloc[-1]:.2f}")

    st.subheader("Resumo Diagnóstico")
    st.code(diag['texto'])
    st.warning(diag['alertas'])

# Comparativo entre empresas
st.markdown("## Comparar Empresas")
with st.expander("Comparar múltiplos arquivos Excel", expanded=False):
    arquivos = st.file_uploader("Selecione os arquivos (mesmo formato de DRE, BP, DFC)", type="xlsx", accept_multiple_files=True)
    nomes = []
    for i in range(len(arquivos)):
        nome = st.text_input(f"Nome da Empresa {i+1}", value=f"Empresa {i+1}")
        nomes.append(nome)

    if st.button("Comparar Empresas") and arquivos:
        lista = list(zip(nomes, arquivos))
        comparativo = comparar_empresas(lista)
        st.dataframe(comparativo)

        grafico = px.bar(comparativo, x="Empresa", y="ROE (%)", title="Comparativo de ROE (%)")
        st.plotly_chart(grafico, use_container_width=True)

# Simulador de Impacto Operacional
st.markdown("## Simulador de Impacto Operacional")
simulacao = None
with st.expander("Simule mudanças operacionais e veja os impactos", expanded=False):
    crescimento = st.slider("Crescimento da Receita (%)", -50.0, 100.0, 10.0)
    nova_margem = st.slider("Nova Margem EBITDA (%)", 5.0, 50.0, 20.0)
    dias_estoque = st.slider("Dias de Estoque", 0, 180, 60)
    dias_receber = st.slider("Dias a Receber", 0, 180, 45)
    dias_pagar = st.slider("Dias a Pagar", 0, 180, 30)

    if st.button("Rodar Simulação"):
        simulacao = simular_impacto(df_dre, df_bp, crescimento, nova_margem, dias_estoque, dias_receber, dias_pagar)
        st.metric("Receita Projetada", f"R$ {simulacao['Receita Projetada']:,.0f}")
        st.metric("EBITDA Projetado", f"R$ {simulacao['EBITDA Projetado']:,.0f}")
        st.metric("NCG Projetada", f"R$ {simulacao['NCG Projetada']:,.0f}")
        st.metric("FCO Estimado", f"R$ {simulacao['FCO Estimado']:,.0f}")

# Exportar HTML
st.markdown("## Exportar Relatório")
if st.button("Exportar Relatório em HTML"):
    html = gerar_html_relatorio(nome_empresa, df_dre, df_bp, df_dfc, indicadores, diag, valuation, simulacao)
    st.download_button("📄 Baixar HTML", data=html, file_name="relatorio_analise.html", mime="text/html")
