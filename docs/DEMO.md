# Script de démo — AgentRelay (≈ 2 min 30)

## Préparation
- Terminal 1 : `agentrelay serve --port 8000`.
- Terminal 2 : `cd frontend && npm run dev` → ouvrir `http://localhost:5173`.
- Terminal 3 : prêt à taper les commandes `agentrelay`.
- Dossier `demo/` : un petit projet Python avec `app.py` vide, dans lequel on va ajouter l'auth JWT.
- Reset : `agentrelay stop && rm -rf .agentrelay AGENTS.md CLAUDE.md`.

## Le problème (20 s)
> « Vous codez avec Claude Code et son quota tombe en pleine tâche. Vous ouvrez Codex ou OpenCode mais il ne sait rien de ce qui a été fait. Vous devez tout réexpliquer. »

## Étape 1 — Démarrer (20 s)
```
agentrelay start "ajouter l'authentification JWT à cette API"
```
→ Dashboard : la session apparaît. Journal : `[BRAIN] gemma décide → claude-code (architecture)`.
Le fichier `CLAUDE.md` est écrit avec la tâche.
> « Gemma a choisi Claude Code pour commencer parce que c'est une tâche d'architecture. »

## Étape 2 — Première exécution (30 s)
*(On simule que Claude Code a fait son travail.)*
```
agentrelay next --output-text "créé le plan : 3 endpoints /login /refresh /verify, middleware JWT, variable JWT_SECRET"
```
→ Dashboard : étape 1 cochée. Journal : `[BRAIN] → opencode (implémentation)`. `AGENTS.md` mis à jour.
> « Le travail de Claude Code est consigné. Gemma passe la main à OpenCode pour implémenter. »

## Étape 3 — La bascule inattendue (30 s)
Cliquer dans le dashboard sur **« Mark exhausted »** sur OpenCode.
```
agentrelay next --output-text "quota opencode atteint"
```
→ Journal : `[QUOTA] OPENCODE exhausted` puis `[BRAIN] → codex (fallback)`.
> « OpenCode a sa limite ? Gemma redirige vers Codex, qui reçoit tout le contexte du travail. »

## Étape 4 — Mode auto (30 s)
```
agentrelay start "écris les tests unitaires" --auto
```
→ Dashboard : les étapes s'enchaînent toutes seules. Chaque agent est marqué actif à son tour. Le journal défile.
> « En mode auto, on laisse Gemma orchestrer. »

## Conclusion (15 s)
> « AgentRelay transforme vos agents de dev en une équipe coordonnée par Gemma. Open source, MIT, ajouter un nouvel agent = 4 lignes de YAML. »

## Plan B
Vidéo de la démo enregistrée la veille.
