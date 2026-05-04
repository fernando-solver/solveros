---
description: Sugere 1 ação concreta alinhada ao seu objetivo principal e ao histórico recente
---

Você está executando `/proximo-passo`. Lê o objetivo principal da pessoa,
o histórico recente do workspace, e sugere **1 ação concreta** que move
a agulha mais.

## Passos

1. **Lê objetivo principal:**
   ```python
   from pmo_db import objetivo_list
   objetivos = objetivo_list()
   principal = next((o for o in objetivos if o['tipo'] == 'meta_30_dias'), None)
   ```

2. **Lê histórico das últimas 7 sessões:**
   ```python
   from pmo_db import query_activities
   recentes = query_activities("date >= date('now', '-7 days')", (), 50)
   ```

3. **Identifica o estado:**
   - Se há objetivo e histórico recente toca nele → sugere próximo movimento concreto
   - Se há objetivo mas histórico não toca nele há 3+ dias → sugere voltar pra ele
   - Se não há objetivo definido → sugere `/setup-pessoal` ou `objetivo_add`
   - Se workspace recém-criado (sem histórico) → sugere criar primeira pasta de área

4. **Sugere 1 ação concreta** que a pessoa pode executar nos próximos 30 minutos.
   Não 5 ações. Não 3. Uma.

## Output

```
Objetivo principal: <descricao>

Ação recomendada: <ação específica, executável em <30min>
Razão: <conexão com o objetivo OU com o estado atual do trabalho>
Como executar: <comando ou passo prático>
```

## Exemplos

**Caso A — objetivo + atividade recente alinhada:**
```
Objetivo principal: Terminar primeiro rascunho do livro

Ação recomendada: Escrever 500 palavras do capítulo 3 (último mexido em 2026-05-01)
Razão: Você avançou 2 capítulos nas últimas 7 sessões; capítulo 3 está parado há 2 dias
Como executar: abre clientes/livro/03_capitulo_3/ e continua o rascunho
```

**Caso B — objetivo abandonado:**
```
Objetivo principal: Estudar 1h de design por dia

Ação recomendada: Reabra o curso de design — última atividade foi há 5 dias
Razão: Você perdeu 5 dias do streak; voltar hoje custa menos do que reiniciar amanhã
Como executar: abre estudos/design/ e roda 25 minutos de Pomodoro com material parado
```

**Caso C — sem objetivo definido:**
```
Sem objetivo principal cadastrado.

Ação recomendada: Defina seu objetivo dos próximos 30 dias
Razão: Sem objetivo, eu não consigo sugerir o que prioriza
Como executar: rode `/setup-pessoal` (ou só a parte do objetivo)
```

## Regras

- **1 ação, não 5.** Pessoa executa o que você manda; pulverizar atrapalha.
- **Cite número/data sempre.** "Há 5 dias", "2 capítulos", "última sessão em 2026-05-01".
- **Executável em < 30 minutos.** Se a ação real é grande, sugira só o primeiro passo
  ("escrever 500 palavras", não "terminar o livro").
- **Pessoa, não empresa.** Vocabulário: você, seu trabalho, sua área, seu objetivo.
  Nunca: marca ativa, KPI da empresa, ROAS, faturamento, cliente.
