# FAQ — SolverOS

Perguntas que aparecem com frequência sobre o SolverOS.

---

## "Claude Code já tem memória persistente. Qual a diferença do SolverOS?"

A objeção tem razão pela metade. Claude Code **tem** memória persistente — mas é uma memória com escopo diferente. As duas não competem; complementam.

### Em uma frase

**Memória do Claude é sobre você, a pessoa. Memória do SolverOS é sobre o seu trabalho.**

### Em uma tabela

| Aspecto | Claude Code memory | SolverOS memory |
|---|---|---|
| **Escopo** | sobre o usuário (preferências, jeito) | sobre o trabalho (projetos, atividades, objetivos) |
| **Lembra de** | preferências, decisões pessoais, jeito de trabalhar | projetos ativos, histórico, decisões, métricas |
| **Estrutura** | texto livre (Claude lê e interpreta) | SQLite estruturado + arquivos canônicos |
| **Query** | "Claude, lembra do que falamos?" | `SELECT * FROM activities WHERE date > '2026-04-01'` |
| **Acompanha você** | SIM (vinculada à sua instalação Claude) | SIM (clone o repo em outra máquina, herda tudo) |
| **Funciona com outro LLM** | NÃO | SIM (arquivos puros, qualquer ferramenta lê) |
| **Auditoria** | opaca ("Claude lembrou que...") | rastreável (`historico.md` append-only, log SQL) |

### As 3 diferenças que mais importam

#### 1. Estruturado vs livre

Claude lembra: *"você estava escrevendo o terceiro capítulo do livro"* (impressão).

SolverOS sabe: *último avanço no capítulo 3 em 2026-05-01, total 1.847 palavras, fonte: `livro/03_capitulo_3/rascunho.md`*.

Você consegue **gerar relatório, calcular ritmo, comparar semanas** com SolverOS. Não consegue com memória do Claude.

#### 2. Memória passiva vs operação ativa

Memória do Claude é **passiva** — Claude usa **se** lembrar.

SolverOS é **ativo** — o hook `SessionStart` injeta contexto do trabalho no boot, skills procedurais executam rotinas reais (gerar dashboard, arquivar pasta, indexar PDFs), slash commands transformam dado em entregável. A memória não só "lembra" — ela **opera**.

#### 3. Portabilidade

A memória do Claude mora em `~/.claude/` — vinculada à sua instalação.

A memória do SolverOS mora no seu workspace (filesystem + SQLite) — você copia a pasta, leva pra outra máquina, e tem tudo de volta. Outro LLM lê os mesmos arquivos.

### A resposta curta e honesta

Os dois juntos são melhores que cada um sozinho. O SolverOS usa a memória do Claude pra entender o **jeito do usuário**, e o `pmo.db` pra operar o **trabalho do usuário**. Não tem redundância — cada um cobre o que o outro não cobre.

---

## "Posso usar sem Claude Code? Funciona com ChatGPT?"

Os arquivos do SolverOS (CLAUDE.md, historico.md, objetivos.md, skills/) são puramente texto markdown e Python. Qualquer LLM com acesso ao filesystem consegue ler.

Mas **a integração nativa é com Claude Code** (slash commands, hooks, agents). Pra rodar com ChatGPT/Cursor/outros, você precisa adaptar os comandos pra invocação manual.

Vale a pena? Provavelmente não no curto prazo. Se você usa Claude Code, ganha 10x. Se não usa, talvez seja a hora de testar.

---

## "Meus dados saem da minha máquina?"

Não. Tudo é local:
- `pmo.db` é SQLite no seu disco
- Arquivos de projeto são markdown no seu filesystem
- Não tem servidor, não tem cloud, não tem telemetria

A única coisa que sai é o que o Claude Code envia pra API da Anthropic durante a sessão (e isso já é como Claude Code funciona, independente do SolverOS).

---

## "É open source ou pago?"

**Core é open source (MIT)**, gratuito, modificável, redistribuível.

**Mentoria/turma é pago.** Pra implementar o SolverOS com método e acompanhamento — desenhar suas áreas, customizar skills pro seu trabalho, montar dashboards específicos — vou abrir turmas periódicas.

Lista de espera no `README.md`.

---

## "O que é Stack? Posso criar o meu?"

Stacks são extensões especializadas. O **Core** é genérico (estrutura mínima, skills universais). Stacks adicionam capacidades pra contextos específicos:

- **Stack Empresa** — PMO empresarial genérico
- **Stack Ecommerce** — métricas Meta/Google Ads, KPIs de loja
- **Stack Consultor** — pipeline de propostas, agenda, projetos por cliente
- **Stack Indústria** — controle de produção, manutenção
- **Stack Serviços** — agendamento, faturamento, recorrência

Sim, você pode criar o seu. A estrutura está em `stacks/<nome>/manifest.yaml`. Quando estiver pronto, abre PR — se fizer sentido, vira stack oficial.

---

## "Por que SQLite e não banco em nuvem?"

3 razões:

1. **Zero infra.** SQLite é um arquivo. Não precisa servidor, não precisa configuração, não precisa pagar.
2. **Zero dependência externa.** Funciona offline, num avião, sem internet, sem conta na nuvem.
3. **Auditável.** Você abre com qualquer ferramenta SQL e vê tudo. Sem mistério.

Limitação: não é multi-usuário simultâneo. Pra time, cada pessoa tem o seu workspace e sincroniza via git.

---

## "Já existe outra ferramenta parecida?"

Existem ferramentas próximas, mas **não fazem a mesma coisa:**

- **claude-mem** — resolve memória conversacional (entre sessões). SolverOS resolve operação ao longo de meses. Camadas complementares.
- **LangChain / CrewAI / AutoGen** — frameworks pra construir agentes em código. SolverOS é filesystem editorial — não tem código de agente, só convenção.
- **Notion / Obsidian** — sistemas de notas estruturados. Não executam ações, não têm log auditável, não geram entregáveis.

A diferença é tese: **agente vive no seu computador real, não num ambiente isolado**. SolverOS é a forma mais barata e direta de transformar isso em prática.

---

## Faltou alguma?

Abre issue em https://github.com/fernando-solver/solveros/issues
