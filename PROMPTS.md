# Prompts — AgentRelay

Chacun code avec **Gemma dans OpenCode**. Avant chaque prompt : `@SPEC.md`.
Un prompt = une tâche courte. Testez entre deux prompts.

---

## Prompt 0 — Squelette (P1, à 0:10)

```
@SPEC.md Crée le squelette du projet selon « Arborescence » : tous les
dossiers et fichiers Python avec seulement les signatures de « Interfaces »
et un `raise NotImplementedError` dans chaque fonction. Crée aussi
requirements.txt (dépendances de la SPEC), un .gitignore (.env,
config/agents.yaml, .agentrelay/, AGENTS.md, CLAUDE.md, .venv, __pycache__,
frontend/node_modules, frontend/dist) et un .env.example avec GEMMA_API_KEY
vide. N'implémente aucune logique.
```
→ Commit, push, les autres font `git pull` et créent leur branche.

---

## P1 — CLI, orchestrateur, serveur (branche `p1-core`)

**P1.1 — Orchestrateur**
```
@SPEC.md Implémente agentrelay/orchestrator.py selon « Flux d'une session » et
« Interfaces » : start initialise le contexte, demande au cerveau la première
décision et écrit la tâche pour l'agent choisi. step_next consigne la sortie,
réinterroge le cerveau, écrit la nouvelle tâche. get_status renvoie tout ce
qu'il faut au dashboard. Si le cerveau retourne None, bascule en mode manuel
(état attend_user_choice=True) et logue. Si decide_next retourne {done:true},
termine la session.
```

**P1.2 — CLI**
```
@SPEC.md Implémente agentrelay/cli.py avec click selon la section « CLI » :
start, next, status, stop, serve. start accepte --auto. next accepte --output
(fichier) ou --output-text. En mode auto, start enchaîne step_next en boucle
jusqu'à done ou max_steps. Affiche à chaque étape : agent choisi, raison,
chemin du contexte écrit, instruction utilisateur si manuel.
```

**P1.3 — Serveur**
```
@SPEC.md Implémente agentrelay/server.py : FastAPI avec CORS ouvert sur
/api/*, tous les endpoints de la section « Endpoints HTTP ». GET /api/status
renvoie orchestrator.get_status + logger.recent(20). POST /api/next peut
recevoir un output optionnel dans le body JSON. POST /api/takeover/{agent}
force cet agent pour la prochaine étape (court-circuite le cerveau une fois).
POST /api/mode change le mode (auto/manual).
```

---

## P2 — Cerveau & config (branche `p2-brain`)

**P2.1 — Config**
```
@SPEC.md Crée config/agents.example.yaml. Section agents : 3 entrées
claude-code, codex, opencode, chacune avec name, description (3 lignes sur ses
forces : raisonnement/code dense/multi-provider), launch_cmd (ex. "claude",
"codex", "opencode"), context_file ("CLAUDE.md", "AGENTS.md", "AGENTS.md").
Section brain : provider gemma, base_url
https://generativelanguage.googleapis.com/v1beta/openai, api_key_env
GEMMA_API_KEY, model gemma-3-27b-it, timeout 10, max_input_chars 3000.
mode_default: manual. max_steps: 10. Commente en français.
```

**P2.2 — Prompt système du cerveau**
```
@SPEC.md Rédige build_system_prompt(config) dans brain.py. Il décrit au
cerveau son rôle d'orchestrateur, liste les agents disponibles avec leur
description, et impose une réponse JSON stricte :
{"agent": "<nom>", "task": "<à faire>", "reason": "<pourquoi>"}
ou {"done": true, "reason": "..."}.
Inclus 2 exemples : (1) nouvelle tâche d'architecture → claude-code ; (2) le
plan est fait, il faut implémenter → opencode.
```

**P2.3 — Décision**
```
@SPEC.md Implémente brain.decide_next(state, config). Construit un prompt
utilisateur résumant : goal, étape actuelle, dernière sortie tronquée à
max_input_chars, 3 dernières étapes de l'historique. Appelle le provider via
httpx (POST base_url/chat/completions). Extrait le JSON (même entouré de
```json). Valide : agent existe dans la config, ou done:true. Toute erreur →
None. Logue BRAIN avec la décision ou l'échec.
```

**P2.4 — Tests**
```
@SPEC.md Écris tests/test_brain.py avec pytest en monkeypatchant httpx :
JSON valide → décision correcte ; {done:true} accepté ; agent inconnu → None ;
texte non JSON → None ; HTTPError → None. Config écrite dans les tests.
```

---

## P3 — Contexte & agents (branche `p3-context`)

**P3.1 — Context**
```
@SPEC.md Implémente agentrelay/context.py selon « Contexte & handoff ».
init_session crée .agentrelay/ avec state.json (goal, created_at, mode,
steps vide), task.md vide, history.jsonl vide. write_task_for(agent, task,
summary) écrit à la fois .agentrelay/task.md ET le context_file de l'agent
(CLAUDE.md ou AGENTS.md) au format spécifié dans la SPEC. append_history
ajoute une ligne JSON à history.jsonl. read_history relit les n dernières.
```

**P3.2 — Agents**
```
@SPEC.md Implémente agentrelay/agents.py. list_agents(config) retourne chaque
agent avec status: "active" (celui du state.current_agent), "idle" (les
autres), "exhausted" si marqué dans state. launch(agent, config) lance
subprocess.Popen(launch_cmd, cwd=".") pour le mode auto, et retourne le
code de retour. mark_done consigne la sortie dans history.
```

**P3.3 — Tests**
```
@SPEC.md Écris tests/test_context.py avec pytest et tmp_path (change de
répertoire pour les tests, ne touche pas au vrai .agentrelay/) : init_session
crée les 3 fichiers avec les bons contenus, write_task_for écrit AGENTS.md ET
task.md avec le format de la SPEC, append_history ajoute bien une ligne JSON
par appel, read_history renvoie dans l'ordre inverse.
```

---

## P4 — Frontend, logs, doc, démo (branche `p4-integration`)

**P4.1 — Logger**
```
@SPEC.md Implémente agentrelay/logger.py : log affiche une ligne colorée
(heure, événement entre crochets, agent en majuscules, détail) et stocke dans
une liste mémoire limitée à 100. recent(n) retourne les n derniers. Couleurs
ANSI : BRAIN magenta gras, HANDOFF cyan, LAUNCH bleu, DONE vert, QUOTA jaune,
CHECKPOINT violet, ERROR rouge gras.
```

**P4.2 — Frontend Lovable**
Lovable est déjà commencé. Mettre à jour avec le prompt que je t'ai donné séparément (changement de domaine : outils de dev, pas providers d'IA). Puis l'exporter dans `frontend/`.

**P4.3 — Doc**
```
@SPEC.md Mets à jour README.md et docs/DEMO.md pour qu'ils correspondent à
ce qui marche réellement, ajoute les noms de l'équipe, et vérifie que les
exemples de commandes CLI sont corrects.
```

**P4.4 — Rename final (après fusion)**
```
@SPEC.md Fais un find-and-replace global : "TokenRelay" → "AgentRelay",
"tokenrelay" → "agentrelay", "token-relay" → "agent-relay",
"tokenrelay-auto" → "agentrelay-auto". Lance pytest, puis commit :
"rename: TokenRelay → AgentRelay".
```

---

## Fusion (1:00 – 1:15)

1. Ordre : **P4 (logger) → P3 (context + agents) → P2 (brain) → P1 (orchestrator + CLI + server)**.
2. Après chaque merge : `pytest`.
3. Démarrer le serveur : `agentrelay serve --port 8000`.
4. Dans un autre terminal : `ngrok http 8000` et mettre l'URL dans le frontend.
5. Dérouler `docs/DEMO.md` deux fois.

**Prompt de debug (si bug d'intégration)**
```
@SPEC.md Voici l'erreur : <coller>. Fichier : @<fichier>. Corrige uniquement
ce qui est nécessaire, sans changer les interfaces de la SPEC.
```
