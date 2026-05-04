---
name: skill_exemplo_01_analisar-planilha-excel
description: Analise exploratoria estruturada de planilha Excel desconhecida
trigger: O usuario pede para "entender", "analisar" ou "dar uma olhada" em um arquivo .xlsx/.xls que voce nunca viu
version: 1
last_updated: 2026-04-22
uses_count: 0
---

# Analise exploratoria de planilha Excel

## Quando usar

- Usuario entrega um arquivo `.xlsx` e pede algo como "da uma olhada" ou "o que tem aqui"
- Voce precisa decidir como estruturar um pipeline de processamento sem conhecer os dados
- Existem multiplas abas e voce nao sabe qual importa

## Quando NAO usar

- Arquivo tem menos de 10 linhas — so abra manualmente
- Usuario ja sabe exatamente o que quer — pule direto para a transformacao

## Procedimento

### 1. Descobrir as abas

```python
import pandas as pd
xl = pd.ExcelFile('caminho/arquivo.xlsx')
print('Abas:', xl.sheet_names)
for name in xl.sheet_names:
    df_sample = xl.parse(name, nrows=5)
    print(f'\n--- {name} ---')
    print(f'Shape: {xl.parse(name).shape}')
    print(f'Colunas: {list(df_sample.columns)}')
```

### 2. Para cada aba relevante

```python
df = pd.read_excel('arquivo.xlsx', sheet_name='aba')
print(df.info())              # tipos + nulos
print(df.describe())          # estatisticas basicas numericas
print(df.head(10))            # primeiras linhas
print('Duplicatas:', df.duplicated().sum())
```

### 3. Identificar chaves e categorias

- **Colunas com texto curto repetitivo** → provavelmente categoricas (listar top 10 com `value_counts()`)
- **Colunas com ID numerico unico** → provavelmente chave primaria (verificar `is_unique`)
- **Colunas de data** → verificar range (`min` e `max`)
- **Colunas monetarias** → verificar moeda e formato (virgula? ponto? R$?)

### 4. Registrar achados no historico

No `historico.md` do projeto atual:

```markdown
- [discovery] Planilha arquivo.xlsx tem 3 abas: Vendas (12450 linhas), Clientes (3120 linhas), Produtos (856 linhas)
- [discovery] Coluna PRECO em Vendas vem com virgula (formato BR) — precisa converter antes de somar
- [decision] Usar aba Vendas como fonte primaria; Clientes e Produtos servem de enriquecimento via JOIN
```

### 5. Propor proximo passo

Com base nos achados, sugira ao usuario:

- Qual aba usar como base
- Quais conversoes/limpezas sao necessarias
- Quais perguntas os dados sao capazes de responder

## Sinais de que precisa melhorar

- Planilha muito grande (> 500k linhas) → este procedimento fica lento; adicionar suporte a `chunksize`
- Planilha com formulas → pd.read_excel carrega valores calculados, mas se der erro considerar `openpyxl.load_workbook(data_only=True)`
- Planilha com celulas mescladas → pode corromper shape; detectar e alertar usuario

## Historico de melhoria

- v1 (2026-04-22): versao inicial (exemplo do kit beta)
