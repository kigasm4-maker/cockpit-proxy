# Mémoire long terme (préférences confirmées)
> Une préférence n'entre ici que si elle a été observée au moins 2 fois ou confirmée explicitement. Promue par consolidate-memory ou research-review.

## Style & communication
- Langue de travail : français, typographie française correcte (accents, ponctuation)
- Signature des courriers : « Cordialement » + nom, rien d'autre
- Documents par destinataire : un PDF individuel par entreprise

## Préférences techniques
- [2026-07-08 confirmé] Utilisateur exclusivement sur iPad, pas d'ordinateur : toute exécution de script (auto_source.py, quality_gate.py, fingerprint_check.py, publish.sh) doit se faire via une session Claude Code (Bash tool), jamais via installation locale/cron/LaunchAgent
- [2026-07-08 confirmé] Automatisation content-ops (consolidate-memory, research-scout, research-review) planifiée via Routines Claude Code Remote (cloud), pas cron/LaunchAgent local — repo cockpit-proxy, branche claude/memory-content-automation-vqmikg
- [2026-07-09 observé 3x] WebFetch retourne systématiquement 403 dans cet environnement (blogs FR testés + API HN Algolia) : research-scout doit s'appuyer uniquement sur WebSearch, ne pas retenter WebFetch sur ces domaines sans raison

## Patterns confirmés (issus de research-review)
<!-- PATTERNS:START -->
- [2026-07-12 confirmé] Sur les applis de rencontre, un premier message qui mentionne un détail précis du profil (plutôt qu'une formule générique type « salut ça va ») augmente nettement les chances de réponse (sources: https://loveshortcut.fr/guides-pratiques/10-premiers-messages-qui-fonctionnent-sur-les-applis-de-rencontre-et-pourquoi/, https://www.datingland.fr/exemple-de-message-pour-site-de-rencontre.html)
- [2026-07-12 confirmé] Après une rupture, pratiquer l'auto-compassion plutôt que l'auto-critique accélère et améliore la récupération psychologique (sources: https://www.la-clinique-e-sante.com/blog/traumatismes/developper-resilience-cles, https://www.esantementale.ca/Yukon/Lauto-compassion-plus-importante-que-lestime-de-soi-et-peut-tre-la-cle-de-la-sante-mentale/index.php?m=article&ID=52807)
- [2026-07-12 confirmé] Un rituel régulier sans écran (hebdomadaire ou quotidien, même court) renforce mesurablement la complicité et la satisfaction dans un couple de longue durée (sources: https://www.coupletherapie59.fr/blog/articles/routine-dans-le-couple-5-cles-pour-retrouver-de-la-complicite, https://www.medisite.fr/couple-couple-3-rituels-quotidiens-pour-retrouver-une-complicite-amoureuse.5717518.40877.html)
- [2026-07-29 confirmé] Après une dispute intense, une pause d'au moins 20 minutes (signal convenu à l'avance) est nécessaire pour laisser le système nerveux sortir du mode survie avant de reprendre la discussion ; ce n'est pas la fréquence des disputes mais la capacité à « réparer » ensuite qui prédit la solidité du couple (sources: https://digiovannicoupleconseil.fr/methode-pour-desamorcer-des-conflits-en-couple/, https://www.puralist.fr/stonewalling-dans-un-couple-que-faire/, https://www.mieuxvivre.ma/famille/se-reconcilier-apres-une-dispute-la-methode-des-3-temps/)
- [2026-07-29 confirmé] Le ratio d'interactions positives/négatives (~5 pour 1) compte davantage pour la solidité du couple que la formulation exacte (« je » vs « tu », reproche vs compliment, humour) — les couples heureux ne suivent pas forcément la CNV à la lettre mais compensent largement leurs frictions par du positif (sources: https://yvondallaire.com/chronique-12-les-illusions-sur-la-communication/, https://www.masculin.com/psycho/842949-lhumour-dans-le-couple-larme-secrete-pour-booster-la-complicite-et-desamorcer-les-conflits-selon-les-psy/)
- [2026-07-29 confirmé] L'argent est un sujet de tension et d'autonomie majeur dans le couple moderne : ~40% des disputes conjugales concernent l'argent et 40% des couples ne discutent jamais de leur organisation financière, dans un contexte où l'autonomie financière (compte séparé) est de plus en plus la norme (sources: https://www.silvereco.fr/autonomie-argent-deces-ce-que-revele-cette-etude-sur-les-couples-en-2026/, https://culture-financiere.com/desequilibre-financier-couple/)
<!-- PATTERNS:END -->
