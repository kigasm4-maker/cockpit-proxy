---
name: consolidate-memory
description: Consolide la mémoire persistante du projet. Utiliser ce skill chaque nuit (via cron/LaunchAgent avec `claude -p`) ou dès que l'utilisateur demande de "consolider la mémoire", "mettre à jour la mémoire", "faire le point sur les dernières 24h" ou mentionne recent-memory, long-term-memory ou project-memory. Lit les logs des 24 dernières heures, extrait les décisions clés et met à jour les 3 fichiers du dossier memory/.
---

# Consolidate Memory

## Objectif
Transformer les conversations brutes des dernières 24h en mémoire structurée dans 3 fichiers :
- `memory/recent-memory.md` — contexte glissant 48h
- `memory/long-term-memory.md` — préférences confirmées
- `memory/project-memory.md` — état actif des projets

## Étapes

### 1. Lire les logs des 24 dernières heures
Les transcripts Claude Code sont dans `~/.claude/projects/<projet>/*.jsonl`.

```bash
find ~/.claude/projects -name "*.jsonl" -mtime -1
```

Pour chaque fichier trouvé, extraire uniquement les messages user et assistant (ignorer les tool_use/tool_result volumineux) :

```bash
cat <fichier> | python3 -c "
import json,sys
for line in sys.stdin:
    try:
        d=json.loads(line)
        m=d.get('message',{})
        if d.get('type') in ('user','assistant'):
            c=m.get('content')
            if isinstance(c,str): print(d['type'].upper()+':',c[:500])
            elif isinstance(c,list):
                for b in c:
                    if b.get('type')=='text': print(d['type'].upper()+':',b['text'][:500])
    except: pass
"
```

Si `~/.claude/projects` est vide ou absent, le signaler et s'arrêter proprement (ne rien inventer).

### 2. Extraire les éléments clés
Pour chaque conversation, identifier :
- **Décisions** : choix explicites ("on part sur X", "abandonne Y", validation d'un livrable)
- **Préférences** : formulations récurrentes sur le style, format, outils, ton
- **Faits nouveaux** : informations stables (contacts, contraintes, deadlines)
- **État projet** : avancement, blocage, prochaine étape mentionnée

Ignorer : le small talk, les tentatives abandonnées, les détails d'implémentation transitoires.

### 3. Mettre à jour recent-memory.md
Insérer les nouvelles entrées entre `<!-- CONSOLIDATE:START -->` et `<!-- CONSOLIDATE:END -->`, format :
`- [YYYY-MM-DD HH:MM] [type] — description (source: nom du projet)`

Puis **supprimer toute entrée datée de plus de 48h**. Avant suppression, vérifier si l'entrée mérite promotion (étape 4).

### 4. Promouvoir vers long-term-memory.md
Une préférence est promue si elle apparaît dans recent-memory **au moins 2 fois** (dates différentes) ou si l'utilisateur l'a confirmée explicitement ("toujours faire comme ça", "retiens que..."). Ajouter dans la section appropriée, une ligne par préférence, sans doublon (vérifier avec grep avant d'ajouter).

### 5. Mettre à jour project-memory.md
Pour chaque projet mentionné dans les logs : mettre à jour son bloc existant (Statut, Dernière action, Prochaine étape, Blocages) ou créer un nouveau bloc entre `<!-- PROJECTS:START/END -->`. Ne jamais supprimer un bloc projet — passer le statut à "en pause" si aucune activité depuis 14 jours.

### 6. Rapport
Terminer par un résumé de 5 lignes max : nombre d'entrées ajoutées, promues, expirées, projets mis à jour.

## Règles
- Ne jamais inventer une décision absente des logs.
- En cas de contradiction entre deux logs, garder la version la plus récente et noter l'ancienne comme obsolète.
- Écriture idempotente : relancer le skill deux fois de suite ne doit pas dupliquer d'entrées.
