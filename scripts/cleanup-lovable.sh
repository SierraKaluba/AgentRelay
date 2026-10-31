#!/usr/bin/env bash
# Nettoie les traces Lovable dans frontend/ (à lancer DEPUIS la racine d'AgentRelay).
# Prérequis : avoir copié le code de token-relay-pulseboard dans frontend/

set -euo pipefail

if [[ ! -d frontend ]]; then
  echo "✗ Lance ce script depuis la racine du repo AgentRelay, et place d'abord le code du pulseboard dans frontend/"
  exit 1
fi

cd frontend

echo "→ Suppression du dossier .lovable/"
rm -rf .lovable

echo "→ Nettoyage de AGENTS.md (bloc LOVABLE)"
if [[ -f AGENTS.md ]]; then
  # Retire le bloc entre <!-- LOVABLE:BEGIN --> et <!-- LOVABLE:END -->
  sed -i '/<!-- LOVABLE:BEGIN -->/,/<!-- LOVABLE:END -->/d' AGENTS.md
  # Si le fichier est maintenant vide ou que du blanc, le supprimer
  [[ -s AGENTS.md ]] || rm -f AGENTS.md
fi

echo "→ Renommage dans package.json : tanstack_start_ts → agentrelay-dashboard"
sed -i 's/"tanstack_start_ts"/"agentrelay-dashboard"/' package.json

echo "→ Retrait de la dépendance @lovable.dev dans package.json (⚠️ nécessite une réécriture de vite.config.ts ensuite)"
# Commenté par défaut car ça casse vite.config.ts si on l'enlève sans refactor.
# Dé-commentez quand vous êtes prêt à réécrire vite.config.ts en Vite + TanStack natif :
# sed -i '/"@lovable.dev\/vite-tanstack-config"/d' package.json

echo "→ Remplacement du README par un README propre"
cat > README.md <<'EOF'
# AgentRelay Dashboard

Dashboard web d'AgentRelay. React + TypeScript + Vite + TailwindCSS.

## Lancer en local

```bash
npm install
npm run dev
```

Le dashboard est servi sur http://localhost:5173 et appelle l'API d'AgentRelay sur http://localhost:8000.

## Variables d'environnement

```
VITE_API_BASE=http://localhost:8000
```

## Build de production

```bash
npm run build
```

Le build est dans `dist/`.

## Structure

```
src/
  components/   # UI
  hooks/        # usePolling, etc.
  lib/          # api.ts (appels backend)
  routes/       # TanStack Router
```

Partie du projet [AgentRelay](https://github.com/SierraKaluba/AgentRelay). MIT.
EOF

echo ""
echo "✓ Nettoyage terminé."
echo ""
echo "⚠️  Points d'attention :"
echo "   - vite.config.ts dépend encore de @lovable.dev/vite-tanstack-config."
echo "     Si vous voulez une indépendance complète, il faut réécrire vite.config.ts"
echo "     avec les plugins Vite + TanStack Start standards."
echo "   - Vérifiez public/favicon.ico : s'il contient un logo Lovable, remplacez-le."
echo "   - Vérifiez src/ pour tout import ou commentaire mentionnant lovable."
echo ""
echo "Pour chercher les mentions restantes :"
echo "   grep -ri 'lovable' . --exclude-dir=node_modules --exclude-dir=.git"
