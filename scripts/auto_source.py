#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auto_source.py — Sélecteur automatique de sujets de contenu.

Lit data/subject-bank.json (50+ sujets tagués pilier/difficulté/CTA) et
data/anti-repetition.json (règles de cooldown + historique).
Score chaque sujet éligible et retourne le top 5.

Cooldowns : même pilier 4 jours, même CTA 2 jours, même sujet 30 jours.
Bonus : +30 contenu existant, +20 difficulté facile, +10 source originale,
+20 CTA sous-représenté.

Usage :
    python3 auto_source.py pick                # top 5 du jour
    python3 auto_source.py mark-used <id>      # après production : met à jour
                                               # subject-bank, anti-repetition
                                               # et memory/project-memory.md
"""
import json
import sys
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
BANK = RACINE / "data" / "subject-bank.json"
ANTI = RACINE / "data" / "anti-repetition.json"
PROJECT_MEMORY = RACINE / "memory" / "project-memory.md"


def charger():
    bank = json.loads(BANK.read_text(encoding="utf-8"))
    anti = json.loads(ANTI.read_text(encoding="utf-8"))
    return bank, anti


def jours_depuis(date_str):
    if not date_str:
        return 9999
    return (date.today() - datetime.strptime(date_str, "%Y-%m-%d").date()).days


def eligibles(bank, anti):
    """Filtre les sujets selon les 3 règles de cooldown."""
    regles = anti["cooldowns"]
    histo = anti["historique"]

    dernier_par_pilier = {}
    dernier_par_cta = {}
    dernier_par_sujet = {}
    for h in histo:
        dernier_par_pilier[h["pilier"]] = max(dernier_par_pilier.get(h["pilier"], h["date"]), h["date"])
        dernier_par_cta[h["cta"]] = max(dernier_par_cta.get(h["cta"], h["date"]), h["date"])
        dernier_par_sujet[h["id"]] = max(dernier_par_sujet.get(h["id"], h["date"]), h["date"])

    ok, exclus = [], []
    for s in bank["sujets"]:
        raisons = []
        if jours_depuis(dernier_par_sujet.get(s["id"])) < regles["meme_sujet_jours"]:
            raisons.append(f"sujet utilisé il y a < {regles['meme_sujet_jours']} j")
        if jours_depuis(dernier_par_pilier.get(s["pilier"])) < regles["meme_pilier_jours"]:
            raisons.append(f"pilier « {s['pilier']} » en cooldown ({regles['meme_pilier_jours']} j)")
        if jours_depuis(dernier_par_cta.get(s["cta"])) < regles["meme_cta_jours"]:
            raisons.append(f"CTA « {s['cta']} » en cooldown ({regles['meme_cta_jours']} j)")
        (exclus if raisons else ok).append((s, raisons))
    return [s for s, _ in ok], exclus


def scorer(sujets, anti):
    """Applique la grille de bonus."""
    fenetre = date.today() - timedelta(days=30)
    ctas_recents = Counter(
        h["cta"] for h in anti["historique"]
        if datetime.strptime(h["date"], "%Y-%m-%d").date() >= fenetre
    )
    moyenne_cta = (sum(ctas_recents.values()) / len(ctas_recents)) if ctas_recents else 0

    resultats = []
    for s in sujets:
        score, detail = 0, []
        if s.get("contenu_existant"):
            score += 30; detail.append("+30 contenu existant")
        if s.get("difficulte") == "facile":
            score += 20; detail.append("+20 facile")
        if s.get("source_originale"):
            score += 10; detail.append("+10 source originale")
        if ctas_recents.get(s["cta"], 0) < moyenne_cta or not ctas_recents:
            score += 20; detail.append("+20 CTA sous-représenté")
        resultats.append({"sujet": s, "score": score, "detail": detail})
    resultats.sort(key=lambda r: (-r["score"], r["sujet"]["id"]))
    return resultats


def cmd_pick():
    bank, anti = charger()
    ok, exclus = eligibles(bank, anti)
    if not ok:
        print("Aucun sujet éligible aujourd'hui (tous en cooldown).")
        for s, raisons in exclus[:5]:
            print(f"  - {s['id']} : {', '.join(raisons)}")
        sys.exit(1)

    top = scorer(ok, anti)[:5]
    print(f"TOP 5 DU {date.today().isoformat()}  ({len(ok)} éligibles / {len(bank['sujets'])} sujets)\n")
    for i, r in enumerate(top, 1):
        s = r["sujet"]
        print(f"{i}. [{r['score']:>3} pts] {s['id']} — {s['titre']}")
        print(f"      pilier: {s['pilier']} | difficulté: {s['difficulte']} | CTA: {s['cta']}")
        print(f"      {', '.join(r['detail']) or 'aucun bonus'}")
    print("\nAprès production : python3 auto_source.py mark-used <id>")


def cmd_mark_used(sujet_id):
    bank, anti = charger()
    sujet = next((s for s in bank["sujets"] if s["id"] == sujet_id), None)
    if not sujet:
        print(f"Sujet introuvable : {sujet_id}")
        sys.exit(1)

    aujourd_hui = date.today().isoformat()

    # 1. anti-repetition.json : historique
    anti["historique"].append(
        {"id": sujet_id, "pilier": sujet["pilier"], "cta": sujet["cta"], "date": aujourd_hui}
    )
    ANTI.write_text(json.dumps(anti, ensure_ascii=False, indent=2), encoding="utf-8")

    # 2. subject-bank.json : last_used + compteur
    sujet["last_used"] = aujourd_hui
    sujet["utilisations"] = sujet.get("utilisations", 0) + 1
    BANK.write_text(json.dumps(bank, ensure_ascii=False, indent=2), encoding="utf-8")

    # 3. memory/project-memory.md : journal de contenu
    if PROJECT_MEMORY.exists():
        contenu = PROJECT_MEMORY.read_text(encoding="utf-8")
        marqueur = "<!-- CONTENT-LOG:START -->"
        ligne = f"\n- [{aujourd_hui}] publié : {sujet['titre']} (pilier {sujet['pilier']}, CTA {sujet['cta']})"
        if marqueur in contenu:
            contenu = contenu.replace(marqueur, marqueur + ligne, 1)
            PROJECT_MEMORY.write_text(contenu, encoding="utf-8")

    print(f"✅ {sujet_id} marqué comme produit le {aujourd_hui}.")
    print("   Mis à jour : anti-repetition.json, subject-bank.json, memory/project-memory.md")


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("pick", "mark-used"):
        print(__doc__)
        sys.exit(1)
    if sys.argv[1] == "pick":
        cmd_pick()
    else:
        if len(sys.argv) < 3:
            print("Usage : python3 auto_source.py mark-used <id>")
            sys.exit(1)
        cmd_mark_used(sys.argv[2])


if __name__ == "__main__":
    main()
