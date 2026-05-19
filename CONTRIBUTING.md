# Contribuindo com o ARGO

## Setup local

```bash
git clone https://github.com/seu-user/argo
cd argo
python -m pytest tests/
```

Sem dependências externas — só Python stdlib + pytest para os testes.

## Testando sem Claude Code

Para rodar o loop completo sem Claude Code, use o modo `--no-interactive`
e coloque uma proposta manualmente:

```bash
# 1. Crie um projeto de teste
mkdir /tmp/test-project
cd /tmp/test-project
mkdir -p harness benchmarks/smoke .argo/proposed_harness/harness

# 2. Crie harness base
echo "# harness base" > harness/CLAUDE.md

# 3. Crie benchmark
echo '#!/bin/bash
grep -qi "teste" harness/CLAUDE.md || exit 1' > benchmarks/smoke/acceptance.sh
chmod +x benchmarks/smoke/acceptance.sh

# 4. Crie proposta
echo "# harness com teste" > .argo/proposed_harness/harness/CLAUDE.md
echo "# Reasoning\nAdicionei instrução de teste" > .argo/proposed_harness/REASONING.md

# 5. Rode sem modo interativo
cd /caminho/do/argo
python core/optimizer.py --project /tmp/test-project --budget 1 --no-interactive
```

## Como adicionar um novo comando

1. Crie `commands/meu-comando.md` seguindo o padrão dos existentes
2. Adicione a entrada em `plugin.yaml` sob `commands:`
3. Documente em `docs/`

## Como adicionar uma nova skill

1. Crie `skills/minha-skill.md` com as instruções para o Claude Code
2. Adicione a entrada em `plugin.yaml` sob `skills:`
3. Referencie a skill nos comandos que a utilizam

## Padrão de PR

- Uma mudança por PR
- Testes passando: `python -m pytest tests/`
- Lint: `ruff check core/ tests/`
- Descrição explica o *porquê*, não o *o quê*

## Padrão de commit

```
tipo: descrição curta em português

feat: adiciona comando /argo status
fix: corrige score parcial quando benchmark crasha
test: cobre edge case de proposta vazia no store
docs: explica invariante do sandbox
```

## Adicionando um backend alternativo

Veja [docs/05-backends.md](docs/05-backends.md) para a interface esperada.
O ponto de extensão é a etapa de proposta em `core/optimizer.py`.

## Estrutura de testes

```
tests/
├── test_store.py      ← Store: salvar, carregar, score, proximo_id
├── test_tracer.py     ← Tracer: parse JSONL, sinais, formatar
├── test_sandbox.py    ← Sandbox: escopo, execução, score parcial
└── test_optimizer.py  ← loop completo com --no-interactive
```

Todos os testes usam `tmp_path` do pytest — sem estado global, sem side effects.
