"""Executa benchmarks e retorna score agregado."""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

from core.store import BenchmarkResult, RunResult


def executar_benchmarks(
    sandbox_dir: str | Path,
    project_path: str | Path,
    timeout_s: int = 60,
) -> RunResult:
    """
    Descobre e executa todos os acceptance.sh em {project_path}/benchmarks/.
    Retorna RunResult com score agregado.
    """
    project_path = Path(project_path)
    sandbox_dir = Path(sandbox_dir)
    benchmarks_dir = project_path / "benchmarks"

    if not benchmarks_dir.exists():
        return RunResult(
            score=0.0,
            status="crash",
            error=f"diretório benchmarks não encontrado em {project_path}",
        )

    bench_dirs = [d for d in sorted(benchmarks_dir.iterdir()) if d.is_dir()]
    if not bench_dirs:
        return RunResult(score=0.0, status="crash", error="nenhum benchmark encontrado")

    results: list[BenchmarkResult] = []
    any_crash = False

    for bench_dir in bench_dirs:
        acceptance = bench_dir / "acceptance.sh"
        if not acceptance.exists():
            continue

        start = time.monotonic()
        try:
            proc = subprocess.run(
                ["bash", str(acceptance)],
                capture_output=True,
                text=True,
                timeout=timeout_s,
                cwd=str(sandbox_dir),
            )
            duration = time.monotonic() - start
            passed = proc.returncode == 0
            output = (proc.stdout + proc.stderr).strip()
            results.append(
                BenchmarkResult(
                    name=bench_dir.name,
                    passed=passed,
                    score=1.0 if passed else 0.0,
                    duration_s=round(duration, 3),
                    output=output[:2000],
                )
            )
        except subprocess.TimeoutExpired:
            duration = time.monotonic() - start
            any_crash = True
            results.append(
                BenchmarkResult(
                    name=bench_dir.name,
                    passed=False,
                    score=0.0,
                    duration_s=round(duration, 3),
                    output=f"timeout após {timeout_s}s",
                )
            )
        except Exception as exc:
            any_crash = True
            results.append(
                BenchmarkResult(
                    name=bench_dir.name,
                    passed=False,
                    score=0.0,
                    duration_s=0.0,
                    output=f"crash: {exc}",
                )
            )

    if not results:
        return RunResult(score=0.0, status="crash", error="nenhum acceptance.sh encontrado")

    score = sum(r.score for r in results) / len(results)
    status = "crash" if any_crash else ("keep" if score > 0 else "discard")

    return RunResult(score=round(score, 4), status=status, benchmarks=results)


def listar_benchmarks(project_path: str | Path) -> list[str]:
    """Retorna nomes de todos os benchmarks disponíveis."""
    benchmarks_dir = Path(project_path) / "benchmarks"
    if not benchmarks_dir.exists():
        return []
    return [d.name for d in sorted(benchmarks_dir.iterdir()) if d.is_dir()]
