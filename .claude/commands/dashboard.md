---
description: Gerar dashboard HTML com retrato do workspace
---

Execute o comando `/dashboard` conforme a secao "## /dashboard" do CLAUDE.md na raiz.

Execute via Bash:

```bash
python -c "from pmo_dashboard import generate_dashboard; generate_dashboard(open_browser=True)"
```

O dashboard e salvo em `dashboard.html` na raiz do workspace (sobrescreve a cada rodada — atalho fixo, duplo-clique resolve) e aberto no navegador padrao.

Apos gerar, informe ao usuario o caminho e convide a interpretar as 8 secoes: banner de frescor, KPIs, calendario 90 dias, horas trabalhadas por dia, top projetos, distribuicao de tipos, objetivos, temas recorrentes, compartilhamentos.

Se o usuario pedir dashboard offline: oriente a baixar `chart.min.js` em `assets/` conforme `assets/README.md`.

Detalhes completos em `skills/skill_ver-dashboard.md`.
