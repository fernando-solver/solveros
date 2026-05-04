---
name: skill_pessoal_05_visao-mes
description: Gera HTML consolidado do mes — projetos, horas por area, evolucao de objetivos, calendario de atividades
trigger: O usuario pede "como foi meu mes", "visao do mes", "fechamento mensal" ou "panorama do que andei fazendo"
version: 1
last_updated: 2026-05-03
uses_count: 0
---

# Visao consolidada do mes

## Quando usar

- Final do mes (ultimos dias)
- Comeco do mes seguinte (revisao do que passou)
- Antes de uma 1:1 mensal ou retrospectiva pessoal
- Quando voce precisa "provar pra si mesmo" o que andou fazendo

## Quando NAO usar

- Workspace com menos de 30 dias de uso — sem dado suficiente
- Pedido genérico "como vai" sem contexto temporal — use
  `skill_pessoal_02_revisar-semana` que cobre 7 dias

## Procedimento

### 1. Define janela do mes

```python
from datetime import datetime, timedelta
from pmo_db import query_activities, objetivo_list, session_count

# Mes corrente OU mes anterior se ja virou
hoje = datetime.now()
if hoje.day < 5:
    # Comeco do mes — usa mes anterior
    primeiro = (hoje.replace(day=1) - timedelta(days=1)).replace(day=1)
else:
    primeiro = hoje.replace(day=1)

ultimo = (primeiro.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

print(f'Janela: {primeiro:%Y-%m-%d} a {ultimo:%Y-%m-%d}')
```

### 2. Coleta dados

```python
atividades = query_activities(
    "date >= ? AND date <= ?",
    (primeiro.strftime('%Y-%m-%d'), ultimo.strftime('%Y-%m-%d')),
    1000
)

# Distribui
from collections import Counter, defaultdict
por_projeto = Counter(a['project'] for a in atividades)
por_tipo = Counter(a['tipo'] for a in atividades)
por_dia = Counter(a['date'] for a in atividades)
```

### 3. Cruza com objetivos

```python
objetivos = objetivo_list()
for obj in objetivos:
    relacionadas = [a for a in atividades
                    if obj['descricao'].lower() in a['description'].lower()]
    obj['atividades_no_mes'] = len(relacionadas)
```

### 4. Gera HTML

Use `pmo_dashboard.py` se existir; se nao, gera HTML minimo inline.

Template do HTML:

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <title>Visao do mes — <MES/ANO></title>
  <style>
    /* CSS minimo: serif pra titulo, mono pra numeros */
    body { font-family: Georgia, serif; max-width: 800px; margin: 40px auto; padding: 0 20px; }
    .kpi { font-family: 'JetBrains Mono', monospace; font-size: 2em; }
    .heat { display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; }
    .heat .dia { aspect-ratio: 1; background: #eee; }
    .heat .dia.ativo { background: #2c5282; }
  </style>
</head>
<body>
  <h1>Visao do mes — <MES/ANO></h1>

  <section>
    <h2>Numeros</h2>
    <p class="kpi"><N> atividades</p>
    <p class="kpi"><M> projetos tocados</p>
    <p class="kpi"><X> sessoes de trabalho</p>
  </section>

  <section>
    <h2>Calendario</h2>
    <div class="heat">
      <!-- 1 div por dia, classe 'ativo' se houve atividade -->
    </div>
  </section>

  <section>
    <h2>Top projetos</h2>
    <ol>
      <li>... (top 5 por numero de atividades)</li>
    </ol>
  </section>

  <section>
    <h2>Objetivos</h2>
    <ul>
      <!-- 1 li por objetivo, com % de atividades alinhadas -->
    </ul>
  </section>

  <section>
    <h2>Insights</h2>
    <ul>
      <li>Dia mais produtivo: <data> com <N> atividades</li>
      <li>Projeto que mais cresceu: <nome></li>
      <li>Projeto abandonado: <nome> (sem atividade ha <N> dias)</li>
    </ul>
  </section>
</body>
</html>
```

### 5. Salva e abre

```python
from pathlib import Path
import webbrowser

destino = Path(f'saidas/visao_mes_{primeiro:%Y-%m}.html')
destino.write_text(html, encoding='utf-8')

webbrowser.open(str(destino.absolute()))
```

### 6. Devolve ao usuario

```
[OK] Visao de <MES/ANO> gerada.

<N> atividades em <M> projetos.
Top 3: <p1>, <p2>, <p3>.

HTML aberto no navegador: <caminho>
```

## Output esperado

HTML em `saidas/visao_mes_<YYYY-MM>.html` aberto no navegador + resumo
de 3 linhas no terminal.

## Erros comuns

- **`pmo.db` vazio ou poucas atividades** → diz "ainda nao tem dado
  suficiente; volta no proximo mes"
- **Dependencia `pmo_dashboard` ausente** → usa template HTML inline
  minimalista (mostrado acima)
- **`webbrowser` falha em servidor headless** → so salva o HTML e
  imprime caminho
