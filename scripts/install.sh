#!/usr/bin/env bash
# ARGO install script — verifica dependências e configura o ambiente
set -euo pipefail

ARGO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_MIN="3.10"

log() { echo "[ARGO] $*"; }
fail() { echo "[ARGO] ERRO: $*" >&2; exit 1; }

# Verifica Python
if ! command -v python3 &>/dev/null; then
    fail "Python 3 não encontrado. Instale Python ${PYTHON_MIN}+."
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)
MIN_MINOR=$(echo "$PYTHON_MIN" | cut -d. -f2)

if [[ "$PYTHON_MAJOR" -lt 3 ]] || [[ "$PYTHON_MAJOR" -eq 3 && "$PYTHON_MINOR" -lt "$MIN_MINOR" ]]; then
    fail "Python ${PYTHON_VERSION} encontrado, mas ${PYTHON_MIN}+ é necessário."
fi

log "Python ${PYTHON_VERSION} — OK"

# Verifica bash (para acceptance.sh)
if ! command -v bash &>/dev/null; then
    fail "bash não encontrado. Instale bash para executar os benchmarks."
fi
log "bash — OK"

# Verifica pytest (opcional mas recomendado)
if python3 -m pytest --version &>/dev/null 2>&1; then
    log "pytest — OK"
else
    log "pytest não encontrado (opcional). Para instalar: pip install pytest"
fi

# Verifica ruff (opcional)
if command -v ruff &>/dev/null; then
    log "ruff — OK"
else
    log "ruff não encontrado (opcional). Para instalar: pip install ruff"
fi

# Cria __init__.py se necessário
touch "${ARGO_DIR}/core/__init__.py" 2>/dev/null || true

# Verifica que os módulos core importam corretamente
log "Verificando módulos core..."
cd "$ARGO_DIR"

if ! python3 -c "from core.store import Store; from core.tracer import Tracer; from core.sandbox import Sandbox; from core.benchmark import executar_benchmarks; from core.optimizer import run" 2>&1; then
    fail "Erro ao importar módulos core. Verifique a instalação."
fi

log "Módulos core — OK"

echo ""
echo "╔═══════════════════════════════════════╗"
echo "║  ARGO instalado com sucesso!           ║"
echo "╚═══════════════════════════════════════╝"
echo ""
echo "Próximos passos:"
echo "  1. Navegue até o seu projeto"
echo "  2. Execute: /argo init"
echo "  3. Edite harness/CLAUDE.md com suas regras"
echo "  4. Adicione benchmarks: /argo benchmark add"
echo "  5. Rode a otimização: /argo run --budget 3"
echo ""
