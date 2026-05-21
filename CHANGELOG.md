# Changelog — SolverOS

Todas as mudanças notáveis deste projeto são documentadas aqui.

Formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e este projeto adere a [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [0.6.1] — 2026-05-03

**Visibility overhaul.** Documentation, community files, and project meta artifacts.

### Added

- **README.md in English** as the primary version
- **README.pt-BR.md** as Brazilian Portuguese translation, linked at top
- **docs/PHILOSOPHY.md** — full thesis on context + environment as the two pillars of agentic systems
- **docs/ARCHITECTURE.md** — deep technical dive into every component (filesystem layout, SQLite schema, hooks, skills, stacks, slash commands)
- **docs/USE_CASES.md** — 6 detailed use case patterns (founder, consultant, researcher, knowledge worker, student, small business)
- **CONTRIBUTING.md** — contribution guidelines, PR process, code style
- **CODE_OF_CONDUCT.md** — Contributor Covenant 2.1
- **SECURITY.md** — vulnerability disclosure policy
- **AUTHORS.md** — contributor recognition (Fernando + Claude + Jorge)
- **SHOWCASE.md** — gallery of users (with template for new entries)
- **.github/ISSUE_TEMPLATE/** — bug report, feature request, use case templates
- **.github/PULL_REQUEST_TEMPLATE.md**
- **.github/FUNDING.yml**
- **.github/workflows/ci.yml** — automated Python syntax + smoke tests on every push/PR
- **assets/social-preview.html** — generates 1280x640 preview image for GitHub social card
- Co-authored commits with Claude (Anthropic) credit

### Changed

- README structure: added thesis section, personas table, architecture diagram (Mermaid), use cases inline, comparison table with alternatives, FAQ short version
- `.gitignore` header updated from "Solver Filesystem" to "SolverOS"
- Added Portuguese-to-English translation guide for all commands and skills in README
- Documented in `docs/PHILOSOPHY.md` why commands are in Portuguese (authenticity + planned i18n in v0.7)
- Added v0.7 i18n milestone to roadmap (multi-language support planned)

---

## [0.6.0] — 2026-05-03

**Reposicionamento: SolverOS pra pessoas.**

A v0.6 é uma reescrita estratégica do produto. Saiu do escopo "PMO empresarial" e voltou pra raiz: ferramenta pra **uma pessoa transformar o próprio computador em ambiente agêntico**.

### Adicionado

- **Tagline oficial:** *"Crie um agente. Em uma pasta. Em menos de 1 minuto."*
- **5 skills procedurais pra pessoa:**
  - `skill_pessoal_01_organizar-leitura` — indexa pasta de PDFs por tema
  - `skill_pessoal_02_revisar-semana` — relatório dos últimos 7 dias
  - `skill_pessoal_03_resumo-projeto` — estado atual + próximos passos
  - `skill_pessoal_04_arquivar-pasta` — arquiva pasta inativa
  - `skill_pessoal_05_visao-mes` — HTML consolidado do mês
- **Comando `/setup-pessoal`** — cadastro inicial em 5 perguntas (você + agente + áreas + objetivo + skill)
- **Sistema de stacks** (`pmo_stacks.py`) — Core sempre disponível, stacks especializados como adições futuras
- **Logo SolverOS** (mascote gato Jorge) em `assets/solveros.png`

### Alterado

- **`/comecar` reescrito** — apresentação charmosa + apelido opcional + delegação pro `/setup-pessoal` (antes apontava pra `/setup-empresa`)
- **`/proximo-passo` reescrito** — agora lê objetivo principal + histórico recente e sugere 1 ação concreta executável em < 30 minutos (antes era específico ecommerce com subagentes ROAS/marca-ativa)
- **`stacks/core/_template/`** — vocabulário "pasta de projeto" no lugar de "pasta-empresa"
- **`stacks/core/manifest.yaml`** — versão 0.6, descrição neutra ("serve qualquer pessoa"), commands sem `setup-empresa` nem `arrumar-cliente`
- **`guia-filesystem.md`** — exemplo principal trocado de "Relatório Semanal de Vendas" para "Curadoria Mensal de Newsletter"

### Removido

- **`pmo_inbox.py`** — 50+ regex de detecção de Meta Ads/Google Ads/TikTok/ROAS (movido pra Stack Ecommerce futuro, fora do Core)
- **`/setup-empresa`** — substituído por `/setup-pessoal`
- **`/arrumar-cliente`** — específico do Stack Ecommerce
- **`stacks/ecommerce/`** — não faz parte da v0.6 Core (lançamento futuro como Stack)
- **`clientes/`** — pasta vazia template não faz sentido pra workspace pessoal

### Limpeza

- Zero referências a clientes, ERPs proprietários ou nomes específicos de pessoas no código ou documentação.
- Auditoria pré-publicação: varredura completa por padrões sensíveis retornou 0 matches.

---

## [0.5.0] — 2026-05-02 *(não publicado)*

Versão experimental que tentou embarcar Stack Ecommerce no Core. Decidido reverter — Stack Ecommerce vira lançamento futuro independente. Conteúdo e aprendizados absorvidos pela v0.6.

---

## [0.4.0] — 2026-04-24

Primeira versão pública estável. PMO genérico em filesystem + SQLite, skills procedurais, dashboard editorial, sistema de share com scrub de credenciais.

### Componentes

- `pmo_db.py`, `pmo_setup.py`, `pmo_dashboard.py`, `pmo_share.py`, `pmo_tokens.py`, `pmo_preflight.py`
- 1 skill (`skill_compartilhar-projeto`)
- Comandos `/setup`, `/nova-pasta`, `/compartilhar`, `/dashboard`, `/fechar-dia`, `/status`
- Documentação: `guia-filesystem.md`, `playbook.md`, `COMEÇAR-AQUI.html/.txt`

---

## [0.3.0] — abril 2026

Redesign visual completo. Onboarding sem Python obrigatório.

## [0.2.0] — abril 2026

Onboarding sem Python + preflight + 3 skills.

## [0.1.0] — abril 2026

Versão inicial. Snapshot histórico em `kit-solver-filesystem-v0.1/`.
