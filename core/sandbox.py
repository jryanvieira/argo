"""Sandbox isolado para testar propostas de harness sem tocar o workspace."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from core.store import BenchmarkResult, RunResult


@dataclass
class SandboxConfig:
    timeout_per_benchmark_s: int = 60
    allowed_scope: list[str] = field(default_factory=lambda: ["harness/"])


def viola_escopo(proposta_path: Path, allowed: list[str]) -> bool:
    """Retorna True se a proposta contém arquivos fora do escopo permitido."""
    if not proposta_path.exists():
        return False
    for f in proposta_path.rglob("*"):
        if not f.is_file():
            continue
        rel = f.relative_to(proposta_path).as_posix()
        if not any(rel.startswith(a) for a in allowed):
            return True
    return False


def executar_benchmark(
    benchmark_dir: Path,
    sandbox_dir: Path,
    timeout_s: int = 60,
) -> BenchmarkResult:
    """Executa acceptance.sh de um benchmark dentro do sandbox."""
    acceptance = benchmark_dir / "acceptance.sh"
    name = benchmark_dir.name

    if not acceptance.exists():
        return BenchmarkResult(
            name=name,
            passed=False,
            score=0.0,
            duration_s=0.0,
            output=f"acceptance.sh não encontrado em {benchmark_dir}",
        )

    import time

    start = time.monotonic()
    try:
        result = subprocess.run(
            ["bash", str(acceptance)],
            capture_output=True,
            text=True,
            timeout=timeout_s,
            cwd=str(sandbox_dir),
        )
        duration = time.monotonic() - start
        passed = result.returncode == 0
        output = (result.stdout + result.stderr).strip()
        return BenchmarkResult(
            name=name,
            passed=passed,
            score=1.0 if passed else 0.0,
            duration_s=round(duration, 3),
            output=output[:2000],
        )
    except subprocess.TimeoutExpired:
        duration = time.monotonic() - start
        return BenchmarkResult(
            name=name,
            passed=False,
            score=0.0,
            duration_s=round(duration, 3),
            output=f"timeout após {timeout_s}s",
        )
    except Exception as exc:
        return BenchmarkResult(
            name=name,
            passed=False,
            score=0.0,
            duration_s=0.0,
            output=f"erro ao executar: {exc}",
        )


class Sandbox:
    """Testa uma proposta de harness em diretório temporário isolado."""

    def __init__(self, config: SandboxConfig | None = None) -> None:
        self.config = config or SandboxConfig()

    def testar(
        self,
        proposta_path: Path,
        benchmarks_path: Path,
        project_path: Path,
    ) -> RunResult:
        """
        Copia a proposta para tmpdir e executa todos os benchmarks.
        Nunca modifica o workspace original.
        """
        if viola_escopo(proposta_path, self.config.allowed_scope):
            return RunResult(score=0.0, status="scope-violation")

        if not benchmarks_path.exists() or not any(benchmarks_path.iterdir()):
            return RunResult(
                score=0.0,
                status="crash",
                error="nenhum benchmark encontrado",
            )

        with tempfile.TemporaryDirectory(prefix="argo_sandbox_") as tmp:
            sandbox_dir = Path(tmp)

            harness_dest = sandbox_dir / "harness"
            if proposta_path.exists():
                shutil.copytree(proposta_path, harness_dest)

            project_copy = sandbox_dir / "project"
            try:
                shutil.copytree(
                    project_path,
                    project_copy,
                    ignore=shutil.ignore_patterns(".argo", "runs", ".git"),
                )
            except Exception:
                pass

            results: list[BenchmarkResult] = []
            crashed = False

            for bench_dir in sorted(benchmarks_path.iterdir()):
                if not bench_dir.is_dir():
                    continue
                br = executar_benchmark(
                    bench_dir, sandbox_dir, self.config.timeout_per_benchmark_s
                )
                results.append(br)
                if not br.passed and "timeout" in br.output:
                    crashed = True

            if not results:
                return RunResult(score=0.0, status="crash", error="sem benchmarks executados")

            score = sum(b.score for b in results) / len(results)
            status = "crash" if crashed else ("keep" if score > 0 else "discard")

            return RunResult(score=round(score, 4), status=status, benchmarks=results)
