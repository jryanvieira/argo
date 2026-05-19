"""Testes para core/tracer.py."""

import json
import tempfile
from pathlib import Path

import pytest

from core.tracer import (
    FailureTrace,
    Tracer,
    _count_turns,
    _extract_tool_calls,
    _find_repeated_commands,
    _find_user_corrections,
    _parse_jsonl,
)


def make_entry(role: str, content, tool_calls=None):
    msg = {"role": role, "content": content}
    if tool_calls:
        msg["content"] = tool_calls
    return {"message": msg, "timestamp": "2026-05-19T10:00:00Z"}


def make_bash_entry(command: str):
    return {
        "message": {
            "role": "assistant",
            "content": [
                {
                    "type": "tool_use",
                    "name": "Bash",
                    "input": {"command": command},
                }
            ],
        },
        "timestamp": "2026-05-19T10:00:00Z",
    }


def test_parse_jsonl_valido(tmp_path):
    f = tmp_path / "session.jsonl"
    f.write_text('{"message": {"role": "user", "content": "hi"}}\n{"invalid"}\n')
    entries = _parse_jsonl(f)
    assert len(entries) == 1


def test_parse_jsonl_inexistente(tmp_path):
    assert _parse_jsonl(tmp_path / "nope.jsonl") == []


def test_count_turns():
    entries = [
        make_entry("user", "hello"),
        make_entry("assistant", "hi"),
        make_entry("user", "thanks"),
    ]
    assert _count_turns(entries) == 3


def test_extract_tool_calls():
    entries = [
        make_bash_entry("git status"),
        make_bash_entry("pytest"),
        make_entry("user", "ok"),
    ]
    commands = _extract_tool_calls(entries)
    assert commands == ["git status", "pytest"]


def test_find_repeated_commands_threshold():
    commands = ["git status", "git status", "git status", "pytest"]
    repeated = _find_repeated_commands(commands, threshold=3)
    assert "git status" in repeated
    assert "pytest" not in repeated


def test_find_repeated_commands_abaixo_threshold():
    commands = ["git status", "git status", "pytest"]
    assert _find_repeated_commands(commands, threshold=3) == []


def test_tracer_sessao_longa(tmp_path):
    projects_dir = tmp_path / "projects" / "my-project"
    projects_dir.mkdir(parents=True)

    entries = []
    for i in range(10):
        entries.append(make_entry("user", f"msg {i}"))
        entries.append(make_entry("assistant", f"resp {i}"))

    jsonl = projects_dir / "session1.jsonl"
    jsonl.write_text("\n".join(json.dumps(e) for e in entries))

    tracer = Tracer(projects_dir=tmp_path / "projects")
    traces = tracer.extrair_falhas(últimos_N_dias=30)

    assert len(traces) == 1
    assert traces[0].turn_count == 20
    assert any("turnos" in s for s in traces[0].signals)


def test_tracer_sem_sinais_nao_retorna(tmp_path):
    projects_dir = tmp_path / "projects" / "clean-project"
    projects_dir.mkdir(parents=True)

    entries = [make_entry("user", "ok"), make_entry("assistant", "done")]
    jsonl = projects_dir / "session.jsonl"
    jsonl.write_text("\n".join(json.dumps(e) for e in entries))

    tracer = Tracer(projects_dir=tmp_path / "projects")
    traces = tracer.extrair_falhas(últimos_N_dias=30)
    assert traces == []


def test_tracer_projetos_inexistente(tmp_path):
    tracer = Tracer(projects_dir=tmp_path / "nope")
    assert tracer.extrair_falhas() == []


def test_formatar_para_contexto_vazio():
    tracer = Tracer()
    resultado = tracer.formatar_para_contexto([])
    assert "Nenhum trace" in resultado


def test_formatar_para_contexto_com_traces():
    tracer = Tracer()
    trace = FailureTrace(
        session_id="abc123",
        project="my-project",
        timestamp="2026-05-19T10:00:00Z",
        signals=["sessão longa: 12 turnos"],
        turn_count=12,
        repeated_commands=[],
        user_corrections=[],
    )
    resultado = tracer.formatar_para_contexto([trace])
    assert "my-project" in resultado
    assert "abc123" in resultado
    assert "12 turnos" in resultado
