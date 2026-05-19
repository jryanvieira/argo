#!/usr/bin/env bash
# {{title}}
# Critério: {{acceptance_criteria}}
# Gerado pelo ARGO em {{created_at}}
set -euo pipefail

# Verifique se o harness existe
[ -d "harness" ] || { echo "FAIL: diretório harness/ não encontrado"; exit 1; }
[ -f "harness/CLAUDE.md" ] || { echo "FAIL: harness/CLAUDE.md não encontrado"; exit 1; }

# TODO: adicione suas verificações aqui
# Exemplos:
#
# Verificar se instrução existe no CLAUDE.md:
# grep -qi "pytest" harness/CLAUDE.md || { echo "FAIL: pytest não mencionado no CLAUDE.md"; exit 1; }
#
# Verificar estrutura de arquivos:
# [ -f "harness/scripts/setup.sh" ] || { echo "FAIL: setup.sh não encontrado"; exit 1; }
#
# Verificar padrão no conteúdo:
# grep -qE "rodar testes|run tests" harness/CLAUDE.md || exit 1

echo "PASS: {{title}}"
exit 0
