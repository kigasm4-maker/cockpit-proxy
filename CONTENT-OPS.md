# Content Ops — mémoire, veille, quality gates, sujets

Ce dossier n'a aucun lien fonctionnel avec `worker.js` (le proxy Cloudflare
de ce repo) : c'est un système autonome de production de contenu pour la
niche **coaching relationnel**, installé ici à la demande explicite de
l'utilisateur (session cloud dédiée).

## Contenu

```
memory/
├── recent-memory.md        # contexte glissant 48h
├── long-term-memory.md     # préférences confirmées + patterns validés
└── project-memory.md       # état actif des projets + journal de contenu
.claude/skills/
├── consolidate-memory/      # consolidation nocturne des logs ~/.claude
├── research-scout/          # veille web/Reddit/HN → new_learnings.md
└── research-review/         # promotion des patterns le dimanche
scripts/
├── quality_gate.py          # gate 1 : densité, mots vagues, phrases, placeholders (min 60/100)
├── fingerprint_check.py     # gate 2 : 24 formulations robot interdites (min 55/100)
├── auto_source.py           # sélecteur de sujets (pick / mark-used)
└── publish.sh               # pipeline : rien ne sort sans passer les 2 gates
data/
├── subject-bank.json        # 52 sujets — niche "coaching relationnel"
└── anti-repetition.json     # cooldowns : pilier 4j, CTA 2j, sujet 30j
new_learnings.md              # trouvailles de la veille (research-scout)
```

## Utilisation

```bash
# Choisir le sujet du jour (top 5)
python3 scripts/auto_source.py pick

# Écrire le contenu, puis le passer au pipeline (bloquant sur les 2 gates)
./scripts/publish.sh brouillon.md

# Une fois publié, mettre à jour le tracking (anti-repetition.json,
# subject-bank.json, memory/project-memory.md en un seul appel)
python3 scripts/auto_source.py mark-used S001
```

Aucune dépendance externe : Python 3 stdlib uniquement.

## Planification automatique — IMPORTANT

Cette session tourne dans un **container cloud éphémère** rattaché à ce
repo GitHub, pas sur votre machine locale. Deux conséquences :

1. **`~/.claude` ici ≠ votre historique Claude Code local.** Le skill
   `consolidate-memory` ne peut consolider que l'activité des sessions qui
   tournent *dans cet environnement cloud*. Si vous utilisez aussi Claude
   Code en local, ces logs-là ne sont pas visibles d'ici : pour les
   consolider, il faut soit copier ce dossier sur votre machine et lancer
   `consolidate-memory` localement (cron/LaunchAgent, voir plus bas), soit
   accepter que la version cloud ne consolide que le travail fait sur ce repo.
2. **cron / LaunchAgent locaux ne peuvent pas exister dans ce container**
   (il est détruit après inactivité). La planification réelle mise en place
   ici utilise donc des **Routines Claude Code Remote** (`create_trigger`),
   qui réveillent cette session cloud aux horaires prévus et lui font
   exécuter le skill demandé, puis commit/push le résultat sur la branche
   `claude/memory-content-automation-vqmikg`.

Routines créées (toutes en UTC) :

| Nom | Cron (UTC) | Action |
|---|---|---|
| `consolidate-memory-nightly` | `30 2 * * *` | Skill consolidate-memory + commit/push |
| `research-scout-3x` | `0 7,13,19 * * *` | Skill research-scout + commit/push |
| `research-review-weekly` | `0 18 * * 0` (dimanche) | Skill research-review + commit/push |

Pour les gérer : demander à Claude "liste/modifie/désactive les routines
content-ops" dans une session de ce compte.

### Alternative locale (si vous préférez cron/LaunchAgent sur votre Mac/serveur)

```cron
30 2 * * *   cd /chemin/vers/ce/repo && claude -p "Utilise le skill consolidate-memory." --allowedTools "Bash,Read,Write,Edit" >> logs/consolidate.log 2>&1
0 7,13,19 * * *  cd /chemin/vers/ce/repo && claude -p "Utilise le skill research-scout." --allowedTools "Bash,Read,Write,Edit,WebSearch,WebFetch" >> logs/scout.log 2>&1
0 18 * * 0   cd /chemin/vers/ce/repo && claude -p "Utilise le skill research-review." --allowedTools "Bash,Read,Write,Edit" >> logs/review.log 2>&1
```

## Notes

- Les gates sont volontairement stricts. Si un texte légitime est bloqué,
  ajuster les seuils en tête de `scripts/quality_gate.py`
  (`SEUIL_PUBLICATION`, `DENSITE_MIN`) et `scripts/fingerprint_check.py`
  (`SEUIL`), ou retirer des mots des listes.
- `auto_source.py mark-used` mutualise les 3 fichiers de tracking :
  `data/anti-repetition.json` (historique), `data/subject-bank.json`
  (last_used, compteur) et `memory/project-memory.md` (journal de contenu).
- `research-scout` s'appuie sur `WebSearch`/`WebFetch` : vérifié
  fonctionnel dans cet environnement au moment de l'installation.
