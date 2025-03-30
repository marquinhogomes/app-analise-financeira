def gerar_diagnostico(indicadores, dre):
    texto = ""
    alertas = []
    dados = indicadores.iloc[-1]
    ano = dados['Ano']
    lucro_liquido = dre['Lucro Líquido'].iloc[-1]

    if dados['FCO'] < 0:
        alertas.append(f"🔴 Fluxo de Caixa Operacional negativo em {ano}")
    if dados['NCG'] > dados['Capital de Giro']:
        alertas.append(f"🟠 Necessidade de Capital de Giro maior que o Capital disponível em {ano}")
    if dados['Cobertura de Juros'] < 1.5:
        alertas.append(f"🔴 Cobertura de Juros inferior a 1,5x em {ano} (risco de inadimplência)")
    if dados['Liquidez Corrente'] < 1:
        alertas.append(f"🔴 Liquidez Corrente inferior a 1,0 em {ano}")
    if dados['FCO'] < 0 and lucro_liquido > 0:
        alertas.append("🟡 Lucro contábil positivo, mas FCO negativo (lucro não recorrente?)")

    if dados['FCO'] > 0:
        texto += f"✅ A empresa gerou caixa operacional em {ano}.\n"
    if dados['Margem EBITDA (%)'] > 20:
        texto += "✅ Boa margem operacional (EBITDA > 20%)\n"
    if dados['ROE (%)'] > 15:
        texto += "✅ ROE acima de 15% - bom retorno sobre o capital próprio.\n"
    if dados['Dívida/PL'] < 1:
        texto += "✅ Baixa alavancagem (Dívida/PL < 1,0)\n"

    if not alertas:
        alertas.append("🟢 Nenhum alerta crítico identificado no último ano.")

    return {"texto": texto.strip(), "alertas": "\n".join(alertas)}

