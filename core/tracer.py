"""Lê sessões do Claude Code e extrai sinais de harness fraco."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path


@dataclass
class FailureTrace:
    session_id: str
    project: str
    timestamp: str
    signals: list[str]
    turn_count: int
    repeated_commands: list[str]
    user_corrections: list[str]
    summary: str = ""


def _claude_projects_dir() -> Path:
    import os

    home = Path(os.path.expanduser("~"))
    return home / ".claude" / "projects"


def _parse_jsonl(path: Path) -> list[dict]:
    entries: list[dict] = []
    try:
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    except Exception:
        pass
    return entries


def _extract_tool_calls(entries: list[dict]) -> list[str]:
    """Retorna lista de comandos bash executados na sessão."""
    commands: list[str] = []
    for entry in entries:
        msg = entry.get("message", {})
        if not isinstance(msg, dict):
            continue
        content = msg.get("content", [])
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_use" and block.get("name") == "Bash":
                cmd = block.get("input", {}).get("command", "")
                if cmd:
                    commands.append(cmd.strip())
    return commands


def _find_repeated_commands(commands: list[str], threshold: int = 3) -> list[str]:
    """Retorna comandos executados threshold+ vezes seguidas."""
    repeated: list[str] = []
    i = 0
    while i < len(commands):
        j = i + 1
        while j < len(commands) and commands[j] == commands[i]:
            j += 1
        if j - i >= threshold:
            repeated.append(commands[i])
        i = j
    return list(set(repeated))


def _find_user_corrections(entries: list[dict]) -> list[str]:
    """Detecta mensagens curtas do usuário após erro do agente."""
    corrections: list[str] = []
    short_correction_re = re.compile(
        r"^(não|nao|use|usa|tenta|certo|errado|para|stop|no,|sim,|yes,|\w+\.|\w+ \w+\.?)$",
        re.IGNORECASE,
    )
    prev_was_error = False
    for entry in entries:
        role = entry.get("message", {}).get("role", "")
        content = entry.get("message", {}).get("content", "")
        if isinstance(content, list):
            text = " ".join(
                b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"
            )
        else:
            text = str(content)

        text = text.strip()

        if role == "assistant" and ("error" in text.lower() or "failed" in text.lower()):
            prev_was_error = True
            continue

        if role == "user" and prev_was_error:
            if len(text) < 60 and short_correction_re.search(text):
                corrections.append(text)
            prev_was_error = False
        else:
            prev_was_error = False

    return corrections


def _count_turns(entries: list[dict]) -> int:
    return sum(
        1
        for e in entries
        if e.get("message", {}).get("role") in ("user", "assistant")
    )


def _session_timestamp(entries: list[dict]) -> str:
    for entry in entries:
        ts = entry.get("timestamp", "")
        if ts:
            return ts
    return ""


class Tracer:
    """Extrai falhas de harness de sessões recentes do Claude Code."""

    def __init__(self, projects_dir: Path | None = None) -> None:
        self.projects_dir = projects_dir or _claude_projects_dir()

    def extrair_falhas(self, últimos_N_dias: int = 7) -> list[FailureTrace]:
        """
        Lê ~/.claude/projects/**/*.jsonl e retorna sessões com sinais de harness fraco.
        Sinais detectados:
        - turnos > 8 para sessão (tarefa simples)
        - mesmo comando bash repetido 3+ vezes seguidas
        - mensagens curtas de correção do usuário após erro
        - agente perguntou algo que deveria saber pelo CLAUDE.md
        """
        cutoff = datetime.now(timezone.utc) - timedelta(days=últimos_N_dias)
        traces: list[FailureTrace] = []

        if not self.projects_dir.exists():
            return traces

        for jsonl_file in self.projects_dir.rglob("*.jsonl"):
            entries = _parse_jsonl(jsonl_file)
            if not entries:
                continue

            ts_str = _session_timestamp(entries)
            if ts_str:
                try:
                    ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                    if ts < cutoff:
                        continue
                except ValueError:
                    pass

            turn_count = _count_turns(entries)
            commands = _extract_tool_calls(entries)
            repeated = _find_repeated_commands(commands)
            corrections = _find_user_corrections(entries)

            signals: list[str] = []
            if turn_count > 8:
                signals.append(f"sessão longa: {turn_count} turnos")
            if repeated:
                signals.append(f"comandos repetidos: {', '.join(repeated[:3])}")
            if corrections:
                signals.append(f"correções manuais: {len(corrections)}")

            if not signals:
                continue

            project = jsonl_file.parent.name
            session_id = jsonl_file.stem

            traces.append(
                FailureTrace(
                    session_id=session_id,
                    project=project,
                    timestamp=ts_str,
                    signals=signals,
                    turn_count=turn_count,
                    repeated_commands=repeated,
                    user_corrections=corrections,
                    summary=f"{project}/{session_id}: {'; '.join(signals)}",
                )
            )

        return traces

    def formatar_para_contexto(self, traces: list[FailureTrace]) -> str:
        """Formata traces como markdown para o context.md."""
        if not traces:
            return "Nenhum trace de falha encontrado nos últimos dias.\n"

        lines = ["## Traces de falha recentes\n"]
        for t in traces:
            lines.append(f"### {t.project} — {t.session_id}")
            lines.append(f"- Timestamp: {t.timestamp}")
            lines.append(f"- Turnos: {t.turn_count}")
            lines.append(f"- Sinais: {', '.join(t.signals)}")
            if t.repeated_commands:
                lines.append(f"- Comandos repetidos: {', '.join(t.repeated_commands)}")
            if t.user_corrections:
                lines.append(f"- Correções: {t.user_corrections}")
            lines.append("")

        return "\n".join(lines)
