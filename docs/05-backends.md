# Backends — Como adicionar suporte a outros modelos

## Arquitetura atual

O ARGO v0.1.0 usa o Claude Code como único backend. O modelo é invocado
implicitamente — o Python prepara o contexto e o Claude Code (com seu modelo
interno) lê e propõe.

Esse design tem zero configuração, mas é acoplado ao Claude Code.

## Como adicionar um backend alternativo

Para suportar outros modelos (Ollama, OpenAI, Claude API direta), o ponto
de extensão é a etapa de proposta no loop:

```python
# Em core/optimizer.py, após escrever context.md:
# HOJE (Claude Code implícito):
#   aguardar_proposta(argo_dir)  # aguarda proposal_ready

# AMANHÃ (backend plugável):
#   backend = carregar_backend(config)
#   backend.propor(context_path, proposta_path)
```

### Interface do backend

```python
from abc import ABC, abstractmethod
from pathlib import Path

class Backend(ABC):
    @abstractmethod
    def propor(self, context_path: Path, proposta_path: Path) -> None:
        """
        Lê context_path, escreve proposta em proposta_path/harness/
        e cria proposta_path/REASONING.md.
        """
        ...
```

### Exemplo: backend Ollama

```python
import httpx
from pathlib import Path

class OllamaBackend(Backend):
    def __init__(self, model: str = "llama3", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    def propor(self, context_path: Path, proposta_path: Path) -> None:
        context = context_path.read_text()
        response = httpx.post(
            f"{self.base_url}/api/generate",
            json={"model": self.model, "prompt": context, "stream": False},
            timeout=120,
        )
        # parse response e escrever arquivos...
```

### Exemplo: backend Claude API

```python
import anthropic
from pathlib import Path

class ClaudeAPIBackend(Backend):
    def __init__(self, model: str = "claude-opus-4-7"):
        self.client = anthropic.Anthropic()  # lê ANTHROPIC_API_KEY do env
        self.model = model

    def propor(self, context_path: Path, proposta_path: Path) -> None:
        context = context_path.read_text()
        message = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[{"role": "user", "content": context}],
        )
        # parse e escrever arquivos...
```

## Configuração futura (plugin.yaml)

```yaml
backend:
  type: claude-code   # padrão, sem configuração
  # type: ollama
  # model: llama3
  # url: http://localhost:11434
  #
  # type: claude-api
  # model: claude-opus-4-7
  # (requer ANTHROPIC_API_KEY no ambiente)
```

## Por que não implementar agora?

O Claude Code como backend resolve 100% do caso de uso atual sem:
- Gerenciar API keys
- Lidar com rate limits e billing
- Adicionar dependências externas

Backends alternativos fazem sentido quando você precisa de:
- Execução offline completa (Ollama local)
- Custo por token controlado
- Modelo diferente para propostas

Contribuições são bem-vindas. Veja `CONTRIBUTING.md`.
