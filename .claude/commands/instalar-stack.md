---
description: Instala um stack no workspace ativo, copiando agents/commands/skills/hooks pra raiz
argument-hint: <stack> [--dry-run]
---

Voce esta executando `/instalar-stack`. Use `pmo_stacks.py` pra
copiar agents, commands, skills e hooks do stack solicitado pra
raiz do workspace.

## Como conduzir

1. **Se nenhum argumento veio**, liste stacks disponiveis:
   ```bash
   python pmo_stacks.py list
   ```
   E pergunte qual o usuario quer instalar.

2. **Se argumento veio mas com `--dry-run`**, mostre o que seria feito:
   ```bash
   python pmo_stacks.py install <nome> --dry-run
   ```

3. **Se argumento veio sem `--dry-run`**, mostre primeiro um dry-run e
   peca confirmacao antes de aplicar:
   ```
   Voce esta prestes a instalar o stack '<nome>'.
   Isso vai copiar:
     - X agents pra .claude/agents/
     - Y commands pra .claude/commands/
     - Z skills pra skills/
     - W hooks pra pmo_hooks/

   Arquivos com mesmo nome no destino serao SOBRESCRITOS.

   Confirma? (sim/nao)
   ```

   Apos `sim`, rode:
   ```bash
   python pmo_stacks.py install <nome>
   ```

4. **Apos instalacao bem-sucedida**, oriente o usuario:
   ```
   [OK] Stack '<nome>' instalado.

   IMPORTANTE: feche e reabra o Claude Code pra Claude carregar os
   novos agents, commands e hooks. So apos reiniciar:
     - Slash commands novos aparecerao em /
     - Subagents poderao ser invocados via Task tool
     - SessionStart vai injetar contexto baseado no stack
   ```

## Regras

- **Nunca instalar sem confirmacao** quando vai sobrescrever arquivos.
- **Lembrar do reinicio**: muitas mudancas so refletem no proximo boot.
- **Se stack nao existe**: liste os disponiveis e sugira `core` como minimo.
