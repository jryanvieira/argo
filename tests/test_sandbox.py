"""Testes para core/sandbox.py."""

import tempfile
from pathlib import Path

import pytest

from core.sandbox import Sandbox, SandboxConfig, viola_escopo


def make_harness(base: Path, files: dict[str, str]) -> Path:
    for rel, content in files.items():
        f = base / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(content)
    return base


def test_viola_escopo_dentro_permitido(tmp_path):
    proposta = tmp_path / "proposal"
    (proposta / "harness").mkdir(parents=True)
    (proposta / "harness" / "CLAUDE.md").write_text("ok")
    assert not viola_escopo(proposta, allowed=["harness/"])


def test_viola_escopo_fora_permitido(tmp_path):
    proposta = tmp_path / "proposal"
    (proposta / "harness").mkdir(parents=True)
    (proposta / "harness" / "CLAUDE.md").write_text("ok")
    (proposta / "src" / "main.py").parent.mkdir(parents=True)
    (proposta / "src" / "main.py").write_text("código do produto")
    assert viola_escopo(proposta, allowed=["harness/"])


def test_viola_escopo_proposta_inexistente(tmp_path):
    assert not viola_escopo(tmp_path / "nope", allowed=["harness/"])


def make_benchmark(bench_dir: Path, script: str) -> Path:
    bench_dir.mkdir(parents=True)
    acc = bench_dir / "acceptance.sh"
    acc.write_text(script)
    return bench_dir


def test_sandbox_benchmark_passa(tmp_path):
    project = tmp_path / "project"
    project.mkdir()

    benchmarks = project / "benchmarks" / "test_ok"
    make_benchmark(benchmarks, "#!/bin/bash\nexit 0\n")

    proposta = tmp_path / "proposal"
    (proposta / "harness").mkdir(parents=True)
    (proposta / "harness" / "CLAUDE.md").write_text("# harness")

    sandbox = Sandbox()
    result = sandbox.testar(proposta, project / "benchmarks", project)

    assert result.score == 1.0
    assert result.status == "keep"
    assert len(result.benchmarks) == 1
    assert result.benchmarks[0].passed


def test_sandbox_benchmark_falha(tmp_path):
    project = tmp_path / "project"
    project.mkdir()

    benchmarks = project / "benchmarks" / "test_fail"
    make_benchmark(benchmarks, "#!/bin/bash\nexit 1\n")

    proposta = tmp_path / "proposal"
    (proposta / "harness").mkdir(parents=True)

    sandbox = Sandbox()
    result = sandbox.testar(proposta, project / "benchmarks", project)

    assert result.score == 0.0
    assert result.status == "discard"
    assert not result.benchmarks[0].passed


def test_sandbox_scope_violation(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "benchmarks" / "t").mkdir(parents=True)
    (project / "benchmarks" / "t" / "acceptance.sh").write_text("exit 0")

    proposta = tmp_path / "proposal"
    (proposta / "harness").mkdir(parents=True)
    (proposta / "src").mkdir(parents=True)
    (proposta / "src" / "evil.py").write_text("bad")

    sandbox = Sandbox()
    result = sandbox.testar(proposta, project / "benchmarks", project)

    assert result.status == "scope-violation"
    assert result.score == 0.0


def test_sandbox_sem_benchmarks(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "benchmarks").mkdir()

    proposta = tmp_path / "proposal"
    (proposta / "harness").mkdir(parents=True)

    sandbox = Sandbox()
    result = sandbox.testar(proposta, project / "benchmarks", project)

    assert result.status == "crash"


def test_sandbox_score_parcial(tmp_path):
    project = tmp_path / "project"
    project.mkdir()

    make_benchmark(project / "benchmarks" / "pass", "#!/bin/bash\nexit 0\n")
    make_benchmark(project / "benchmarks" / "fail", "#!/bin/bash\nexit 1\n")

    proposta = tmp_path / "proposal"
    (proposta / "harness").mkdir(parents=True)

    sandbox = Sandbox()
    result = sandbox.testar(proposta, project / "benchmarks", project)

    assert result.score == pytest.approx(0.5)
