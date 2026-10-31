# Plan — AgentRelay (1 h 30, 4 personnes)

**Objectif démo** : montrer qu'on peut travailler sur une tâche en passant de Claude Code à Codex à OpenCode sans jamais perdre le contexte, grâce à Gemma qui orchestre.

## Les IA utilisées
- **Pour coder le projet** : chacun avec **Gemma dans OpenCode**, sa clé Google AI Studio.
- **Dans le projet (cerveau)** : **Gemma** décide à chaque étape quel agent prend la suite.
- **Pour le dashboard** : **Lovable** (déjà commencé).
- Le programme reste **universel** : la config supporte n'importe quel autre agent (Aider, Cline…) en ajoutant une entrée YAML.

## Répartition

| Personne | Rôle | Fichiers |
|---|---|---|
| **P1** | CLI, orchestrateur, serveur | `cli.py`, `orchestrator.py`, `server.py`, `requirements.txt`, `.env.example`, `.gitignore` |
| **P2** | Cerveau Gemma & config | `brain.py`, `config/agents.example.yaml`, `tests/test_brain.py` |
| **P3** | Contexte & adaptateurs d'agents | `context.py`, `agents.py`, `tests/test_context.py` |
| **P4** | Frontend (déjà en cours), logs, doc, démo | `logger.py`, `frontend/` (via Lovable), `README.md`, `docs/DEMO.md` |

**Règle d'or** : on ne touche pas aux fichiers d'un autre. Interface à changer ? On prévient et on met à jour `SPEC.md`.

## Déroulé 1 h 30

| Horaire | Quoi | Qui |
|---|---|---|
| 0:00 – 0:10 | Clés Gemma + repo cloné + OpenCode configuré + Lovable sur un nouvel écran | Tous (P4 continue Lovable) |
| 0:10 – 0:15 | Prompt 0 : squelette | P1 |
| 0:15 – 1:00 | Code en parallèle | Chacun |
| 1:00 – 1:15 | Fusion + test du scénario de démo | P1 + P4 |
| 1:15 – 1:25 | Répétition démo, README final | Tous |
| 1:25 – 1:30 | Marge | — |

## À faire AVANT
- [ ] Clé Google AI Studio pour chaque personne (`aistudio.google.com`).
- [ ] OpenCode installé.
- [ ] Repo GitHub avec les docs actuels.
- [ ] ngrok installé pour exposer `localhost:8000` au frontend Lovable.
- [ ] Préparer un petit dossier `demo/` avec un fichier simple (ex. un `app.py` à modifier) pour la démo : les 3 agents y touchent chacun à leur tour.

Les prompts prêts à copier sont dans [`PROMPTS.md`](PROMPTS.md).
