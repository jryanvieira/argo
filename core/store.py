"""Filesystem run store — persiste e carrega runs de otimização."""

from __future__ import annotations

import json
import shutil
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VALID_STATUSES = frozenset(
    {"keep", "discard", "crash", "timeout", "no-change", "scope-violation"}
)


@dataclass
class BenchmarkResult:
    name: str
    passed: bool
    score: float
    duration_s: float
    output: str = ""


@dataclass
class RunResult:
    score: float
    status: str
    benchmarks: list[BenchmarkResult] = field(default_factory=list)
    error: str = ""


@dataclass
class RunRecord:
    run_id: int
    timestamp: str
    status: str
    score: float
    diff: str = ""
    reasoning: str = ""
    traces_used: list[dict[str, Any]] = field(default_factory=list)
    benchmarks: list[dict[str, Any]] = field(default_factory=list)
    model: str = ""
    budget: int = 0


class Store:
    """Persiste e carrega runs no filesystem dentro de {project_path}/runs/."""

    def __init__(self, project_path: str) -> None:
        self.project_path = Path(project_path)
        self.runs_dir = self.project_path / "runs"
        self.runs_dir.mkdir(parents=True, exist_ok=True)

    def _run_dir(self, run_id: int) -> Path:
        return self.runs_dir / f"run_{run_id:03d}"

    def melhor_score_atual(self) -> float:
        """Retorna o maior score entre todos os runs com status 'keep'."""
        melhor = 0.0
        for record in self.carregar_runs():
            if record.status == "keep" and record.score > melhor:
                melhor = record.score
        return melhor

    def carregar_runs(self) -> list[RunRecord]:
        """Carrega todos os runs do filesystem, ordenados por run_id."""
        records: list[RunRecord] = []
        for meta_file in sorted(self.runs_dir.glob("run_*/meta.json")):
            try:
                data = json.loads(meta_file.read_text(encoding="utf-8"))
                records.append(RunRecord(**data))
            except Exception:
                continue
        return records

    def carregar_run(self, run_id: int) -> RunRecord | None:
        """Carrega um run específico pelo ID."""
        meta_file = self._run_dir(run_id) / "meta.json"
        if not meta_file.exists():
            return None
        data = json.loads(meta_file.read_text(encoding="utf-8"))
        return RunRecord(**data)

    def salvar_run(
        self,
        run_id: int,
        resultado: RunResult,
        proposta: Path | None = None,
        diff: str = "",
        traces_usados: list[dict[str, Any]] | None = None,
        reasoning: str = "",
        model: str = "",
        budget: int = 0,
    ) -> Path:
        """Salva todos os artefatos de um run no filesystem."""
        if resultado.status not in VALID_STATUSES:
            raise ValueError(f"Status inválido: {resultado.status}")

        run_dir = self._run_dir(run_id)
        run_dir.mkdir(parents=True, exist_ok=True)

        if proposta and proposta.exists():
            dest = run_dir / "proposed_harness"
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(proposta, dest)

        if diff:
            (run_dir / "diff.patch").write_text(diff, encoding="utf-8")

        if reasoning:
            (run_dir / "REASONING.md").write_text(reasoning, encoding="utf-8")

        traces = traces_usados or []
        (run_dir / "traces_usados.json").write_text(
            json.dumps(traces, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        benchmarks_data = [asdict(b) for b in resultado.benchmarks]
        (run_dir / "result.json").write_text(
            json.dumps(
                {
                    "score": resultado.score,
                    "status": resultado.status,
                    "error": resultado.error,
                    "benchmarks": benchmarks_data,
                },
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        record = RunRecord(
            run_id=run_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            status=resultado.status,
            score=resultado.score,
            diff=diff,
            reasoning=reasoning,
            traces_used=traces,
            benchmarks=benchmarks_data,
            model=model,
            budget=budget,
        )
        (run_dir / "meta.json").write_text(
            json.dumps(asdict(record), indent=2, ensure_ascii=False), encoding="utf-8"
        )

        return run_dir

    def salvar(self, status: str, run_id: int) -> None:
        """Salva um run com status simples (sem artefatos)."""
        resultado = RunResult(score=0.0, status=status)
        self.salvar_run(run_id=run_id, resultado=resultado)

    def proximo_run_id(self) -> int:
        """Retorna o próximo run_id disponível."""
        ids = [r.run_id for r in self.carregar_runs()]
        return max(ids) + 1 if ids else 0
