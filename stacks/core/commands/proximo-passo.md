---
description: Sugere 1 acao concreta pra marca ativa, alinhada ao objetivo mais distante da meta
---

Voce esta executando `/proximo-passo`. Olhe os objetivos da marca ativa e os
issues abertos de auditoria; sugira **1 acao concreta** que move a agulha mais.

## Passos

1. Marca ativa via `.solver-active-brand`.
2. Identifique objetivos em risco:
   ```python
   from pmo_db import objetivos_em_risco, auditoria_open_issues, cliente_get
   cliente = cliente_get('<slug>')
   em_risco = objetivos_em_risco(threshold_pct=0.7)
   issues = auditoria_open_issues(cliente_id=cliente['id'])
   ```
3. Pegue o **objetivo com menor pct** (mais distante da meta) ou, se nao
   houver risco, o **issue mais severo**.
4. Sugira 1 acao concreta vinculada ao subagente certo:
   - Objetivo `roas` em risco -> "Rode `/auditar-trafego`; trafego-solver
     vai apontar campanhas com ROAS<2 pra pausar/ajustar"
   - Objetivo `faturamento_mensal` em risco -> "Use `/big-idea` com
     estrategista-solver pra plano de aceleracao"
   - Issue de duplicata -> "Wave 2: `/arrumar-cliente` (em desenvolvimento)"
   - Sem risco e sem issue -> "Tudo limpo. Que tal `/relatorio-pra-mim` pra
     consolidar onde estamos?"

## Output

```
Marca: <nome>

Acao recomendada: <acao especifica>
Razao: <objetivo X esta em <pct>%; ultima medicao em <data>>
Subagente: <quem vai executar>
Comando: <slash comando>
```

## Regras

- **1 acao, nao 5.** Usuario executa o que voce manda; pulverizar atrapalha.
- Cite numero sempre.
