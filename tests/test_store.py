"""Testes para core/store.py."""

import json
import tempfile
from pathlib import Path

import pytest

from core.store import BenchmarkResult, RunRecord, RunResult, Store


@pytest.fixture
def tmp_project(tmp_path):
    return tmp_path


def test_store_vazio_retorna_score_zero(tmp_project):
    store = Store(str(tmp_project))
    assert store.melhor_score_atual() == 0.0


def test_store_vazio_retorna_lista_vazia(tmp_project):
    store = Store(str(tmp_project))
    assert store.carregar_runs() == []


def test_proximo_run_id_vazio(tmp_project):
    store = Store(str(tmp_project))
    assert store.proximo_run_id() == 0


def test_salvar_e_carregar_run(tmp_project):
    store = Store(str(tmp_project))
    resultado = RunResult(
        score=0.75,
        status="keep",
        benchmarks=[BenchmarkResult(name="t1", passed=True, score=1.0, duration_s=0.1)],
    )
    store.salvar_run(run_id=0, resultado=resultado, diff="--- a\n+++ b\n", reasoning="test")

    runs = store.carregar_runs()
    assert len(runs) == 1
    assert runs[0].score == 0.75
    assert runs[0].status == "keep"


def test_melhor_score_apenas_keep(tmp_project):
    store = Store(str(tmp_project))

    store.salvar_run(run_id=0, resultado=RunResult(score=0.5, status="keep"))
    store.salvar_run(run_id=1, resultado=RunResult(score=0.9, status="discard"))
    store.salvar_run(run_id=2, resultado=RunResult(score=0.7, status="keep"))

    assert store.melhor_score_atual() == 0.7


def test_carregar_run_especifico(tmp_project):
    store = Store(str(tmp_project))
    store.salvar_run(run_id=5, resultado=RunResult(score=0.3, status="discard"))

    record = store.carregar_run(5)
    assert record is not None
    assert record.run_id == 5
    assert record.score == 0.3


def test_carregar_run_inexistente(tmp_project):
    store = Store(str(tmp_project))
    assert store.carregar_run(999) is None


def test_status_invalido_levanta_erro(tmp_project):
    store = Store(str(tmp_project))
    with pytest.raises(ValueError, match="Status inválido"):
        store.salvar_run(run_id=0, resultado=RunResult(score=0.0, status="invalid"))


def test_proximo_run_id_incrementa(tmp_project):
    store = Store(str(tmp_project))
    store.salvar_run(run_id=0, resultado=RunResult(score=0.0, status="discard"))
    store.salvar_run(run_id=1, resultado=RunResult(score=0.0, status="discard"))
    assert store.proximo_run_id() == 2


def test_artefatos_salvos_no_filesystem(tmp_project):
    store = Store(str(tmp_project))
    store.salvar_run(
        run_id=0,
        resultado=RunResult(score=0.5, status="keep"),
        diff="diff content",
        reasoning="reasoning content",
    )

    run_dir = tmp_project / "runs" / "run_000"
    assert (run_dir / "meta.json").exists()
    assert (run_dir / "result.json").exists()
    assert (run_dir / "diff.patch").read_text() == "diff content"
    assert (run_dir / "REASONING.md").read_text() == "reasoning content"
