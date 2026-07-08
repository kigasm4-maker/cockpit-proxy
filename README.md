# cockpit-proxy

## Worker proxy

`worker.js` est un reverse proxy Cloudflare Worker en lecture seule pour un
petit ensemble d'API externes autorisées (`api.twelvedata.com`,
`api.coingecko.com`, `api.frankfurter.app`, `gamma-api.polymarket.com`),
avec cache 10s et injection de clé API pour Twelve Data. Déploiement via
`wrangler.toml`.

## Pack automatisation Claude Code — mémoire, veille, quality gates, sujets

### Contenu

```
.
├── memory/
│   ├── recent-memory.md        # contexte glissant 48h
│   ├── long-term-memory.md     # préférences confirmées
│   └── project-memory.md       # état actif des projets
├── skills/
│   ├── consolidate-memory/     # consolidation nocturne des logs ~/.claude
│   ├── research-scout/         # veille web/Reddit/HN → new_learnings.md
│   └── research-review/        # promotion des patterns le dimanche
├── scripts/
│   ├── quality_gate.py         # gate n°1 : densité, mots vagues, phrases, placeholders (min 60/100)
│   ├── fingerprint_check.py    # gate n°2 : 24 formulations robot interdites (min 55/100)
│   ├── auto_source.py          # sélecteur de sujets (pick / mark-used)
│   └── publish.sh              # pipeline : rien ne sort sans passer les 2 gates
├── data/
│   ├── subject-bank.json       # sujets tagués pilier/difficulté/CTA
│   └── anti-repetition.json    # cooldowns : pilier 4j, CTA 2j, sujet 30j
└── new_learnings.md            # trouvailles de la veille
```

### Installation (sur votre machine, dans Claude Code)

1. Cloner ce dépôt.
2. Copier les skills dans le dossier de skills de Claude Code :
   ```bash
   cp -r skills/consolidate-memory skills/research-scout skills/research-review ~/.claude/skills/
   ```
3. Vérifier Python 3 : `python3 --version` (aucune dépendance externe requise).
4. Personnaliser la section « Niche » dans `skills/research-scout/SKILL.md`
   et les sujets de `data/subject-bank.json`.

### Utilisation quotidienne

```bash
# Choisir le sujet du jour
python3 scripts/auto_source.py pick

# Écrire le contenu, puis le passer au pipeline
./scripts/publish.sh brouillon.md

# Une fois publié, mettre à jour le tracking (3 fichiers)
python3 scripts/auto_source.py mark-used S024
```

### Planification automatique

Les tâches planifiées s'exécutent sur **votre machine** (Claude Code + cron
ou LaunchAgent), pas dans un environnement Claude Code éphémère. Adapter
`/chemin/vers/cockpit-proxy` partout ci-dessous à votre clone local.

#### Linux / serveur — crontab (`crontab -e`)

```cron
# Consolidation mémoire chaque nuit à 02h30
30 2 * * * cd /chemin/vers/cockpit-proxy && claude -p "Utilise le skill consolidate-memory et exécute la consolidation complète." --allowedTools "Bash,Read,Write,Edit" >> logs/consolidate.log 2>&1

# Research scout 3x par jour (07h, 13h, 19h)
0 7,13,19 * * * cd /chemin/vers/cockpit-proxy && claude -p "Utilise le skill research-scout et lance une session de veille." --allowedTools "Bash,Read,Write,Edit,WebSearch,WebFetch" >> logs/scout.log 2>&1

# Research review chaque dimanche à 18h
0 18 * * 0 cd /chemin/vers/cockpit-proxy && claude -p "Utilise le skill research-review et fais la revue hebdomadaire." --allowedTools "Bash,Read,Write,Edit" >> logs/review.log 2>&1
```

Créer le dossier de logs : `mkdir -p /chemin/vers/cockpit-proxy/logs`

#### macOS — LaunchAgent (exemple pour research-scout)

Fichier `~/Library/LaunchAgents/com.claude.research-scout.plist` :

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
 "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.claude.research-scout</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/zsh</string><string>-lc</string>
    <string>cd /chemin/vers/cockpit-proxy && claude -p "Utilise le skill research-scout et lance une session de veille." --allowedTools "Bash,Read,Write,Edit,WebSearch,WebFetch" >> logs/scout.log 2>&1</string>
  </array>
  <key>StartCalendarInterval</key>
  <array>
    <dict><key>Hour</key><integer>7</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Hour</key><integer>13</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Hour</key><integer>19</integer><key>Minute</key><integer>0</integer></dict>
  </array>
</dict>
</plist>
```

Activer : `launchctl load ~/Library/LaunchAgents/com.claude.research-scout.plist`
Dupliquer le fichier pour consolidate-memory (02h30, quotidien) et
research-review (dimanche 18h, ajouter `<key>Weekday</key><integer>0</integer>`).

### Notes importantes

- `claude -p` en mode automatique consomme votre quota : 3 sessions de veille
  par jour + 1 consolidation, c'est ~120 exécutions/mois. Commencer par 1x/jour
  et augmenter si la valeur est là.
- Les gates sont volontairement stricts. Si un texte légitime est bloqué,
  ajuster les seuils en tête de `quality_gate.py` (SEUIL_PUBLICATION, DENSITE_MIN)
  et `fingerprint_check.py` (SEUIL), ou retirer des mots des listes.
- `auto_source.py mark-used` met à jour les 3 fichiers de tracking :
  anti-repetition.json (historique), subject-bank.json (last_used, compteur)
  et memory/project-memory.md (journal de contenu).
- Le cron/LaunchAgent doit tourner sur une machine persistante à vous : un
  environnement Claude Code éphémère (comme celui-ci) est reconstruit à
  chaque session et ne conserve pas de crontab entre deux sessions.
