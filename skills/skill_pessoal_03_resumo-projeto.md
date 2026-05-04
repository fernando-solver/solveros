---
name: skill_pessoal_03_resumo-projeto
description: Le um projeto inteiro e gera 1 paragrafo do estado atual + 3 proximos passos
trigger: O usuario pede "me explica esse projeto", "onde estou nesse trabalho" ou "o que falta aqui"
version: 1
last_updated: 2026-05-03
uses_count: 0
---

# Resumo do estado de um projeto

## Quando usar

- Voltando a um projeto depois de dias/semanas sem mexer
- Antes de uma reuniao sobre esse projeto
- Quando precisa explicar pra outra pessoa o que esta rolando
- Quando voce mesmo perdeu o fio da meada

## Quando NAO usar

- Projeto recém-criado (sem `historico.md` ou < 3 entradas) — só leia
  o `CLAUDE.md` e pronto
- Pedido vago tipo "me ajuda" sem nome de projeto — pergunte qual

## Procedimento

### 1. Identifica os 3 arquivos canônicos

```python
from pathlib import Path

projeto = Path('caminho/do/projeto')

claude_md = projeto / 'CLAUDE.md'
historico = projeto / 'historico.md'
proximos = projeto / 'proximos-passos.md'

# Se algum nao existe, sinalize mas nao pare
if not claude_md.exists():
    print('[AVISO] sem CLAUDE.md — projeto nao tem briefing canonico')
```

### 2. Lê e sintetiza

```python
def ler(p):
    return p.read_text(encoding='utf-8') if p.exists() else ''

contexto = ler(claude_md)        # missao, regras
historia = ler(historico)         # cronologia
proximos_atual = ler(proximos)    # o que estava planejado
```

### 3. Identifica padrões

- **Última atividade**: data mais recente em `historico.md`
- **Tipo da última**: `feature`/`bugfix`/`discovery`/`decision`?
- **Decisões tomadas**: todas as entradas de tipo `decision` em ordem
- **Travas conhecidas**: entradas `bugfix` sem `feature` posterior

### 4. Gera resumo em 3 partes

**Parte 1 — Estado atual (1 paragrafo, ~5 linhas):**

> O projeto <X> está em fase <Y>. Última atividade foi em <data>:
> <descricao>. As decisões importantes foram <D1> e <D2>. Há <N>
> coisas em andamento e <M> coisas decididas mas não executadas.

**Parte 2 — O que importa agora (3 bullets):**

> - **Mais urgente:** <coisa que está bloqueando outras coisas>
> - **Mais lucrativo:** <coisa que destrava mais valor>
> - **Mais barato:** <coisa que termina rápido e tira da lista>

**Parte 3 — 3 próximos passos concretos:**

> 1. <ação executável em < 1 hora>
> 2. <ação executável em < 1 dia>
> 3. <ação maior, planejada pra esta semana>

### 5. Salva em `<projeto>/saidas/resumo_<YYYYMMDD>.md`

Mantém histórico de resumos pra comparar evolução depois.

### 6. Devolve ao usuario

```
[OK] Resumo de <projeto> gerado.

Estado: <1 frase>

Próximos 3 passos:
  1. <acao>
  2. <acao>
  3. <acao>

Resumo completo: <projeto>/saidas/resumo_<data>.md
```

## Output esperado

Arquivo `saidas/resumo_<data>.md` no projeto + 3 linhas no terminal.

## Erros comuns

- **Sem `historico.md`** → use só `CLAUDE.md` pra estado e dê
  próximos-passos baseados em `proximos-passos.md`
- **Sem nenhum dos 3 arquivos** → diz "esse projeto não tá estruturado;
  rode `/nova-pasta` pra criar a estrutura canônica e volta aqui"
- **Histórico muito longo (> 200 entradas)** → foca nos últimos 30 dias
  + entradas de tipo `decision` (essas valem sempre)
