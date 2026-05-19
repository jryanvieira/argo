# ARGO — Agent Runtime Goal Optimizer
## Prompt para Claude Code — v2 (Plugin-first, sem API key externa)

Vamos construir o **ARGO** como um Claude Code plugin instalável via URL,
sem necessidade de API key externa. O Claude Code é o runtime — ele já tem
acesso ao modelo internamente.

---

## Instalação alvo

```bash
# instala o plugin uma vez por máquina
/plugin add github.com/seu-user/argo

# inicializa num projeto
/argo init

# roda o loop de otimização
/argo run --budget 3
```

Zero configuração. Zero API key. Zero pip install obrigatório.

---

## Arquitetura: plugin como runtime, filesystem como memória

O Claude Code **é** o propositor. O ARGO orquestra o loop ao redor dele,
usando o filesystem para acumular evidência entre sessões — exatamente como
o paper Meta-Harness da Stanford descreve.

```
sessão 1: você usa Claude Code normalmente
               ↓ traces salvos em ~/.claude/projects/
sessão 2: /argo run
               ↓ lê traces de falha
               ↓ Claude Code propõe novo harness
               ↓ testa em sandbox
               ↓ promove se melhorou
sessão 3: Claude Code começa com harness melhorado
```

O loop roda **dentro** do Claude Code, mas o estado persiste **fora** dele
no filesystem. Cada sessão é melhor que a anterior.

---

## Estrutura do plugin

```
argo/
├── commands/
│   ├── init.md          ← /argo init
│   ├── run.md           ← /argo run --budget N
│   ├── inspect.md       ← /argo inspect
│   ├── logs.md          ← /argo logs
│   └── benchmark.md     ← /argo benchmark add
│
├── skills/
│   ├── optimizer.md     ← skill: como rodar o loop de otimização
│   ├── tracer.md        ← skill: como ler e interpretar traces de falha
│   ├── sandbox.md       ← skill: como testar propostas em isolamento
│   ├── store.md         ← skill: como salvar e carregar runs do filesystem
│   └── proposer.md      ← skill: como propor melhorias de harness com evidência
│
├── core/
│   ├── optimizer.py     ← loop central (Python, invocado pelo Claude Code)
│   ├── tracer.py        ← lê ~/.claude/projects/**/*.jsonl
│   ├── sandbox.py       ← isolamento por tmpdir + write scope
│   ├── store.py         ← filesystem run store
│   └── benchmark.py     ← executa acceptance.sh e retorna score
│
├── templates/
│   ├── CLAUDE.md.tpl    ← harness base gerado no init
│   └── benchmark/
│       ├── description.md.tpl
│       └── acceptance.sh.tpl
│
├── tests/
│   ├── test_optimizer.py
│   ├── test_tracer.py
│   ├── test_store.py
│   └── test_sandbox.py
│
├── docs/
│   ├── 01-conceitos.md      ← o que é harness, o que é o loop, o que é trace
│   ├── 02-arquitetura.md    ← como plugin + filesystem + Claude Code se conectam
│   ├── 03-onboarding.md     ← instalação + primeiro run passo a passo
│   ├── 04-benchmarks.md     ← como criar benchmarks do seu trabalho real
│   └── 05-backends.md       ← como adicionar backends futuros (Ollama, API)
│
├── scripts/
│   └── install.sh       ← setup inicial: cria estrutura, verifica dependências
│
├── plugin.yaml          ← manifesto do plugin (nome, versão, comandos, skills)
├── README.md            ← quickstart em 3 comandos + badges
├── CONTRIBUTING.md
├── CHANGELOG.md         ← começa em v0.1.0
└── LICENSE              ← Apache 2.0
```

---

## O loop central (core/optimizer.py)

Arquivo Python puro, invocado pelo Claude Code via Bash tool.
Sem dependências externas — só stdlib.

```python
import json, shutil, subprocess, tempfile
from pathlib import Path

def run(project_path: str, budget: int, require_approval: bool = False):

    store = Store(project_path)
    tracer = Tracer()
    melhor_score = store.melhor_score_atual()

    for i in range(budget):

        # 1. lê histórico completo de runs anteriores
        história = store.carregar_runs()

        # 2. extrai traces de falha das sessões recentes do Claude Code
        traces = tracer.extrair_falhas(últimos_N_dias=7)

        # 3. escreve contexto para o Claude Code propor
        #    (o Claude Code lê esse arquivo e gera a proposta)
        contexto = montar_contexto(história, traces, ler_harness(project_path))
        Path(f"{project_path}/.argo/context.md").write_text(contexto)

        # PAUSA: o Claude Code lê context.md e escreve proposed_harness/
        # (isso é orquestrado pela skill proposer.md)

        proposta_path = Path(f"{project_path}/.argo/proposed_harness")

        # 4. valida escopo
        if viola_escopo(proposta_path, allowed=["harness/"]):
            store.salvar(status="scope-violation", run_id=i)
            continue

        # 5. testa em sandbox isolado
        with tempfile.TemporaryDirectory() as sandbox:
            shutil.copytree(proposta_path, f"{sandbox}/harness")
            resultado = executar_benchmarks(sandbox, project_path)

        # 6. salva tudo no filesystem
        store.salvar_run(
            run_id=i,
            proposta=proposta_path,
            resultado=resultado,
            diff=gerar_diff(project_path, proposta_path)
        )

        # 7. aprovação humana se pedida
        if require_approval:
            exibir_diff_e_aguardar(store.carregar_run(i))

        # 8. promove se melhorou
        if resultado.score > melhor_score:
            promover(proposta_path, project_path)
            melhor_score = resultado.score
            print(f"✅ Run {i}: score {resultado.score:.1%} — promovido")
        else:
            print(f"↩️  Run {i}: score {resultado.score:.1%} — descartado")
```

**Importante:** o Python nunca chama a API diretamente.
Ele prepara o contexto, salva no filesystem, e o Claude Code
(orquestrado pelas skills) lê e escreve as propostas.

---

## As skills

As skills ensinam o Claude Code como executar cada parte do loop.
Seguem o padrão agentskills.io (mesmo padrão do TRUST).

### skills/proposer.md
```
Você é o propositor do ARGO. Seu trabalho é melhorar harnesses de agentes.

Ao ser invocado:
1. Leia .argo/context.md — contém o harness atual, histórico de runs e traces de falha
2. Analise os padrões de falha: onde o agente travou, quantos turnos desperdiçou
3. Proponha mudanças específicas e justificadas no harness
4. Escreva os arquivos propostos em .argo/proposed_harness/
5. Documente seu raciocínio em .argo/proposed_harness/REASONING.md

Regras:
- Só modifique arquivos dentro de harness/ (nunca o código do produto)
- Cada mudança deve ter uma justificativa baseada em evidência dos traces
- Se não há evidência suficiente para melhorar, escreva REASONING.md
  explicando por que e deixe o harness inalterado (status: no-change)
```

### skills/tracer.md
```
Você sabe interpretar traces de sessões do Claude Code.

Sinais de harness fraco:
- Sessão com mais de 8 turnos para tarefa simples
- Mesmo comando bash executado 3+ vezes seguidas
- Usuário enviou mensagem curta corrigindo o agente (ex: "não, usa pytest")
- Agente perguntou algo que deveria saber pelo CLAUDE.md

Como extrair:
- Leia os JSONLs em ~/.claude/projects/**/*.jsonl
- Filtre pelos três sinais acima
- Para cada falha, identifique: o que o agente tentou, onde errou, como foi corrigido
- Exporte como lista estruturada para o context.md
```

### skills/sandbox.md
```
Antes de promover qualquer proposta de harness:

1. Copie proposed_harness/ para um diretório temporário
2. Execute cada benchmark em acceptance.sh dentro desse diretório
3. Registre: passou/falhou, tempo de execução, output
4. NUNCA modifique o workspace original antes de aprovação
5. Se qualquer benchmark crashar, status = crash, não promova
```

---

## Os comandos

### commands/run.md
```
Comando: /argo run

Parâmetros:
  --budget N          número máximo de iterações (default: 3)
  --require-approval  pausa antes de cada promoção para confirmação humana

Execução:
1. Chame Bash: python core/optimizer.py --budget {N} --project {cwd}
2. Para cada iteração que o optimizer pausar para proposta:
   a. Leia .argo/context.md
   b. Use a skill proposer para gerar .argo/proposed_harness/
   c. Sinalize o optimizer para continuar: touch .argo/proposal_ready
3. Ao final, exiba tabela resumo com rich: run_id, score, status, tempo
```

### commands/init.md
```
Comando: /argo init [nome]

1. Cria estrutura de diretórios:
   harness/        ← CLAUDE.md e scripts do projeto
   benchmarks/     ← tarefas com acceptance.sh
   runs/           ← histórico de otimizações
   .argo/          ← estado interno do loop

2. Gera harness/CLAUDE.md a partir de templates/CLAUDE.md.tpl
   Personaliza com: linguagem detectada, estrutura do projeto, ferramentas encontradas

3. Gera benchmarks/example_task/ com description.md e acceptance.sh funcionais

4. Exibe próximos passos:
   - Edite harness/CLAUDE.md com suas regras reais
   - Adicione benchmarks do seu trabalho: /argo benchmark add
   - Rode a primeira otimização: /argo run --budget 3
```

### commands/logs.md
```
Comando: /argo logs

1. Leia todos os JSONLs em ~/.claude/projects/**/*.jsonl dos últimos 14 dias
2. Use a skill tracer para identificar padrões de falha
3. Exiba tabela com top 5 padrões:
   - Descrição do padrão
   - Frequência (quantas sessões afetadas)
   - Turnos desperdiçados em média
   - Sugestão de melhoria no harness
4. Pergunte: "Quer criar benchmarks baseados nesses padrões? [s/n]"
   Se sim: execute /argo benchmark add para cada padrão identificado
```

### commands/inspect.md
```
Comando: /argo inspect [run_id]

Sem run_id: exibe tabela de todos os runs com score, status, data, tempo
Com run_id: exibe diff completo colorido + reasoning do propositor + traces usados
```

### commands/benchmark.md
```
Comando: /argo benchmark add

Wizard interativo:
1. "Descreva uma tarefa que o agente costuma errar:"
   → usuário descreve em linguagem natural

2. "Como você sabe que a tarefa foi concluída corretamente?"
   → usuário define critério de aceitação

3. Gera benchmarks/{slug}/description.md com a descrição
4. Gera benchmarks/{slug}/acceptance.sh com o critério como script bash
5. Confirma: "Roda esse benchmark agora para validar que funciona? [s/n]"
```

---

## O store (core/store.py)

Cada run em `runs/run_NNN/`:
```
proposed_harness/     ← arquivos propostos pelo Claude Code
traces_usados.json    ← quais traces embasaram a proposta
diff.patch            ← diff vs harness atual
result.json           ← score, status, tempo por benchmark
meta.json             ← timestamp, budget, iteração, modelo usado
REASONING.md          ← por que o Claude Code fez essas mudanças
```

Status possíveis: `keep` | `discard` | `crash` | `timeout` | `no-change` | `scope-violation`

---

## O tracer (core/tracer.py)

```python
def extrair_falhas(últimos_N_dias: int = 7) -> list[FailureTrace]:
    """
    Lê ~/.claude/projects/**/*.jsonl
    Retorna sessões com sinais de harness fraco:
    - turnos > 8
    - tool calls repetidos (mesmo comando 3+ vezes)
    - intervenção manual do usuário (mensagem curta pós-erro)
    """
```

Zero configuração. Funciona com qualquer projeto que usou Claude Code.

---

## Segurança

- **Sandbox:** cada proposta testa em tmpdir isolado, nunca no workspace
- **Write scope:** proposals fora de `harness/` → `scope-violation` automático
- **Aprovação humana:** `--require-approval` mostra diff antes de promover
- **Sem API key:** zero credenciais no código ou configuração
- **Sem rede:** o loop não faz chamadas externas — só filesystem + Claude Code local

---

## plugin.yaml

```yaml
name: argo
version: 0.1.0
description: "Agent Runtime Goal Optimizer — otimiza harnesses de coding agents automaticamente"
author: seu-user

commands:
  - name: init
    description: "Inicializa ARGO num projeto"
    file: commands/init.md
  - name: run
    description: "Roda o loop de otimização"
    file: commands/run.md
  - name: inspect
    description: "Inspeciona histórico de runs"
    file: commands/inspect.md
  - name: logs
    description: "Analisa traces e lista padrões de falha"
    file: commands/logs.md
  - name: benchmark
    description: "Gerencia benchmarks do projeto"
    file: commands/benchmark.md

skills:
  - name: optimizer
    file: skills/optimizer.md
  - name: tracer
    file: skills/tracer.md
  - name: sandbox
    file: skills/sandbox.md
  - name: store
    file: skills/store.md
  - name: proposer
    file: skills/proposer.md
```

---

## Qualidade

- Python puro, stdlib only no core (sem dependências externas obrigatórias)
- `ruff` para linting
- `pytest` cobrindo o loop completo com mocks do filesystem
- Type hints em todos os módulos Python
- Docstrings em todas as classes e funções públicas

---

## Para open source

**README.md:**
- Badge de CI, License, Status
- Quickstart em 3 comandos
- Diagrama do loop (texto ASCII)
- Diferença entre ARGO e outros frameworks (sem API key, plugin-first)

**CONTRIBUTING.md:**
- Como testar localmente sem Claude Code (FakeBackend via scripts/test_local.sh)
- Como adicionar um novo comando
- Como adicionar uma nova skill
- Padrão de PR e commit

---

## Ordem de execução — siga esta sequência

1. `plugin.yaml` + `LICENSE` (Apache 2.0) + estrutura de pastas vazia
2. `core/store.py` + `core/sandbox.py` (stdlib only, testáveis sem Claude Code)
3. `core/tracer.py` lendo os JSONLs
4. `core/benchmark.py` executando acceptance.sh
5. `core/optimizer.py` com o loop completo
6. `skills/` — todas as 5 skills
7. `commands/` — todos os 5 comandos
8. `templates/` — CLAUDE.md.tpl + benchmark templates
9. `tests/` cobrindo os módulos core
10. `scripts/install.sh`
11. `docs/` completa
12. `README.md` + `CONTRIBUTING.md` + `CHANGELOG.md`

**Após cada etapa:** confirma que os testes passam antes de avançar.

---

## Validação final

Estes comandos devem funcionar do zero após instalação:

```bash
/plugin add github.com/seu-user/argo
/argo init meu-projeto
/argo logs
/argo benchmark add
/argo run --budget 3
/argo inspect
```

Nenhum desses comandos deve pedir API key, pip install adicional,
ou qualquer configuração além do próprio Claude Code já instalado.
