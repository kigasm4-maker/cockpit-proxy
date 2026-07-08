---
name: research-scout
description: Scout de veille automatisé. Utiliser ce skill quand l'utilisateur demande une "veille", "les nouveautés", "quoi de neuf dans ma niche", ou quand il est lancé automatiquement 3x/jour via cron/LaunchAgent avec `claude -p`. Cherche sur le web, Reddit, Hacker News et les forums de la niche, puis stocke chaque trouvaille dans new_learnings.md avec URL, date, résumé 1 ligne et score de pertinence 1 à 5.
---

# Research Scout

## Configuration de niche
Lire d'abord la section "Niche" ci-dessous. Si elle est vide, demander à l'utilisateur (ou en mode automatique, utiliser les projets actifs de `memory/project-memory.md` comme niche).

**Niche** : coaching relationnel, monétisation de contenu en ligne, trading retail / certifications AMF, outils IA pour créateurs
**Sources prioritaires** : Reddit (r/Entrepreneur, r/relationships_advice côté tendances, r/Daytrading), Hacker News, blogs spécialisés, X/Twitter via recherche web

## Étapes

### 1. Construire 3 à 5 requêtes de recherche
Croiser la niche avec des mots de fraîcheur : "nouveau", "2026", "cette semaine", noms d'outils récents. Exemples :
- `site:reddit.com coaching en ligne monétisation` (via recherche web)
- `Hacker News AI content tools` — ou directement l'API HN : `https://hn.algolia.com/api/v1/search_by_date?query=<terme>&tags=story`
- Reddit JSON public : `https://www.reddit.com/r/<subreddit>/new.json?limit=25` (User-Agent requis)

### 2. Filtrer
Garder uniquement : moins de 7 jours, en lien direct avec la niche, apport concret (technique, chiffre, outil, retour d'expérience). Écarter le contenu purement promotionnel.

### 3. Scorer la pertinence (1-5)
- 5 : directement actionnable sur un projet actif cette semaine
- 4 : pattern utile, à confirmer
- 3 : bon à savoir, contexte
- 2 : marginal
- 1 : hors sujet (ne pas stocker)

### 4. Stocker dans new_learnings.md
Insérer entre `<!-- SCOUT:START -->` et `<!-- SCOUT:END -->`, une ligne par trouvaille :
`- [YYYY-MM-DD] [score/5] résumé en 1 ligne — <URL>`

Vérifier les doublons par URL (grep) avant insertion. Maximum 10 nouvelles lignes par exécution.

### 5. Rapport
Résumer en 3 lignes : nombre de trouvailles, meilleure trouvaille du jour, source la plus productive.

## Règles
- Toujours inclure l'URL source réelle, jamais reconstruite de mémoire.
- Résumé strictement en 1 ligne, en français.
- Ne jamais dépasser 200 lignes dans new_learnings.md : si dépassé, archiver les plus anciennes dans `new_learnings_archive.md`.
