# Use cases — Solverkitty in real work

Below are concrete patterns of how people use Solverkitty across different fields.
Each pattern includes setup, key skills, example prompts, and what you should expect.

> 📌 **Have a use case to add?** Open a PR with your story — see [SHOWCASE.md](../SHOWCASE.md).

---

## 🧠 Solo founder / indie hacker

### Pattern: tracking 5+ projects in parallel

**The problem:**
You're building 3 SaaS products, doing client work on the side, writing a newsletter, and prototyping a fourth idea. Every time you switch context, you lose 30 minutes.

**The setup:**
- One area folder per product (`saas-a/`, `saas-b/`, `saas-c/`)
- One area folder for client work (`clients/`) with subfolders per client
- One area folder for content (`writing/`)
- Main objective in `pmo.db`: tied to whichever product is the priority that month

**Key skills:**
- `revisar-semana` — runs every Monday morning
- `resumo-projeto` — runs when reopening a stale product
- `proximo-passo` — runs when you don't know what to do next

**Example prompts:**
```
You: "preciso decidir em qual saas focar essa semana"
Agent: [reads objetivos.md + last 7 days from each saas folder]
       "saas-a teve 12 atividades, mas todas bugfixes — você está em
       firefighting mode. saas-b teve 3 features novas mas 0 nos últimos
       4 dias. saas-c sem atividade há 11 dias.

       Recomendo focar saas-b — o ritmo de feature parou recentemente
       mas há momentum recuperável."
```

**What changes:**
You stop the "where was I?" tax. Switching context costs 30 seconds, not 30 minutes.

---

## 💼 Consultant / freelancer

### Pattern: one folder per client, history of decisions, deliverable archive

**The problem:**
You have 8 active clients. Some you talk to weekly, some monthly. Each has its own context, deliverables, decisions, and stakeholders. You can't keep it all in your head.

**The setup:**
- `clients/` folder with one subfolder per client
- Each client folder has `CLAUDE.md` with their context (industry, goals, constraints)
- Each client folder has `historico.md` with chronological notes (calls, decisions, deliverables)
- Each client folder has `saidas/` for finished deliverables (ready to share)

**Key skills:**
- `compartilhar-projeto` — when client asks for a deliverable summary
- `resumo-projeto` — before every client call
- `revisar-semana` — weekly check on which clients haven't been touched

**Example prompts:**
```
You: "preparar reunião com cliente X amanhã às 10h"
Agent: [reads clients/x/CLAUDE.md + historico.md last 60 days]
       "Cliente X — última conversa em 2026-04-22, ficou pendente:
       (1) revisão do plano de mídia Q2, (2) aprovação do orçamento
       de criativo para campanha de inverno.

       Sugestão de pauta:
       1. Status das duas pendências
       2. Próximo entregável (definido na última call: relatório
          de performance Q1, prazo 15/04 — verificar se foi enviado)
       3. Espaço pra ele trazer novidades"
```

**What changes:**
You arrive em qualquer reunião com 0 minutos de preparação mental. O contexto está pronto.

---

## 🔬 Researcher / academic

### Pattern: indexing papers, tracking experiments, generating monthly reviews

**The problem:**
Your literature folder has 200+ PDFs. You can't remember which ones you've read, which are relevant to your current paper, which informed which decisions in your methodology.

**The setup:**
- `papers/` folder with all PDFs
- `experiments/` folder with one subfolder per experiment
- Each experiment has `CLAUDE.md` with hypothesis, methodology, results
- `paper-draft/` folder for the manuscript in progress
- Main objective: "primeiro draft do paper até 2026-08-31"

**Key skills:**
- `organizar-leitura` — indexes papers by topic, marks top 3 to read
- `resumo-projeto` — for each experiment, generates current state
- `visao-mes` — monthly review of research progress for advisor meetings

**Example prompts:**
```
You: "preciso citar trabalhos sobre transformer attention pra section 3"
Agent: [searches papers/ INDICE.md for "attention", "transformer"]
       "Encontrei 12 papers indexados sobre o tópico. Os 4 mais
       relevantes pro contexto da sua section 3 (que segundo
       paper-draft/CLAUDE.md trata de eficiência computacional):

       1. Vaswani et al. 2017 — Attention Is All You Need (paper fundacional)
       2. Wang et al. 2020 — Linformer: Self-Attention with Linear Complexity
       3. Choromanski et al. 2021 — Rethinking Attention with Performers
       4. Dao et al. 2022 — FlashAttention

       Quer que eu gere as citações em BibTeX?"
```

**What changes:**
Você para de gastar 2h por sessão "procurando aquele paper que você lembra que leu". A literatura vira ferramenta, não obstáculo.

---

## 📊 Knowledge worker (analyst, manager, PM)

### Pattern: replacing scattered notes with auditable system

**The problem:**
You take notes em Notion, Obsidian, Apple Notes, sticky notes, post-its. Decisões importantes ficam perdidas. Você não consegue responder "o que decidimos sobre X há 3 meses?".

**The setup:**
- `decisions/` folder with `historico.md` cronológico de decisões
- `meetings/` folder com transcrições + decisões extraídas
- `projects/` com uma subpasta por iniciativa
- Main objective: tied to your quarterly OKR

**Key skills:**
- `resumo-executivo` — turns a 1-hour meeting transcript into TL;DR + bullets + actions
- `revisar-semana` — weekly recap before 1:1 with manager
- `visao-mes` — monthly summary for self-review

**Example prompts:**
```
You: "o que decidimos sobre estratégia de pricing pra produto Z?"
Agent: [searches decisions/historico.md + projects/produto-z/]
       "Três decisões registradas sobre pricing do produto Z:

       2026-04-18 [decision] Adotar pricing por usuário (não por uso)
                  Razão: alinha com como concorrentes B vs C precificam
                  Discussão: meetings/2026-04-18_strategy_call.md

       2026-04-25 [decision] Tier inicial em US$ 49/user/mo
                  Razão: feedback dos 12 design partners
                  Discussão: meetings/2026-04-25_pricing_workshop.md

       2026-05-01 [decision] Trial de 14 dias (não 30)
                  Razão: dados internos mostram conversão melhor em 14d
                  Discussão: projects/produto-z/historico.md"
```

**What changes:**
Memória institucional vira sua. Você se torna "a pessoa que lembra".

---

## 🎓 Student / lifelong learner

### Pattern: tracking reading lists, study progress, projects

**The problem:**
Você está fazendo um curso online + lendo 3 livros + escrevendo um projeto pessoal + pesquisando uma área nova. Não consegue ver progresso porque está fragmentado.

**The setup:**
- `course-X/` com `historico.md` por módulo concluído
- `reading/` com PDFs e `INDICE.md`
- `personal-project/` com `CLAUDE.md` + `historico.md`
- `notes/` com aprendizados sintetizados
- Main objective: "concluir curso X até 2026-07-31"

**Key skills:**
- `organizar-leitura` — quarterly cleanup of reading folder
- `revisar-semana` — Sunday evening study review
- `visao-mes` — monthly progress portrait
- `resumo-executivo` — turn course videos into structured notes

**Example prompts:**
```
You: "como tá meu progresso no curso?"
Agent: [reads course-X/historico.md + objetivos.md]
       "Curso X — 12 de 24 módulos concluídos (50%).

       Última atividade: módulo 12 finalizado em 2026-04-29.
       Tempo médio por módulo: 2.3 sessões.

       No ritmo atual, você termina em ~6 semanas. Seu objetivo é
       2026-07-31 — está 4 semanas à frente do prazo.

       Próximo módulo recomendado: Módulo 13 — Advanced patterns.
       Material no inbox/: video + slides já baixados em 2026-04-30."
```

**What changes:**
Você vê progresso composto. Aprender de fato vira hábito visível, não promessa abstrata.

---

## 🏪 Small business owner

### Pattern: managing the personal side without mixing with company tools

**The problem:**
Você tem uma empresa pequena com sistemas próprios (CRM, ERP, accounting). Mas decisões pessoais sobre estratégia, contratações, parcerias acabam dispersas em emails, conversas, anotações no celular.

**The setup:**
- Workspace pessoal **separado** do filesystem da empresa
- `strategy/` com `CLAUDE.md` (visão de longo prazo) + `historico.md` (decisões)
- `partnerships/` com uma pasta por parceria em consideração
- `hires/` com avaliações de candidatos
- Main objective: tied to current quarter's strategic focus

**Key skills:**
- `revisar-semana` — weekly strategic review (not operational)
- `resumo-projeto` — when reopening a partnership/hire decision
- `visao-mes` — monthly strategic snapshot

**Example prompts:**
```
You: "lembrei daquele candidato que conversamos há 3 semanas — qual era?"
Agent: [searches hires/]
       "Pessoa: Ana Silva. Cargo considerado: Diretora de Marketing.
       Conversa registrada em hires/ana-silva/historico.md em 2026-04-15.

       Estado da decisão: pausado.
       Razão registrada: 'Forte tecnicamente mas pediu remoto 100% e
       achamos que esse cargo precisa estar fisicamente conosco
       primeiros 6 meses'.

       Notas: ela mandou follow-up por email em 2026-04-29 perguntando
       se reconsiderou (registrado em historico.md). Não respondemos
       ainda — pendente."
```

**What changes:**
Decisões estratégicas viram auditáveis. Você para de re-debater coisas que já decidiu.

---

## Common patterns across personas

Independente do uso, alguns padrões emergem:

### 1. The Monday morning ritual
Most users start their week with `/proximo-passo` or `revisar-semana`. The hook auto-loads context. The skill processes the data. You get clarity in 90 seconds.

### 2. The weekly archival
Friday afternoons, run `arquivar-pasta` on stale folders. Workspace stays clean. History is preserved.

### 3. The pre-meeting check
Before any meeting/call, run `resumo-projeto` on the relevant area. Arrive prepared. Nobody knows you didn't think about it before.

### 4. The monthly accounting
End of month, run `visao-mes`. Save the HTML output. Compare month-over-month evolution. Notice patterns you couldn't see in fragments.

### 5. The "I don't know" rescue
When stuck, run `/proximo-passo`. The agent reads your objective, your history, and proposes one concrete action. Doesn't tell you what to think — gives you a thread to pull.

---

## What's NOT a good use case

To be honest:

- **One-off tasks.** If you don't have ongoing work, Solverkitty is overkill. Use vanilla Claude Code.
- **Highly collaborative work.** Solverkitty is single-user. Teams need different tools (or a fork of this thinking).
- **Work where everything fits in your head.** If you have 1 project and 1 day at a time, you don't need infrastructure.
- **Pure brainstorming.** Solverkitty shines on continuous structured work, not exploratory ideation.

If you fit those, save your time and don't install. We're not selling. We're building for who needs this.

---

*Have a use case worth adding? PR welcome.*
