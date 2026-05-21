---
description: Criar nova pasta de projeto na estrutura _departamento/AAAAMM_empresa_nome
argument-hint: [nome-projeto] [departamento] [empresa] [descricao]
---

Execute o comando `/nova-pasta` conforme a secao "## Criacao de projetos" do CLAUDE.md na raiz.

Fluxo:

1. Se o usuario nao forneceu os argumentos, **pergunte um de cada vez**:
   - Departamento (area funcional: ex `financeiro`, `credito`, `fiscal`)
   - Empresa do grupo (ex `jandaia`)
   - Nome do projeto (minusculo, hifens: ex `conciliacao-bancaria`)
   - Descricao curta (1 linha)

2. Execute via Bash:

```bash
python -c "from pmo_setup import nova_pasta; nova_pasta('<nome>', '<departamento>', '<empresa>', '<descricao>')"
```

Isso cria `_<departamento>/<AAAAMM>_<empresa>_<nome>/` com a estrutura padrao e
registra no banco (com `empresa` e `departamento` como campos queryaveis).

3. Confirme ao usuario: pasta criada (mostre o caminho relativo), banco atualizado, GLOSSARIO.md atualizado.

4. Pergunte se o usuario ja quer comecar a trabalhar no projeto (abrir `01_input/instrucoes.md` para preencher a fonte de dados).

**NUNCA crie pasta de projeto manualmente (mkdir/Write).** Sempre via `nova_pasta` — senao quebra a organizacao e o registro no banco.

Argumentos recebidos: $ARGUMENTS
