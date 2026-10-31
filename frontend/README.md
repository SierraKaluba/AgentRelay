# Token Relay Pulseboard

Crée un dashboard web nommé "TokenRelay" avec l'esthétique d'un outil de 

développeur type OpenCode / Vercel / Linear : interface sobre, dense en 

information, monospace partout, thème sombre, animations discrètes.

## Stack technique

- React + Vite + TypeScript

- TailwindCSS pour le style

- lucide-react pour les icônes

- Police : JetBrains Mono (via Google Fonts) partout, aucune autre police

- Pas de bibliothèque de composants type shadcn, tout construit à la main 

  pour garder le contrôle du style

## Palette (fond sombre, pas noir pur)

- Fond principal : #0a0a0a

- Fond cartes : #141414

- Bordures : #262626

- Texte principal : #e5e5e5

- Texte secondaire : #737373

- Vert accent (actif, OK) : #4ade80

- Rouge (limited, ERROR) : #f87171

- Jaune (fallback, rules) : #facc15

- Violet (brain) : #c084fc

- Bleu (route, call) : #60a5fa

- Cyan (handoff) : #22d3ee

## Mise en page (une seule page, pas de routing)

### Barre supérieure (hauteur 56px, bordure basse)

À gauche : logo texte "> tokenrelay" en vert accent, suivi en texte 

secondaire de "v0.1.0 · hackathon build".

À droite : un petit indicateur rond vert + texte "connected" (plus

This project was built with [Lovable](https://lovable.dev).

## Build with Lovable

Continue developing this project in the [Lovable editor](https://lovable.dev/projects/6355864b-f0c6-4a63-ae27-0755df9b9c9f).

- **Ship faster**: describe what you want to build and Lovable handles the code.
- **Stay in sync**: every change made in Lovable is committed straight to this repository.
- **Full ownership**: this code is yours. Push to `main` on GitHub and your changes sync back into Lovable, ready for your next prompt.

## Development

Prefer working locally? You need Node.js and npm — [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating).

```sh
git clone <this-repository-url>
cd <repository-name>
npm i
npm run dev
```
