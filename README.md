# AgentRelay

**MVP : orchestrez Claude Code, Codex et OpenCode en préservant le contexte de travail.**

Vous codez avec Claude Code et vous atteignez la limite ? Vous aimeriez enchaîner une tâche avec Codex puis OpenCode selon leurs forces ? AgentRelay s'occupe de tout :

- **Gemma, le cerveau**, décide quel agent est le mieux placé pour chaque étape.
- **Le contexte est préservé** : chaque agent reçoit un `AGENTS.md` (ou `CLAUDE.md`) qui résume ce qui a été fait et ce qui reste.
- **Mode manuel ou auto** : vous confirmez chaque bascule, ou vous laissez AgentRelay enchaîner tout seul.
- **Universel** : ajouter un nouvel agent (Aider, Cline…) = 4 lignes de YAML.
- **Dashboard web** pour visualiser qui travaille, quand il passe la main, et pourquoi.

```
                   ┌──────────────┐
                   │ Gemma (brain)│  « cette étape → opencode »
                   └──────▲───────┘
                          │
     ┌──────────► AgentRelay ◄──────────┐
     │             │  ▲                 │
     │             │  │ AGENTS.md       │
     ▼             ▼  │                 ▼
 Claude Code    Codex │             OpenCode
                      └─ Dashboard (React, Lovable)
```

> Projet réalisé en 1 h 30 lors d'un hackathon. MVP simple, lisible, extensible.

---

## Fonctionnalités

| Fonctionnalité | Statut |
|---|---|
| Orchestration multi-agents et handoff par fichiers | MVP |
| Décision Gemma avec repli manuel si indisponible | MVP |
| CLI et API FastAPI | MVP |
| Dashboard local | MVP |
| Mode automatique via commandes configurées | Expérimental |

## Installation

Prérequis : Python 3.11+ ; un agent installé uniquement pour le mode auto.

```bash
git clone https://github.com/<votre-equipe>/agentrelay.git
cd agentrelay
python -m venv .venv
```

Windows PowerShell :
```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
Copy-Item config/agents.example.yaml config/agents.yaml
```

macOS/Linux :
```bash
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
cp config/agents.example.yaml config/agents.yaml
```

## Configuration

```bash
 # Ouvrez .env et renseignez GEMMA_API_KEY avec votre clé Google AI Studio.
```

Ouvrez `.env` et renseignez `GEMMA_API_KEY=votre_nouvelle_cle`. Le fichier `.env`
reste local et ne doit jamais être ajouté à Git. La clé partagée précédemment
dans le chat doit être révoquée avant d'utiliser une nouvelle clé.

Chaque agent est défini par :
```yaml
agents:
  claude-code:
    description: Fort pour l'architecture et le raisonnement
    launch_cmd: claude
    context_file: CLAUDE.md
```

## Utilisation (CLI)

```bash
# Démarrer une session
agentrelay start "ajouter l'authentification JWT à mon API"

# Mode auto : enchaîne les agents sans intervention
agentrelay start "..." --auto

# Après qu'un agent a fini
agentrelay next --output-text "voici ce que j'ai fait..."

# Voir où on en est
agentrelay status

# Lancer le serveur et le dashboard sur http://127.0.0.1:8000
agentrelay serve --port 8000
```

## Dashboard

Le dashboard est servi directement par le serveur à `http://127.0.0.1:8000`.
L’API est disponible sous `/api/` et sa documentation interactive à `/docs`.

## Comment ça marche

1. `agentrelay start "..."` crée `.agentrelay/state.json` et un `AGENTS.md`.
2. Le **cerveau (Gemma)** reçoit l'objectif et l'historique, et décide : `{agent, task, reason}`.
3. AgentRelay écrit la tâche dans le `context_file` de l'agent choisi.
4. Vous lancez l'agent (ou AgentRelay le fait en mode auto). Il lit son contexte et travaille.
5. `agentrelay next` : la sortie est consignée, Gemma décide la suite.
6. Boucle jusqu'à `{done: true}`.

## Structure

```
agentrelay/
  cli.py           # commandes CLI
  orchestrator.py  # coordination
  server.py        # FastAPI pour le dashboard
  brain.py         # Gemma décide
  context.py       # état & handoff
  agents.py        # adaptateurs par agent
  logger.py        # logs colorés
frontend/          # dashboard autonome
config/            # agents.yaml
tests/             # pytest
```

## Limites actuelles

- En mode manuel, l’utilisateur lance l’agent et fournit son résultat à `agentrelay next`.
- Le mode auto exécute la commande configurée de façon bloquante ; détection de fin via code retour.
- L’API est prévue pour un usage local. Ne l’exposez pas sur un réseau public sans authentification.

## Contribuer

Voir [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Équipe

- Prénom Nom — CLI, orchestrateur, serveur
- Prénom Nom — cerveau Gemma
- Prénom Nom — contexte & agents
- Prénom Nom — frontend, logs, doc, démo

## Licence

MIT. Voir [`LICENSE`](LICENSE).
