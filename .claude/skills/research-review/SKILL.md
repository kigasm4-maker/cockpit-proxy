---
name: research-review
description: Revue hebdomadaire de veille. Utiliser chaque dimanche (via cron/LaunchAgent avec `claude -p`) ou quand l'utilisateur demande de "faire la revue de veille", "promouvoir les patterns" ou "consolider les learnings". Analyse new_learnings.md et promeut les patterns confirmés vers memory/long-term-memory.md.
---

# Research Review

## Étapes

### 1. Lire new_learnings.md
Charger toutes les entrées entre `<!-- SCOUT:START -->` et `<!-- SCOUT:END -->`.

### 2. Détecter les patterns confirmés
Un pattern est **confirmé** si :
- il apparaît dans **au moins 2 trouvailles indépendantes** (sources/URL différentes), ET
- le score moyen des trouvailles concernées est **≥ 4/5**, ET
- il est toujours d'actualité (pas contredit par une trouvaille plus récente).

Regrouper les trouvailles par thème avant d'évaluer (ex. 3 posts différents disant "les carrousels courts convertissent mieux" = 1 pattern candidat).

### 3. Promouvoir vers long-term-memory.md
Ajouter chaque pattern confirmé dans `memory/long-term-memory.md` entre `<!-- PATTERNS:START -->` et `<!-- PATTERNS:END -->`, format :
`- [YYYY-MM-DD confirmé] pattern en 1 phrase (sources: URL1, URL2)`

Vérifier les doublons avant insertion. Si un pattern déjà présent est contredit par de nouvelles données, le marquer `[obsolète YYYY-MM-DD]` au lieu de le supprimer.

### 4. Nettoyer new_learnings.md
- Supprimer les entrées promues (elles vivent désormais en long terme).
- Supprimer les entrées de score ≤ 2 datant de plus de 14 jours.
- Garder les scores 3-4 récents comme candidats pour la semaine suivante.

### 5. Rapport
5 lignes max : patterns promus, patterns candidats en attente, entrées purgées.

## Règles
- Jamais de promotion sur la base d'une seule source, même score 5.
- Idempotent : deux exécutions le même dimanche ne doublonnent rien.
