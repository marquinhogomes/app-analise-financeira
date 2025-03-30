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
            table {{ width: 100%; border-collaps...
    }
  ]
}
