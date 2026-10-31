# Contribuer à TokenRelay

Merci de votre intérêt ! Voici comment participer.

## Signaler un problème
Ouvrez une *issue* en précisant : ce que vous avez fait, ce que vous attendiez, ce qui s'est passé, et les logs du terminal (sans vos clés API).

## Proposer une modification
1. Forkez le dépôt et créez une branche : `git checkout -b ma-fonctionnalite`
2. Faites des changements petits et ciblés.
3. Lancez les tests : `pytest`
4. Ouvrez une *pull request* qui explique le pourquoi du changement.

## Conventions
- Python 3.11+, fonctions courtes et lisibles.
- Respectez les interfaces décrites dans `SPEC.md` ; si vous devez les changer, expliquez pourquoi dans la PR.
- Aucune clé API dans le code, la config ou les commits : uniquement des noms de variables d'environnement.

## Ajouter un provider
Si le provider est compatible OpenAI, une entrée dans `config/providers.example.yaml` suffit. Sinon, ajoutez un adaptateur dans `providers.py` et documentez-le dans le README.

## Licence
En contribuant, vous acceptez que votre contribution soit publiée sous la licence MIT du projet.
