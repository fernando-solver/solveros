<div align="center">

<img src="assets/solverkitty.png" alt="Solverkitty" width="520" />

> **Crie um agente. Em uma pasta. Em menos de 1 minuto.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Versão](https://img.shields.io/badge/versão-0.6-blue.svg)](CHANGELOG.md)
[![Made for Claude Code](https://img.shields.io/badge/Made%20for-Claude%20Code-purple.svg)](https://claude.com/product/claude-code)

</div>

---

## O que é

Solverkitty é um kit de arquivos + scripts Python que transforma seu Claude Code num parceiro de trabalho contínuo. Você cria a pasta, instala, e seu agente passa a:

- **Lembrar do que você faz**, mês a mês (SQLite local — nada vai pra nuvem)
- **Organizar seus projetos** automaticamente (filesystem editorial)
- **Executar rotinas** que você define (skills procedurais)
- **Gerar dashboards, relatórios, resumos** do seu trabalho

Não é framework. Não é stack pesada. **É filesystem editorial + SQLite + skills.**

## Pra quem

Pra quem trabalha com a cabeça e perde contexto entre projetos.

Profissional liberal, consultor, freelancer, pesquisador, estudante, empresário — qualquer pessoa que quer transformar o próprio computador em ambiente agêntico, sem precisar virar dev.

## Quick start (menos de 1 minuto)

```bash
git clone https://github.com/fernando-solver/solverkitty.git
cd solverkitty
python instalar.py
claude
```

Dentro do Claude Code:

```
/comecar
```

Pronto. Seu agente está rodando.

## Como funciona

```
seu-workspace/
├── CLAUDE.md           ← identidade e regras do agente
├── pmo.db              ← memória estruturada (SQLite local)
├── skills/             ← rotinas que o agente executa
├── .claude/commands/   ← seus comandos personalizados
├── stacks/             ← extensões especializadas (futuras)
└── <suas pastas>/      ← uma pasta por área que você organiza
```

3 princípios:

1. **Filesystem é a memória.** Cada pasta de projeto carrega seu próprio `CLAUDE.md`, `historico.md` e `objetivos.md` — o agente lê e sabe onde paramos.
2. **SQLite é o log.** Toda decisão, bugfix, descoberta vai registrada com tipo. Auditável via consulta SQL.
3. **Skills são procedurais.** Não documentação. Código que o agente executa quando você pede.

## O que vem com o Core (v0.6)

**Comandos:**
- `/comecar` — apresentação + cadastro inicial em 5 minutos
- `/setup-pessoal` — você + agente + áreas + objetivo principal
- `/proximo-passo` — sugere 1 ação alinhada ao seu objetivo
- `/nova-pasta` — cria uma pasta de projeto canônica
- `/dashboard` — gera retrato visual do seu trabalho
- `/compartilhar` — exporta projeto com scrub de credenciais
- `/fechar-dia` — consolida atividades no diário
- `/instalar-stack` — instala stacks especializados (futuros)

**Skills procedurais já incluídas:**
- `organizar-leitura` — indexa pasta de PDFs por tema
- `revisar-semana` — relatório do que evoluiu nos últimos 7 dias
- `resumo-projeto` — estado atual de um projeto + próximos passos
- `arquivar-pasta` — move pasta inativa pra `_archive/` mantendo histórico
- `visao-mes` — HTML consolidado do mês

**Módulos Python:**
- `pmo_db.py` — interface SQLite
- `pmo_setup.py` — bootstrap de projetos
- `pmo_dashboard.py` — geração de dashboard HTML
- `pmo_share.py` — exportação com scrub de credenciais
- `pmo_stacks.py` — sistema de stacks

## Roadmap

- ✅ **v0.6 — Core pra pessoas** (atual)
- 🛠️ **Stack Empresa** — PMO empresarial genérico (em desenvolvimento)
- 🎯 **Stack Ecommerce** — lojista BR
- 🎯 **Stack Consultor / Mentor / Educador** — quem vende conhecimento
- 🎯 **Stack Indústria pequena** — fábrica/manufatura
- 🎯 **Stack Serviços** — agência/clínica/escritório

## Quer ir além?

Solverkitty Core é open source. Pra implementar com método e acompanhamento, vou abrir turmas periódicas:

- 📋 **Lista de espera:** *em breve*
- 💬 **DM:** [@fernandosolver](https://instagram.com/fernandosolver)
- 🌐 **Site:** [fernandosolver.com.br](https://fernandosolver.com.br)

## Licença

MIT — use, modifique, distribua. Cite a fonte se publicar derivado.

---

<div align="center">

*Construído por [Fernando Solver](https://fernandosolver.com.br) em colaboração contínua com [Claude](https://claude.com) (Anthropic).*

*O gato Jorge inspirou o mascote.*

</div>
