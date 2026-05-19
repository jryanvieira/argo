# Benchmarks — Como criar testes do seu trabalho real

## O que faz um bom benchmark?

Um bom benchmark:
- Representa uma falha **real** que você observou
- Tem critério de aceitação **verificável automaticamente**
- É **determinístico** — passa sempre se o harness cobre o requisito
- Roda **rápido** — idealmente abaixo de 5 segundos

## Padrões de acceptance.sh

### Verificar instrução presente no CLAUDE.md

```bash
#!/usr/bin/env bash
set -euo pipefail
# O harness deve mencionar pytest como framework de testes
grep -qi "pytest" harness/CLAUDE.md || { echo "FAIL: pytest não mencionado"; exit 1; }
```

### Verificar múltiplas instruções

```bash
#!/usr/bin/env bash
set -euo pipefail
# O harness deve mencionar testes E commit
grep -qi "test\|pytest\|unittest" harness/CLAUDE.md || exit 1
grep -qi "commit\|git" harness/CLAUDE.md || exit 1
```

### Verificar arquivo existe

```bash
#!/usr/bin/env bash
set -euo pipefail
[ -f "harness/CLAUDE.md" ] || exit 1
[ -f "harness/scripts/setup.sh" ] || exit 1
```

### Verificar padrão com contexto

```bash
#!/usr/bin/env bash
set -euo pipefail
# O harness deve ter seção de "o que não fazer"
grep -qi "não faça\|nunca\|avoid\|don't\|do not" harness/CLAUDE.md || {
    echo "FAIL: harness sem seção de restrições"
    exit 1
}
```

## Exemplos por tipo de projeto

### Projeto Python

```bash
#!/usr/bin/env bash
set -euo pipefail
# Harness deve especificar: pytest, não unittest
grep -qi "pytest" harness/CLAUDE.md || exit 1
# E proibir prints em testes
grep -qi "print\|sem print\|no print" harness/CLAUDE.md || exit 1
```

### Projeto Go

```bash
#!/usr/bin/env bash
set -euo pipefail
grep -q "go test" harness/CLAUDE.md || exit 1
grep -qi "gofmt\|goimports\|golangci" harness/CLAUDE.md || exit 1
```

### Projeto com banco de dados

```bash
#!/usr/bin/env bash
set -euo pipefail
# O harness deve alertar sobre migrations
grep -qi "migration\|migração\|schema" harness/CLAUDE.md || exit 1
```

## Anti-padrões a evitar

**Ruim — testa o código do produto, não o harness:**
```bash
# ERRADO: isso testa se o código funciona, não se o harness é bom
cd projeto && python -m pytest tests/
```

**Ruim — critério subjetivo:**
```bash
# ERRADO: impossível automatizar
echo "O agente melhorou? [s/n]"
```

**Bom — testa se o harness contém a instrução necessária:**
```bash
grep -qi "rodar testes antes de commitar" harness/CLAUDE.md || exit 1
```

## Ciclo benchmark → run → melhoria

1. Observe uma falha no Claude Code
2. `/argo benchmark add` — descreva a falha e o critério
3. `/argo run` — o ARGO propõe um harness que faça o benchmark passar
4. Inspecione: `/argo inspect` — veja o que foi mudado
5. Use o Claude Code novamente — observe se a falha sumiu
