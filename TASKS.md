# TASKS — AgentRelay

Répartition des tâches pour le hackathon (1 h 30, 4 personnes). Chaque personne travaille sur sa branche. Référence : `SPEC.md`, `PROMPTS.md`.

**Règle d'or** : on ne touche pas aux fichiers d'un autre. Changement d'interface ? On prévient et on met à jour `SPEC.md`.

---

## 🟩 SETUP (collectif, 0:00 – 0:15)

- [ ] Chacun crée sa clé Google AI Studio sur `aistudio.google.com`
- [ ] `git clone` du repo, création des branches : `p1-core`, `p2-brain`, `p3-context`, `p4-frontend`
- [ ] OpenCode configuré avec Gemma sur les 4 machines
- [ ] **P1** lance le Prompt 0 (squelette) et push sur `main`

---

## 🟦 P1 — CLI, orchestrateur, serveur (branche `p1-core`)

- [ ] **P1.1** — Orchestrateur : `start`, `step_next`, `get_status` → `agentrelay/orchestrator.py`
- [ ] **P1.2** — CLI click : `start`, `next`, `status`, `stop`, `serve`, mode `--auto` → `agentrelay/cli.py`
- [ ] **P1.3** — Serveur FastAPI + CORS + tous les endpoints `/api/*` → `agentrelay/server.py`

Prompts prêts à l'emploi : `PROMPTS.md` § P1.

---

## 🟪 P2 — Cerveau Gemma & config (branche `p2-brain`)

- [ ] **P2.1** — Config `config/agents.example.yaml` (3 agents + cerveau Gemma 3 27B)
- [ ] **P2.2** — `build_system_prompt(config)` → `agentrelay/brain.py`
- [ ] **P2.3** — `decide_next(state, config)` + validation JSON stricte → `agentrelay/brain.py`
- [ ] **P2.4** — Tests pytest avec monkeypatch httpx → `tests/test_brain.py`

Prompts prêts à l'emploi : `PROMPTS.md` § P2.

---

## 🟨 P3 — Contexte & agents (branche `p3-context`)

- [ ] **P3.1** — `init_session`, `write_task_for`, `append_history`, `read_history` → `agentrelay/context.py`
- [ ] **P3.2** — `list_agents`, `launch`, `mark_done` → `agentrelay/agents.py`
- [ ] **P3.3** — Tests pytest avec `tmp_path` → `tests/test_context.py`

Prompts prêts à l'emploi : `PROMPTS.md` § P3.

---

## 🟥 P4 — Frontend, logs, doc, démo (branche `p4-frontend`)

- [ ] **P4.1** — Logger coloré + journal mémoire → `agentrelay/logger.py`
- [ ] **P4.2** — Intégrer le dashboard dans `frontend/` : copier le code du pulseboard puis lancer `scripts/cleanup-lovable.sh`
- [ ] **P4.3** — Mettre à jour `README.md` et `docs/DEMO.md` avec les noms de l'équipe et ce qui marche vraiment
- [ ] **P4.4** — Préparer le dossier `demo/` (projet exemple) et répéter la démo 2 fois

Prompts prêts à l'emploi : `PROMPTS.md` § P4.

---

## 🟩 FUSION (collectif, 1:00 – 1:15)

- [ ] Ordre de merge : **P4 → P3 → P2 → P1**
- [ ] `pytest` après chaque merge
- [ ] Lancer `agentrelay serve` + dashboard + ngrok si besoin
- [ ] Dérouler `docs/DEMO.md` deux fois sans erreur
- [ ] Rename final : `tokenrelay` → `agentrelay` (voir `PROMPTS.md` § P4.4)
- [ ] Push final sur `main`

---

## 🚨 En cas de blocage

Prompt de debug prêt à copier dans OpenCode :
```
@SPEC.md Voici l'erreur : <coller>. Fichier : @<fichier>. Corrige
uniquement ce qui est nécessaire, sans changer les interfaces de la SPEC.
```
