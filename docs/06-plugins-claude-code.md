# Como funcionam os plugins do Claude Code

## Estrutura obrigatória

```
meu-plugin/
├── .claude-plugin/
│   ├── plugin.json        ← manifesto do plugin
│   └── marketplace.json   ← necessário para instalação via /plugin marketplace add
├── skills/
│   └── minha-skill/
│       └── SKILL.md       ← cada skill é uma PASTA com SKILL.md dentro
├── commands/
│   └── meu-comando.md     ← commands são arquivos .md diretos
└── agents/                ← opcional
    └── meu-agente.md
```

---

## .claude-plugin/plugin.json

```json
{
  "name": "meu-plugin",
  "displayName": "Meu Plugin",
  "version": "1.0.0",
  "description": "O que o plugin faz",
  "author": {
    "name": "seu-usuario",
    "url": "https://github.com/seu-usuario"
  },
  "repository": "https://github.com/seu-usuario/meu-plugin",
  "license": "MIT",
  "keywords": ["tag1", "tag2"],
  "skills": "./skills/",
  "commands": ["./commands/"]
}
```

**Único campo obrigatório:** `name`

---

## .claude-plugin/marketplace.json

Necessário para que o repositório seja reconhecido como fonte instalável.

```json
{
  "name": "meu-plugin",
  "owner": { "name": "seu-usuario" },
  "description": "Descrição curta",
  "plugins": [
    {
      "name": "meu-plugin",
      "displayName": "Meu Plugin",
      "description": "O que o plugin faz",
      "version": "1.0.0",
      "source": "./"
    }
  ]
}
```

---

## Skills

Cada skill é uma **pasta** com um arquivo `SKILL.md` dentro.  
O frontmatter YAML é obrigatório.

```
skills/
└── minha-skill/
    └── SKILL.md
```

```markdown
---
description: Uma linha descrevendo quando essa skill é usada
---

Conteúdo da skill — instruções para o Claude Code executar.
```

---

## Commands

Commands são arquivos `.md` diretos (não precisam de pasta).  
O frontmatter YAML é obrigatório.

```
commands/
└── meu-comando.md
```

```markdown
---
description: O que esse comando faz
---

# Comando: /meu-plugin meu-comando

Instruções detalhadas de execução...
```

---

## Agents (opcional)

```
agents/
└── meu-agente.md
```

```markdown
---
name: meu-agente
description: Quando invocar esse agente
model: sonnet
effort: medium
maxTurns: 20
---

System prompt do agente...
```

---

## Como instalar

```bash
# Passo 1 — registra o repositório como marketplace
/plugin marketplace add seu-usuario/meu-plugin

# Passo 2 — instala o plugin desse marketplace
/plugin install meu-plugin@meu-plugin

# Para verificar / ver erros de carregamento
/plugin
```

> **Atenção:** `/plugin add` não existe. O fluxo correto é sempre `marketplace add` → `install`.

---

## Verificar instalação

Após instalar, abra `/plugin` e verifique:
- **Installed** — lista plugins ativos
- **Errors** — mostra falhas de carregamento (schema inválido, arquivo faltando, etc.)

---

## Limitações conhecidas

| Situação | Comportamento |
|----------|---------------|
| Remote Control (web app, IDE extension) | `/plugin` não funciona — apenas no CLI |
| Plugin instalado mas não ativo | Rode `/reload-plugins` na sessão atual |
| `plugin.yaml` em vez de `plugin.json` | Ignorado silenciosamente |
| Skill como arquivo `.md` direto | Ignorada — precisa ser pasta com `SKILL.md` |

---

## Checklist antes de publicar

- [ ] `.claude-plugin/plugin.json` com `name` preenchido
- [ ] `.claude-plugin/marketplace.json` com `plugins[].source` apontando para `./`
- [ ] Cada skill em `skills/nome/SKILL.md` com frontmatter `description:`
- [ ] Cada command em `commands/nome.md` com frontmatter `description:`
- [ ] Testado com `/plugin marketplace add` + `/plugin install`
