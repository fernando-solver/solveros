---
name: skill_ver-dashboard
description: Gera dashboard HTML estatico com retrato do trabalho (KPIs, heatmap, temas, objetivos, shares)
trigger: Usuario pergunta "como estou indo", "panorama geral", "retrospectiva", "dashboard"; preparacao de reuniao de status
version: 1
last_updated: 2026-04-23
uses_count: 0
---

# Ver dashboard do workspace

## Quando usar

- Perguntas tipo: "como estou indo?", "o que eu fiz esse mes?", "me da um panorama"
- Retrospectiva semanal/mensal
- Antes de reuniao — screenshot do dashboard para mostrar status
- Auto-diagnostico: ver onde o tempo esta indo

## Quando NAO usar

- Para perguntas especificas (ex: "quantas atividades do tipo decision em marco?") — use query direto ao pmo.db
- Dashboard e snapshot agregado, nao substitui query ad-hoc

## Procedimento

### 1. Gerar o HTML

```python
python -c "
from pmo_dashboard import generate_dashboard
path = generate_dashboard()
print(f'Dashboard: {path}')
"
```

### 2. Abrir no navegador

```python
python -c "
from pmo_dashboard import generate_dashboard
import webbrowser
path = generate_dashboard()
webbrowser.open(f'file:///{path}')
"
```

Ou (ainda mais direto):

```python
python -c "from pmo_dashboard import generate_dashboard; generate_dashboard(open_browser=True)"
```

### 3. Interpretar secoes do dashboard

**KPIs (4 cards):**
- Projetos totais
- Sessoes totais
- Atividades no mes corrente
- Pendencias abertas

**Heatmap 90 dias:** celulas mais escuras = mais atividades no dia. Rapidamente mostra padroes de trabalho (quais dias da semana sao mais produtivos).

**Top projetos:** barras ordenadas por volume de atividades. Ve onde o tempo realmente foi.

**Distribuicao por tipo:** donut de decision/bugfix/feature/discovery/etc. Razoes saudaveis de referencia:
- feature dominante ~ 20-30% — criando coisa nova
- bugfix ~ 5-10% — disciplina de correcao
- decision ~ 3-5% — escolhas arquiteturais documentadas

**Objetivos:** barras de progresso (% projetos ativos sobre projetos vinculados) + atividades no mes por objetivo.

**Temas recorrentes:** palavras mais frequentes nos summary das atividades. Tamanho da palavra = frequencia. Revela o que realmente ocupa seu tempo (vs o que voce acha que ocupa).

**Compartilhamentos:** tabela de shares recentes via `/compartilhar`.

### 4. Regenerar com periodo/escopo diferente (futuro)

Hoje o dashboard usa defaults: heatmap 90 dias, temas 90 dias. Para recortar por periodo ou projeto, editar `_gather_data` em `pmo_dashboard.py` ou filtrar diretamente via pmo_db.

## Chart.js offline

Por padrao o dashboard carrega Chart.js via CDN. Para funcionar offline (apresentacao sem wifi, ambiente isolado), baixe o `chart.min.js` conforme `assets/README.md`. Uma vez presente, o dashboard **embeda inline** automaticamente — HTML fica 100% auto-contido.

## Sinais de melhoria

- Se o usuario regenera o dashboard toda hora — provavelmente falta auto-refresh (feature futura)
- Se o heatmap tem buracos grandes — pode indicar periodos sem registro no pmo.db (disciplina)
- Se temas recorrentes fazem pouco sentido — refinar lista `_STOPWORDS_PT` em `pmo_db.py`

## Historico de melhoria

- v1 (2026-04-23): versao inicial com 7 secoes + Chart.js para donut, SVG+CSS para barras/heatmap/temas
