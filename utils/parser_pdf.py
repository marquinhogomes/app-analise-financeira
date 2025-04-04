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

    # Mapeamento de colunas
    mapeamento_bp = {
        'Ativo Circulante': ['Ativo Circulante', 'Total Ativo Circulante'],
        'Disponível': ['Disponivel', 'Caixa', 'Bancos Conta Movimento', 'Numerarios'],
        'Aplicações Financeiras': ['Aplicacoes Financeiras', 'Aplicacoes Financeiras Liquidez Imediata'],
        'Clientes': ['Clientes', 'Duplicatas A Receber'],
        'Outros Créditos': ['Outros Creditos'],
        'Adiantamentos a Fornecedores': ['Adiantamentos A Fornecedores'],
        'Tributos a Recuperar': ['Tributos A Recuperar / Compensar'],
        'Estoques': ['Estoques', 'Mercadorias Para Revenda'],
        'Ativo Não Circulante': ['Ativo Nao Circulante'],
        'Realizável a Longo Prazo': ['Ativo Realizavel A Longo Prazo'],
        'Depósitos Judiciais': ['Depositos Judiciais'],
        'Imobilizado': ['Imobilizado'],
        'Bens Imóveis': ['Bens Imoveis'],
        'Bens Móveis': ['Bens Moveis'],
        'Imobilizado em Andamento': ['Imobilizado Em Andamento', 'Bens Adq. Consorcio- A Contemplar'],
        'Depreciações Acumuladas': ['Depreciacoes Acumuladas Bens Imoveis', 'Depr.Acum.de Moveis E Utensilios', 'Depr.Acum.equip.Tecnologia Inform.', 'Depr. Acumuladas De Veiculos', 'Depr. Acumuladas Maq E Equiptos', 'Depr. Acumuladas Instalacoes'],
        'Operações com Materiais Próprios': ['Operacoes Com Materiais Proprios'],
        'Operações com Materiais de Terceiros': ['Operacoes Com Materiais De Terceiros'],
        'Passivo Circulante': ['Passivo Circulante', 'Exigivel A Curto Prazo'],
        'Empréstimos e Financiamentos CP': ['Emprestimos E Financiamentos'],
        'Fornecedores': ['Fornecedores', 'Fornecedores Nacionais'],
        'Obrigações Tributárias': ['Obrigacoes Tributarias', 'Impostos E Contribuicoes A Recolher'],
        'Obrigações Trabalhistas e Previdenciárias': ['Obrigacoes Trabalhistas E Previdenciaria'],
        'Provisões': ['Provisoes'],
        'Outras Obrigações': ['Outras Obrigacoes', 'Contas A Pagar'],
        'Passivo Não Circulante': ['Passivo Nao Circulante', 'Passivo Exigivel A Longo Prazo'],
        'Empréstimos e Financiamentos LP': ['Emprestimos De Socios', 'Outros Debitos Socios, Administradores'],
        'Outras Obrigações LP': ['Outras Contas A Pagar'],
        'Patrimônio Líquido': ['Patrimonio Liquido'],
        'Capital Social': ['Capital Social', 'Capital Subscrito'],
        'Reservas de Lucros': ['Reservas De Lucros'],
        'Prejuízos Acumulados': ['Prejuizos Acumulados']
    }
    mapeamento_dre = {
        'Receita Bruta': ['Receitas', 'Receita Da Prestacao De Servicos', 'Venda De Mercadorias No Mercado Externo'],
        'Cancelamentos e Devoluções': ['Cancelamento E Devolucoes', 'Dev. Venda Mercadorias Mercado Ext'],
        'Descontos Incondicionais': ['Descontos Incondicionais'],
        'Impostos sobre Vendas': ['Impostos Incidentes S/ Vendas', 'ICMS'],
        'Juros e Descontos Obtidos': ['Juros E Descontos', 'Juros De Aplicacoes Financeiras', 'Juros Ativos', 'Descontos Financeiros Obtidos'],
        'Variações Cambiais Ativas': ['Variacoes Monetarias', 'Variacoes Cambiais Ativas'],
        'Receitas Não Operacionais': ['Resultados Nao Operacionais', 'Outras Receitas Nao Operacionais'],
        'Resultado Alienação Imobilizado': ['Resultado Positivo Na Alienacao Do Imobi'],
        'Material Aplicado': ['Material Aplicado', 'Consumo De Embalagens'],
        'CPV': ['Custo Dos Produtos Vendidos'],
        'Despesas com Pessoal': ['Despesas Com Pessoal', 'Salarios E Ordenados', 'Pro-Labore', '13o Salario', 'Ferias', 'INSS', 'FGTS', 'Indenizacoes E Aviso Previo', 'Assistencia Medica', 'Horas Extras', 'Adicional Noturno', 'EPI - Equipto De Protecao Individual', 'Vale Alimentacao', 'Vale Transporte', 'Cesta Basica', 'Ajuda De Custo'],
        'Comissões sobre Vendas': ['Comissoes Sobre Vendas', 'Comissoes'],
        'Propaganda e Publicidade': ['Propaganda E Publicidade', 'Amostras Gratis'],
        'Despesas com Entrega': ['Despesas Com Entrega', 'Fretes Nacionais', 'Fretes Internacionais', 'Manutencao De Veiculos', 'Despesas Aduaneiras', 'Despesas Portuarias'],
        'Despesas com Viagens': ['Despesas C/ Viagens E Representacoes', 'Viagens E Representacoes', 'Refeicoes'],
        'Despesas Gerais': ['Despesas Gerais', 'Alugueis E Condominios', 'Manutencao E Reparos', 'Telefone', 'Despesas Postais E Telegraficas', 'Agua E Esgoto', 'Servicos Prestados Por Terceiros', 'Seguros', 'Locacao De Veiculos E Equipamentos', 'Energia Eletrica', 'IPVA E Licenciamento De Veiculos', 'Material De Escritorio', 'Material De Limpeza', 'Copa, Cozinha E Refeitorio', 'Combustiveis E Lubrificantes', 'Despesas Com Informatica', 'Bens De Pequeno Valor', 'Despesas Diversas', 'Manutencao De Maquinas E Equipamentos', 'Estacionamento', 'Multas De Transito', 'Assessoria Contabil'],
        'Depreciação e Amortização': ['Depreciacao E Amortizacao'],
        'Despesas Judiciais e Legais': ['Despesas Legais E Judiciais'],
        'Taxas Diversas': ['Taxas Diversas'],
        'Créditos de PIS/Cofins': ['Creditos De PIS', 'Creditos De Cofins'],
        'Despesas Financeiras': ['Despesas Financeiras', 'Variacoes Cambiais Passivas', 'Atualizacao De Impostos Atrasados', 'Juros E Comissoes Bancarias', 'IOF'],
        'Resultado Alienação Imobilizado Negativo': ['Resultado Negativo Na Alienacao Do Imobi'],
        'Lucro Líquido': ['Lucro']
    }
    mapeamento_dfc = {
        'FCO': ['Fluxo De Caixa Operacional', 'FCO', 'Fluxo Operacional'],
        'FCI': ['Fluxo De Caixa De Investimento', 'FCI', 'Atividades De Investimento'],
        'FCF': ['Fluxo De Caixa De Financiamento', 'FCF', 'Atividades De Financiamento'],
        'Lucro Líquido': ['Lucro Líquido Do Exercício'],
        'Depreciações': ['Depreciações'],
        'Resultado Venda Imobilizado': ['Resultado Na Venda De Imobilizado'],
        'Ajustes de Exercícios Anteriores': ['Ajuste De Exercicio Anterior'],
        'Contas a Receber': ['Contas A Receber De Clientes'],
        'Impostos a Recuperar': ['Impostos A Recuperar'],
        'Adiantamento a Fornecedores': ['Adiantamento De Fornecedores'],
        'Estoques': ['Estoque'],
        'Outros Créditos': ['Outros Créditos'],
        'Despesas Antecipadas': ['Despesas Antecipadas'],
        'Fornecedores': ['Fornecedores'],
        'Obrigações Trabalhistas': ['Obrigações Trabalhistas E Sociais'],
        'Impostos a Recolher': ['Impostos E Contribuições A Recolher'],
        'Outras Contas a Pagar': ['Outras Contas A Pagar'],
        'Aquisicao Imobilizado': ['Aquisição De Bens Do Ativo Imobilizado'],
        'Venda Imobilizado': ['Venda De Ativo Imobilizado'],
        'Emprestimos e Financiamentos': ['Empréstimos E Financiamentos'],
        'Empresas Ligadas': ['Empresas Ligadas - Ativo'],
        'Variação De Caixa': ['Aumento / (Redução) Líquido De Caixa E Equivalente De Caixa'],
        'Caixa Inicial': ['Caixa E Equivalente De Caixa No Início Do Período'],
        'Caixa Final': ['Caixa E Equivalente De Caixa No Final Do Período']
    }

    aplicar_mapeamento_colunas(bp_df, mapeamento_bp)
    aplicar_mapeamento_colunas(dre_df, mapeamento_dre)
    aplicar_mapeamento_colunas(dfc_df, mapeamento_dfc)

    # Preenchimento padrão para evitar KeyError na análise posterior
    colunas_obrigatorias_bp = [
        'Ativo Circulante', 'Passivo Circulante', 'Estoques', 'Caixa e equivalentes de caixa',
        'Contas a receber de clientes', 'Impostos a recuperar', 'Adiantamento a fornecedores e outros',
        'Outros créditos', 'Devedores cotistas', 'Ativo não circulante', 'Outros valores a receber',
        'Imobilizado', 'Intangível', 'Fornecedores e outras obrigações', 'Empréstimos e financiamentos',
        'Duplicatas Descontadas', 'Obrigações trabalhistas com provisoes', 'Impostos a recolher',
        'Adiantamento de clientes', 'Parcelamento de impostos', 'Empréstimos e financiamentos giro e Maq.',
        'Fornecedores Não Circulante', 'Capital social', 'Reserva de lucros', 'Patrimônio líquido'
    ]
    colunas_obrigatorias_dre = [
        'Receita Bruta', 'Receita Líquida', 'Custo dos produtos vendidos', 'Lucro Bruto',
        'Vendas', 'Gerais e administrativas', 'Receitas \(despesas\) operacionais líquidas',
        'Lucro Operacional', 'Receitas financeiras', 'Despesas financeiras',
        'Resultado antes dos tributos sobre os lucros', 'Receitas / Despesas Não operacionais',
        'Imposto de renda e contribuição social', 'Lucro \(prejuízo\) líquido do período'
    ]
    colunas_obrigatorias_dfc = [
        'FCO', 'FCI', 'FCF', 'Lucro Líquido', 'Depreciações',
        'Resultado Venda Imobilizado', 'Ajustes de Exercícios Anteriores', 'Contas a Receber',
        'Impostos a Recuperar', 'Adiantamento a Fornecedores', 'Estoques', 'Outros Créditos',
        'Despesas Antecipadas', 'Fornecedores', 'Obrigações Trabalhistas', 'Impostos a Recolher',
        'Outras Contas a Pagar', 'Aquisicao Imobilizado', 'Venda Imobilizado',
        'Emprestimos e Financiamentos', 'Empresas Ligadas', 'Variação De Caixa',
        'Caixa Inicial', 'Caixa Final'
    ]

    for col in colunas_obrigatorias_bp:
        if col not in bp_df.columns:
            bp_df[col] = [0.0]

    for col in colunas_obrigatorias_dre:
        if col not in dre_df.columns:
            dre_df[col] = [0.0]

    for col in colunas_obrigatorias_dfc:
        if col not in dfc_df.columns:
            dfc_df[col] = [0.0]

    return dre_df, bp_df, dfc_df
