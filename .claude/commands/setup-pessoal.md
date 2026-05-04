---
description: Cadastro inicial — você + agente + áreas + objetivo principal. 5 perguntas em ~3 minutos.
argument-hint: (nenhum)
---

Você está executando `/setup-pessoal`. Esse é o cadastro inicial do
workspace pra **uma pessoa** (não empresa). 5 perguntas, uma de cada vez,
com 1 linha de contexto antes de cada uma. Total: ~3 minutos.

**Princípios:**
- Pergunta aberta, sem sugerir nomes ou opções fechadas.
- Acuse o que ouviu antes de seguir ("entendi: você é Maria, foca em…").
- Valide sanidade silenciosamente (resposta vazia, nome com 200 caracteres, etc).
- Feche com diagnóstico de 2 linhas — não recapitule tudo.

## Pergunta 1 — você

> *Pra eu te endereçar nas conversas e nos relatórios.*

**Como vou te chamar?**

Aceite qualquer string (nome, sobrenome, apelido). Em branco: usa `você`.
Limita 60 caracteres.

→ salva em `nome_usuario`.

## Pergunta 2 — agente

> *Esse é o nome do seu agente. Pode ser próprio, de função, ou deixar como Solverkitty mesmo.*

**Que nome quer dar pro seu agente?**

Pergunta aberta, **sem sugerir nomes**. Deixe a pessoa escolher.
Em branco ou "Solverkitty mesmo": mantém `Solverkitty`. Limita 30 caracteres.

→ salva em `nome_agente`.

## Pergunta 3 — áreas

> *Vou criar uma pasta por área. Não precisa acertar agora — você muda depois.*

**Quais 3 áreas da sua vida ou trabalho você quer organizar primeiro?**

Aceite resposta livre. Exemplos do que a pessoa pode dar (não sugira você
primeiro): "estudos, clientes, pessoal" ou "trabalho, leitura, projetos
paralelos" ou "consultoria, livro, finanças".

Valide:
- Se a pessoa der menos de 2: pergunte se quer adicionar mais ou seguir
  com o que tem (mínimo 1 vale, não force 3).
- Se der mais de 5: aceite, mas avise "começa pesado — sugiro 3-4 pra
  testar; sempre dá pra adicionar depois".

→ cria 1 pasta por área no formato `slug-da-area/` na raiz do workspace,
cada uma com `_template/` aplicado (CLAUDE.md, inbox/, saidas/, _archive/).

## Pergunta 4 — objetivo principal

> *Vou guardar como referência. Quando você pedir `/proximo-passo`, eu sempre puxo isso.*

**Qual seu objetivo mais importante pros próximos 30 dias?**

Aceite frase livre. Exemplos do que pode ser:
- "terminar primeiro rascunho do livro"
- "fechar 3 contratos novos"
- "estudar 1h por dia de design"
- "organizar finanças pessoais"

Não force estrutura SMART agora — se a pessoa quer "ficar mais saudável",
aceite. O objetivo evolui com o uso.

→ salva em `objetivo_principal`, sincroniza com `pmo.db` via
`objetivo_add(tipo='meta_30_dias', descricao=<texto>, prazo=<data+30d>)`.

## Pergunta 5 — skill inicial (opcional)

> *Skills são rotinas que o agente faz pra você. Você pode pular e adicionar depois.*

**Quer ativar uma skill agora?** (sim / não — default: não)

Se "não": pula direto pro fechamento.

Se "sim": liste as skills disponíveis com 1 linha cada:

```python
from pmo_db import skill_list
for s in skill_list():
    print(f"  - {s['name']}: {s['description']}")
```

Pessoa escolhe o nome. Você ativa via `skill_activate(<nome>)`.

## Fechamento — diagnóstico em 2 linhas

Após salvar tudo, devolva exatamente:

```
[OK] Pronto.

{{nome_usuario}}, você tem o agente {{nome_agente}} configurado pra
organizar {{areas}}, focado em "{{objetivo_principal}}".

Próximo passo: solte arquivos relevantes em qualquer pasta de área que
acabei de criar, ou rode `/proximo-passo` quando quiser saber o que fazer agora.
```

Não liste mais nada. Não recapitule. A pessoa quer começar a trabalhar.

## Regras

- **Pergunta aberta sempre.** Sugerir opções fechadas vira formulário.
- **1 pergunta por vez.** Nunca mande 5 perguntas em bloco.
- **Acuse o que ouviu.** "Maria, entendi" antes de seguir pra próxima.
- **Diagnóstico final em 2 linhas.** Não em 10. Não em parágrafo.
- **Pessoa, não empresa.** Vocabulário: "área", "projeto", "objetivo".
  Nunca: "departamento", "negócio", "empresa", "marca", "cliente".
