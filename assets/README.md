# assets/ — bibliotecas locais para dashboards

## Chart.js (opcional, para dashboards offline)

O `pmo_dashboard.py` gera HTMLs que usam Chart.js para renderizar graficos. Por padrao, o HTML carrega Chart.js via CDN (funciona online).

**Se voce quer que os dashboards funcionem sem internet** (por exemplo para apresentar em reuniao sem wifi), baixe o Chart.js localmente:

### Opcao 1 — download direto

Baixe **Chart.js v4 UMD minified** em:
https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js

Salve como `assets/chart.min.js` nesta pasta.

### Opcao 2 — via terminal

```bash
# No Windows (PowerShell):
curl.exe -o assets/chart.min.js https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js

# No macOS/Linux:
curl -o assets/chart.min.js https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js
```

Uma vez que `assets/chart.min.js` exista, o `pmo_dashboard.py` vai **embedar a biblioteca inline no HTML** automaticamente. Dashboards ficam 100% offline e auto-contidos (~200KB por HTML).

Se o arquivo nao existe, o dashboard usa CDN como fallback (funciona na maioria dos ambientes, mas requer internet no primeiro load).

## Verificacao

Depois de baixar, confirme:

```bash
python -c "from pmo_dashboard import has_chart_local; print(has_chart_local())"
```

Deve imprimir `True`.
