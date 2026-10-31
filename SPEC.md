# SPEC — AgentRelay

> À donner à Gemma (`@SPEC.md`) avant chaque prompt.
> Langage : **Python 3.11+**. Dépendances : `fastapi`, `uvicorn`, `httpx`, `pyyaml`, `python-dotenv`, `click` (+ `pytest`).
> Frontend : React (Lovable), appelle le backend via HTTP.

## Ce que fait AgentRelay
AgentRelay est un **orchestrateur d'agents de dev** (Claude Code, Codex, OpenCode). Au lieu de taper directement dans un outil :
1. L'utilisateur dit : *« je veux ajouter l'auth JWT »* → `agentrelay start "..."`.
2. **Gemma (le cerveau) décide** quel outil est le mieux pour la première étape, et écrit la tâche + le contexte dans `.agentrelay/task.md`.
3. L'utilisateur (ou le mode auto) lance cet outil. L'outil lit `AGENTS.md` et travaille.
4. Quand l'outil a fini : `agentrelay next <sortie>` → Gemma lit la sortie, met à jour le contexte, décide **qui prend la suite**.
5. L'étape passée est enregistrée dans l'historique ; le prochain outil reprend là où le précédent s'est arrêté.
6. Dashboard web pour voir qui travaille, l'historique des bascules et le contexte en cours.

Deux modes : **manuel** (l'utilisateur confirme chaque bascule) ou **auto** (Gemma décide et enchaîne tout seul).

## Agents supportés (par défaut, config extensible)
Chacun est défini par une entrée YAML : `name`, `description` (lue par Gemma), `launch_cmd` (optionnel, pour mode auto), `context_file` (où écrire la tâche pour cet outil).

| Agent | Contexte lu | Cas d'usage typique |
|---|---|---|
| `claude-code` | `CLAUDE.md` | Architecture, raisonnement complexe |
| `codex` | `AGENTS.md` | Code dense, tâches isolées |
| `opencode` | `AGENTS.md` | Multi-provider, tâches variées |

## Arborescence
```
agentrelay/
  __init__.py
  cli.py           # P1 — commandes CLI (start, next, status, auto)
  orchestrator.py  # P1 — coordonne cerveau + contexte + agents
  server.py        # P1 — serveur FastAPI (dashboard + API)
  brain.py         # P2 — Gemma décide quel agent prend la suite
  context.py       # P3 — lit/écrit .agentrelay/state.json + AGENTS.md
  agents.py        # P3 — adaptateurs par agent (lancement, lecture sortie)
  logger.py        # P4 — logs colorés + journal mémoire
config/
  agents.example.yaml   # P2
tests/
  test_brain.py         # P2
  test_context.py       # P3
frontend/               # P4 — dashboard Lovable
.agentrelay/            # créé à l'exécution (ignoré par Git)
  state.json
  task.md
  history.jsonl
.env.example
requirements.txt
```

## Interfaces (à ne pas changer sans prévenir l'équipe)

```python
# brain.py (P2)
def build_system_prompt(config: dict) -> str: ...
def decide_next(state: dict, config: dict) -> dict | None: ...
    # retourne {"agent": "<nom>", "task": "<description>", "reason": "..."}

# context.py (P3)
def init_session(goal: str) -> dict: ...               # crée .agentrelay/*
def load_state() -> dict: ...                          # lit state.json
def save_state(state: dict) -> None: ...
def write_task_for(agent: str, task: str, context: str) -> None: ...
    # écrit AGENTS.md (ou CLAUDE.md) + .agentrelay/task.md
def append_history(entry: dict) -> None: ...           # append à history.jsonl
def read_history(n: int = 20) -> list[dict]: ...

# agents.py (P3)
def list_agents(config: dict) -> list[dict]: ...       # avec statut
def launch(agent: str, config: dict) -> int: ...       # mode auto: subprocess
def mark_done(agent: str, output: str) -> None: ...    # consigne la sortie

# orchestrator.py (P1)
def start(goal: str, config: dict, auto: bool = False) -> dict: ...
def step_next(output: str | None, config: dict) -> dict: ...
def get_status(config: dict) -> dict: ...              # pour le dashboard

# logger.py (P4)
def log(event: str, agent: str = "", detail: str = "") -> None: ...
def recent(n: int = 20) -> list[dict]: ...
```

## Flux d'une session
1. `agentrelay start "build JWT auth"` → `context.init_session(...)`.
2. `orchestrator.start()` appelle `brain.decide_next(state)` → `{agent, task, reason}`.
3. `context.write_task_for(agent, task, state["summary"])` → l'agent cible a sa consigne.
4. Mode manuel : AgentRelay affiche *« Lance claude-code dans ce dossier »* et attend. Mode auto : `agents.launch(agent)`.
5. Quand l'agent a fini : `agentrelay next --output <fichier>` ou automatique → `orchestrator.step_next(output)`.
6. `brain.decide_next` reçoit le nouvel état et répond : prochain agent, ou `{"done": true}`.
7. Boucle jusqu'à terminé.

## Endpoints HTTP (serveur FastAPI, pour le dashboard)
| Méthode | Chemin | Rôle |
|---|---|---|
| GET  | `/api/status` | Session active, agents, dernière décision, historique |
| POST | `/api/start` | Démarre une session `{goal, auto}` |
| POST | `/api/next` | Déclenche la prochaine étape (optionnel : `output`) |
| POST | `/api/takeover/{agent}` | Force manuellement un agent |
| POST | `/api/mode` | Bascule auto / manuel |
| POST | `/api/stop` | Termine la session |

**CORS** : ouvert sur `/api/*` pour que Lovable puisse appeler.

## Le cerveau (brain.py, P2)
- Message système construit dynamiquement avec les `description` des agents de la config.
- Entrée : `state` (objectif, étape courante, dernière sortie tronquée, historique court).
- Sortie imposée : JSON strict `{"agent": "<nom>", "task": "<quoi faire>", "reason": "<pourquoi>"}` ou `{"done": true, "reason": "..."}`.
- `temperature: 0`, `max_tokens` ≈ 200.
- Toute erreur (réseau, JSON invalide, agent inconnu) → `None` et le mode manuel reprend la main.

## Contexte & handoff (context.py, P3)
- `.agentrelay/state.json` : `{goal, created_at, mode, current_agent, steps: [...]}`
- `AGENTS.md` à la racine du projet, régénéré à chaque étape :
  ```
  # Current task (via AgentRelay)
  **Goal:** <objectif global>
  **This step:** <task pour l'agent choisi>
  **What's done:** <résumé des étapes passées>
  **Don't:** recommencer depuis zéro, contredire les décisions précédentes.
  ```
- `history.jsonl` : une ligne par étape (agent, task, output snippet, duration).

## Config attendue (clés obligatoires)
`agents` (liste), `brain` (`provider`, `base_url`, `api_key_env`, `model`, `timeout`, `max_input_chars`), `mode_default` ("manual" | "auto"), `max_steps` (sécurité pour mode auto).

## CLI (click, P1)
```
agentrelay start "<goal>" [--auto]
agentrelay next [--output <file> | --output-text "..."]
agentrelay status
agentrelay stop
agentrelay serve [--port 8000]
```

## Conventions
- Les clés API : jamais dans le code ni le YAML, seulement le **nom** de la variable d'environnement.
- `.agentrelay/` et `AGENTS.md` sont ignorés par Git.
- Fonctions courtes, noms en anglais, commentaires en français acceptés.
