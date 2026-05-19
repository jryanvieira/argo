"""Testes para core/optimizer.py — testa o loop sem modo interativo."""

import json
import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from core.optimizer import (
    gerar_diff,
    ler_harness,
    montar_contexto,
    promover,
)
from core.store import RunResult


def test_ler_harness_existente(tmp_path):
    harness_dir = tmp_path / "harness"
    harness_dir.mkdir()
    (harness_dir / "CLAUDE.md").write_text("# meu harness")
    resultado = ler_harness(tmp_path)
    assert "meu harness" in resultado


def test_ler_harness_inexistente(tmp_path):
    resultado = ler_harness(tmp_path)
    assert "não encontrado" in resultado


def test_montar_contexto_sem_traces():
    from core.store import RunRecord
    historia = [RunRecord(run_id=0, timestamp="2026-05-01T00:00:00Z", status="keep", score=0.5)]
    resultado = montar_contexto(historia, "Nenhum trace encontrado.\n", "# harness")
    assert "harness" in resultado
    assert "run_000" in resultado


def test_montar_contexto_com_traces():
    resultado = montar_contexto([], "## Traces\n- sinal: sessão longa\n", "# harness")
    assert "Traces" in resultado
    assert "harness" in resultado


def test_promover_substitui_harness(tmp_path):
    harness_atual = tmp_path / "harness"
    harness_atual.mkdir()
    (harness_atual / "CLAUDE.md").write_text("# antigo")

    proposta = tmp_path / "proposal"
    harness_novo = proposta / "harness"
    harness_novo.mkdir(parents=True)
    (harness_novo / "CLAUDE.md").write_text("# novo")

    promover(proposta, tmp_path)

    assert (tmp_path / "harness" / "CLAUDE.md").read_text() == "# novo"


def test_promover_sem_harness_na_proposta(tmp_path):
    harness_atual = tmp_path / "harness"
    harness_atual.mkdir()
    (harness_atual / "CLAUDE.md").write_text("# original")

    proposta = tmp_path / "proposal"
    proposta.mkdir()

    promover(proposta, tmp_path)

    assert (tmp_path / "harness" / "CLAUDE.md").read_text() == "# original"


def test_run_loop_sem_interativo(tmp_path):
    """Testa o loop completo com --no-interactive e proposta já presente."""
    project = tmp_path

    (project / "harness").mkdir()
    (project / "harness" / "CLAUDE.md").write_text("# harness base")

    bench_dir = project / "benchmarks" / "smoke"
    bench_dir.mkdir(parents=True)
    (bench_dir / "acceptance.sh").write_text("#!/bin/bash\nexit 0\n")

    argo_dir = project / ".argo"
    argo_dir.mkdir()
    proposta = argo_dir / "proposed_harness"
    harness_prop = proposta / "harness"
    harness_prop.mkdir(parents=True)
    (harness_prop / "CLAUDE.md").write_text("# harness melhorado")
    (proposta / "REASONING.md").write_text("# Reasoning\nMelhoria X")

    from core.optimizer import run
    run(project_path=str(project), budget=1, require_approval=False, interactive=False)

    store_runs = list((project / "runs").iterdir())
    assert len(store_runs) == 1
