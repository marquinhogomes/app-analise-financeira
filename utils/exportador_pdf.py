from weasyprint import HTML
import datetime
import tempfile
import os

def gerar_html_relatorio(nome_empresa, df_dre, df_bp, df_dfc, indicadores, diagnostico, valuation=None, simulacao=None):
    hoje = datetime.date.today().strftime("%d/%m/%Y")

    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            h1, h2 {{ color: #1f4e79; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
            th, td {{ border: 1px solid #ccc; padding: 5px; text-align: right; }}
            th {{ background-color: #f0f0f0; }}
            .section {{ margin-bottom: 40px; }}
        </style>
    </head>
    <body>
        <h1>Relatório de Análise Financeira</h1>
        <p><b>Empresa:</b> {nome_empresa}<br><b>Data:</b> {hoje}</p>

        <div class="section">
            <h2>DRE</h2>
            {df_dre.to_html(index=False)}
        </div>

        <div class="section">
            <h2>Balanço Patrimonial</h2>
            {df_bp.to_html(index=False)}
        </div>

        <div class="section">
            <h2>DFC</h2>
            {df_dfc.to_html(index=False)}
        </div>

        <div class="section">
            <h2>Indicadores Financeiros</h2>
            {indicadores.to_html(index=False)}
        </div>

        <div class="section">
            <h2>Diagnóstico</h2>
            <p>{diagnostico['texto'].replace('\\n', '<br>')}</p>
            <p style="color: red;">{diagnostico['alertas'].replace('\\n', '<br>')}</p>
        </div>
    """

    if valuation:
        valor, df_fluxo = valuation
        html += f"""
        <div class="section">
            <h2>Valuation</h2>
            <p><b>Valuation Estimado:</b> R$ {valor:,.2f}</p>
            {df_fluxo.to_html(index=False)}
        </div>
        """

    if simulacao:
        html += "<div class='section'><h2>Simulação de Impacto Operacional</h2><table>"
        for k, v in simulacao.items():
            html += f"<tr><td>{k}</td><td>R$ {v:,.2f}</td></tr>"
        html += "</table></div>"

    html += "</body></html>"
    return html

def salvar_pdf(html_content, nome_arquivo="relatorio_analise.pdf"):
    caminho_pdf = os.path.join(tempfile.gettempdir(), nome_arquivo)
    HTML(string=html_content).write_pdf(caminho_pdf)
    return caminho_pdf
