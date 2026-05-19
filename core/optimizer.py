"""Loop central do ARGO — orquestra proposta, teste e promoção de harnesses."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path

from core.benchmark import executar_benchmarks
from core.sandbox import viola_escopo
from core.store import RunResult, Store
from core.tracer import Tracer


def ler_harness(project_path: Path) -> str:
    claude_md = project_path / "harness" / "CLAUDE.md"
    if claude_md.exists():
        return claude_md.read_text(encoding="utf-8")
    return "(harness/CLAUDE.md não encontrado)"


def gerar_diff(project_path: Path, proposta_path: Path) -> str:
    harness_atual = project_path / "harness"
    try:
        result = subprocess.run(
            ["git", "diff", "--no-index", str(harness_atual), str(proposta_path / "harness")],
            capture_output=True,
            text=True,
        )
        return result.stdout
    except Exception:
        return ""


def montar_contexto(
    história: list,
    traces_md: str,
    harness_atual: str,
) -> str:
    linhas = ["# ARGO — Contexto para Propositor\n"]

    linhas.append("## Harness atual\n")
    linhas.append("```markdown")
    linhas.append(harness_atual)
    linhas.append("```\n")

    linhas.append(traces_md)

    if história:
        linhas.append("## Histórico de runs\n")
        for r in história[-5:]:
            linhas.append(
                f"- run_{r.run_id:03d}: score={r.score:.1%} status={r.status} ({r.timestamp[:10]})"
            )
        linhas.append("")

    linhas.append("## Instruções\n")
    linhas.append(
        "Analise os traces e proponha mudanças no harness. "
        "Escreva os arquivos em .argo/proposed_harness/harness/ "
        "e documente o raciocínio em .argo/proposed_harness/REASONING.md."
    )

    return "\n".join(linhas)


def aguardar_proposta(argo_dir: Path, timeout_s: int = 300) -> bool:
    """Aguarda que o Claude Code sinalize proposta pronta via .argo/proposal_ready."""
    ready_file = argo_dir / "proposal_ready"
    ready_file.unlink(missing_ok=True)

    print(
        "\n[ARGO] Aguardando proposta do Claude Code...\n"
        "       Leia .argo/context.md e escreva a proposta em .argo/proposed_harness/\n"
        "       Quando terminar: touch .argo/proposal_ready\n",
        flush=True,
    )

    start = time.monotonic()
    while time.monotonic() - start < timeout_s:
        if ready_file.exists():
            ready_file.unlink(missing_ok=True)
            return True
        time.sleep(2)

    return False


def promover(proposta_path: Path, project_path: Path) -> None:
    """Substitui harness/ pelo conteúdo proposto."""
    harness_dest = project_path / "harness"
    harness_src = proposta_path / "harness"

    if not harness_src.exists():
        return

    if harness_dest.exists():
        shutil.rmtree(harness_dest)
    shutil.copytree(harness_src, harness_dest)


def exibir_tabela_resumo(store: Store) -> None:
    runs = store.carregar_runs()
    if not runs:
        print("\n[ARGO] Nenhum run registrado.")
        return

    print("\n[ARGO] Resumo dos runs:")
    print(f"{'ID':<6} {'Score':<8} {'Status':<18} {'Data':<12}")
    print("-" * 46)
    for r in runs:
        data = r.timestamp[:10] if r.timestamp else "—"
        print(f"{r.run_id:<6} {r.score:<8.1%} {r.status:<18} {data:<12}")


def run(
    project_path: str,
    budget: int,
    require_approval: bool = False,
    interactive: bool = True,
) -> None:
    """
    Loop principal do ARGO.
    Se interactive=True, pausa para o Claude Code propor via filesystem.
    Se interactive=False, espera proposta já presente em .argo/proposed_harness/.
    """
    project = Path(project_path).resolve()
    argo_dir = project / ".argo"
    argo_dir.mkdir(parents=True, exist_ok=True)

    store = Store(str(project))
    tracer = Tracer()
    melhor_score = store.melhor_score_atual()

    print(f"[ARGO] Iniciando loop — budget={budget}, melhor score atual={melhor_score:.1%}")

    for i in range(budget):
        run_id = store.proximo_run_id()
        print(f"\n[ARGO] Iteração {i + 1}/{budget} (run_{run_id:03d})")

        história = store.carregar_runs()
        traces = tracer.extrair_falhas(últimos_N_dias=7)
        traces_md = tracer.formatar_para_contexto(traces)
        harness_atual = ler_harness(project)

        contexto = montar_contexto(história, traces_md, harness_atual)
        (argo_dir / "context.md").write_text(contexto, encoding="utf-8")

        proposta_path = argo_dir / "proposed_harness"
        if proposta_path.exists():
            shutil.rmtree(proposta_path)

        if interactive:
            ok = aguardar_proposta(argo_dir)
            if not ok:
                print(f"[ARGO] Timeout aguardando proposta — run_{run_id:03d} ignorado")
                store.salvar(status="timeout", run_id=run_id)
                continue

        if not proposta_path.exists():
            print(f"[ARGO] Proposta não encontrada — run_{run_id:03d} ignorado")
            store.salvar(status="no-change", run_id=run_id)
            continue

        if viola_escopo(proposta_path, allowed=["harness/", "REASONING.md"]):
            print(f"[ARGO] Violação de escopo detectada — run_{run_id:03d} descartado")
            store.salvar(status="scope-violation", run_id=run_id)
            continue

        resultado = executar_benchmarks(
            sandbox_dir=str(proposta_path),
            project_path=str(project),
        )

        reasoning_file = proposta_path / "REASONING.md"
        reasoning = reasoning_file.read_text(encoding="utf-8") if reasoning_file.exists() else ""

        diff = gerar_diff(project, proposta_path)
        traces_usados = [
            {"summary": t.summary, "signals": t.signals} for t in traces
        ]

        store.salvar_run(
            run_id=run_id,
            resultado=resultado,
            proposta=proposta_path,
            diff=diff,
            traces_usados=traces_usados,
            reasoning=reasoning,
        )

        if require_approval:
            print(f"\n[ARGO] run_{run_id:03d} — score {resultado.score:.1%}")
            print(f"Status: {resultado.status}")
            if diff:
                print("\nDiff:")
                print(diff[:3000])
            resposta = input("\nPromover esse harness? [s/N] ").strip().lower()
            if resposta != "s":
                print(f"[ARGO] run_{run_id:03d} descartado pelo usuário")
                continue

        if resultado.score > melhor_score:
            promover(proposta_path, project)
            melhor_score = resultado.score
            print(f"[ARGO] run_{run_id:03d}: score {resultado.score:.1%} — promovido")
        else:
            print(f"[ARGO] run_{run_id:03d}: score {resultado.score:.1%} — descartado (melhor={melhor_score:.1%})")

    exibir_tabela_resumo(store)


def main() -> None:
    parser = argparse.ArgumentParser(description="ARGO optimizer loop")
    parser.add_argument("--project", default=".", help="Caminho do projeto")
    parser.add_argument("--budget", type=int, default=3, help="Número de iterações")
    parser.add_argument("--require-approval", action="store_true")
    parser.add_argument("--no-interactive", action="store_true", help="Não aguarda proposta interativa")
    args = parser.parse_args()

    run(
        project_path=args.project,
        budget=args.budget,
        require_approval=args.require_approval,
        interactive=not args.no_interactive,
    )


if __name__ == "__main__":
    main()
