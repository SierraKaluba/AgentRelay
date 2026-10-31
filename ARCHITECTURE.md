# AgentRelay — Architecture

AgentRelay orchestre plusieurs **agents de codage** (Claude Code, Codex, OpenCode) et conserve le contexte quand on bascule de l'un à l'autre. Un **cerveau Gemma** décide, à chaque étape, quel agent est le mieux placé pour la suivante.

## Vue d'ensemble

```
                    ┌──────────────────────┐
                    │  Gemma 3 27B (brain) │  « cette étape → opencode »
                    │  Google AI Studio    │
                    └──────────▲───────────┘
                               │ decide_next(state)
                               │
   ┌──────┐  CLI / HTTP   ┌────┴────────┐  AGENTS.md   ┌──────────────┐
   │ User │ ────────────► │ AgentRelay  │ ───────────► │ Claude Code  │
   └──────┘               │ (orchestr.) │              │ Codex        │
                          │             │              │ OpenCode     │
                          └────┬────────┘              └──────────────┘
                               │ /api/status
                               ▼
                       ┌───────────────┐
                       │  Dashboard    │  (React, built with Lovable)
                       │  (frontend/)  │
                       └───────────────┘
```

## Composants

### 1. CLI (`agentrelay/cli.py`)
Point d'entrée utilisateur. Click.
- `agentrelay start "<goal>" [--auto]`
- `agentrelay next [--output-text "..."]`
- `agentrelay status | stop | serve`

### 2. Orchestrator (`agentrelay/orchestrator.py`)
Coordonne cerveau + contexte + agents.
- `start(goal, config, auto)` : init session, demande au cerveau le premier agent, écrit le contexte.
- `step_next(output, config)` : consigne la sortie, redemande au cerveau, écrit le nouveau contexte.
- `get_status(config)` : renvoie l'état pour le dashboard.

### 3. Brain (`agentrelay/brain.py`)
Gemma 3 27B via Google AI Studio (endpoint OpenAI-compatible).
- `build_system_prompt(config)` : décrit les agents disponibles au cerveau.
- `decide_next(state, config)` → `{"agent", "task", "reason"}` ou `{"done": true, "reason"}` ou `None`.
- Toute erreur (réseau, JSON invalide, agent inconnu) → `None` → bascule en mode manuel.

### 4. Context (`agentrelay/context.py`)
Persistance et handoff.
- `.agentrelay/state.json` : goal, mode, current_agent, steps[].
- `AGENTS.md` ou `CLAUDE.md` : régénéré à chaque étape avec le résumé du travail passé.
- `history.jsonl` : une ligne JSON par étape.

### 5. Agents (`agentrelay/agents.py`)
Adaptateurs par agent de codage.
- `list_agents(config)` : liste avec statut (active / idle / exhausted).
- `launch(agent, config)` : subprocess en mode auto.
- `mark_done(agent, output)` : consigne la sortie.

### 6. Server (`agentrelay/server.py`)
FastAPI pour le dashboard.
- CORS ouvert sur `/api/*`.
- Endpoints : `/api/status`, `/api/start`, `/api/next`, `/api/takeover/{agent}`, `/api/mode`, `/api/stop`.

### 7. Logger (`agentrelay/logger.py`)
Logs colorés terminal + journal mémoire pour le dashboard.
- `log(event, agent, detail)`
- `recent(n)` → liste pour `/api/status`.

### 8. Frontend (`frontend/`)
Dashboard React + TypeScript + Vite + TailwindCSS.
- Polling `/api/status` toutes les 2 s.
- Vue : agents (statut, bouton take-over), last decision du cerveau, current task, activity stream.
- Toggle MANUAL / AUTO.

## Flux d'une session

```
1. agentrelay start "add JWT auth"
   └─► context.init_session()
   └─► brain.decide_next(state)                → {agent: "claude-code", ...}
   └─► context.write_task_for("claude-code")   → écrit CLAUDE.md

2. User lance claude-code → il lit CLAUDE.md → fait le travail

3. agentrelay next --output-text "plan done..."
   └─► context.append_history()
   └─► brain.decide_next(state)                → {agent: "opencode", ...}
   └─► context.write_task_for("opencode")      → écrit AGENTS.md

4. ... jusqu'à {done: true}
```

## Modes

- **MANUAL** (défaut) : AgentRelay affiche *« Lance tel agent »* et attend. Chaque étape est confirmée par l'utilisateur.
- **AUTO** : AgentRelay lance l'agent via `subprocess.Popen` et enchaîne jusqu'à `done` ou `max_steps`.

## Config attendue (`config/agents.yaml`)

```yaml
agents:
  claude-code:
    description: Best for architecture and complex reasoning
    launch_cmd: claude
    context_file: CLAUDE.md
  codex:
    description: Best for focused, dense code generation
    launch_cmd: codex
    context_file: AGENTS.md
  opencode:
    description: Multi-provider, best for varied tasks
    launch_cmd: opencode
    context_file: AGENTS.md

brain:
  provider: gemma
  base_url: https://generativelanguage.googleapis.com/v1beta/openai
  api_key_env: GEMMA_API_KEY
  model: gemma-3-27b-it
  timeout: 10
  max_input_chars: 3000

mode_default: manual
max_steps: 10
```

## Points d'extension

- **Nouvel agent** : ajouter une entrée dans `config/agents.yaml`, aucun code à modifier.
- **Nouveau cerveau** : changer `brain.provider` et `brain.base_url` (compatible OpenAI).
- **Hook native** (futur) : remplacer `agentrelay next` manuel par un hook dans l'agent (ex. Claude Code hooks).

## Stack technique

Backend : Python 3.11, FastAPI, Click, httpx, PyYAML, python-dotenv, pytest.
Frontend : React 18, TypeScript, Vite, TailwindCSS, lucide-react.
IA : Gemma 3 27B IT via Google AI Studio (endpoint OpenAI-compatible).

## Licence

MIT.
