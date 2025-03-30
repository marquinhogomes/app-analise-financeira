def simular_impacto(df_dre, df_bp, crescimento_receita_pct, nova_margem_pct, dias_estoque=None, dias_receber=None, dias_pagar=None):
    receita_base = df_dre['Receita Líquida'].iloc[-1]
    margem_base = df_dre['EBITDA'].iloc[-1] / receita_base
    contas_receber = df_bp['Contas a Receber'].iloc[-1]
    estoques = df_bp['Estoques'].iloc[-1]
    fornecedores = df_bp['Fornecedores'].iloc[-1]
    cpv = receita_base - df_dre['Lucro Bruto'].iloc[-1]

    receita_nova = receita_base * (1 + crescimento_receita_pct / 100)
    margem_nova = nova_margem_pct / 100
    ebitda_novo = receita_nova * margem_nova

    faturamento_dia = receita_nova / 360
    cpv_dia = cpv / 360

    contas_receber_novo = faturamento_dia * dias_receber if dias_receber else contas_receber
    estoques_novo = cpv_dia * dias_estoque if dias_estoque else estoques
    fornecedores_novo = cpv_dia * dias_pagar if dias_pagar else fornecedores

    ncg_nova = contas_receber_novo + estoques_novo - fornecedores_novo
    fco_estimado = ebitda_novo - (ncg_nova - (contas_receber + estoques - fornecedores))

    resultado = {
        "Receita Projetada": receita_nova,
        "EBITDA Projetado": ebitda_novo,
        "NCG Projetada": ncg_nova,
        "FCO Estimado": fco_estimado,
        "Contas a Receber": contas_receber_novo,
        "Estoques": estoques_novo,
        "Fornecedores": fornecedores_novo
    }

    return resultado
