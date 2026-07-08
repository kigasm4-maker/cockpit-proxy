#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
quality_gate.py — Quality gate pour contenu (français).
4 critères : densité de mots spécifiques (min 15%), mots vagues (max 10%),
longueur moyenne des phrases (cible 9 mots), détection de placeholders.
Score 0-100. Bloque (exit 1) si score < 60.

Usage :
    python3 quality_gate.py fichier.md
    echo "texte" | python3 quality_gate.py
"""
import re
import sys

SEUIL_PUBLICATION = 60
DENSITE_MIN = 0.15
VAGUE_MAX = 0.10
PHRASE_CIBLE = 9

MOTS_VAGUES = {
    "chose", "choses", "truc", "trucs", "vraiment", "assez", "plutôt",
    "peut-être", "beaucoup", "certains", "certaines", "divers", "diverses",
    "important", "importante", "importants", "intéressant", "intéressante",
    "incroyable", "génial", "super", "très", "quelque", "quelques",
    "globalement", "généralement", "souvent", "parfois", "notamment",
    "nombreux", "nombreuses", "différent", "différents", "différentes",
    "bon", "bonne", "meilleur", "meilleure", "efficace", "optimal",
    "simplement", "facilement", "rapidement", "clairement", "évidemment",
}

PLACEHOLDERS = [
    (r"\bTODO\b", "TODO"),
    (r"\bTBD\b", "TBD"),
    (r"\bFIXME\b", "FIXME"),
    (r"\bXXX+\b", "XXX"),
    (r"\blorem\b", "lorem ipsum", ),
    (r"\{\{[^}]*\}\}", "{{variable}}"),
    (r"\[(?:nom|date|lien|url|titre|insérer|à compléter|placeholder)[^\]]*\]", "[à compléter]"),
    (r"<(?:nom|date|lien|url|titre|insérer)[^>]*>", "<placeholder>"),
    (r"\.{4,}", "…… (points de suspension multiples)"),
]

MOTS_OUTILS = {
    "le", "la", "les", "un", "une", "des", "de", "du", "d", "l", "et", "ou",
    "à", "au", "aux", "en", "dans", "sur", "pour", "par", "avec", "sans",
    "que", "qui", "quoi", "dont", "où", "ne", "pas", "plus", "est", "sont",
    "a", "ont", "être", "avoir", "ce", "cette", "ces", "se", "sa", "son",
    "ses", "il", "elle", "on", "nous", "vous", "ils", "elles", "je", "tu",
    "mais", "donc", "car", "si", "comme", "y",
}


def tokenize(texte):
    return re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9€%°'']+", texte)


def est_specifique(mot, position_debut_phrase):
    """Un mot est 'spécifique' s'il porte de l'information concrète."""
    if re.search(r"[0-9€%°]", mot):
        return True  # chiffres, montants, pourcentages
    if mot[0].isupper() and not position_debut_phrase:
        return True  # nom propre en milieu de phrase
    if len(mot) >= 9 and mot.lower() not in MOTS_VAGUES:
        return True  # terme technique / précis
    return False


def analyser(texte):
    problemes = []
    scores = {}

    # Découpage en phrases
    phrases = [p.strip() for p in re.split(r"[.!?]+", texte) if p.strip()]
    mots = tokenize(texte)
    total = max(len(mots), 1)

    # --- Critère 1 : densité de mots spécifiques (min 15%) — 30 pts
    specifiques = 0
    for p in phrases:
        toks = tokenize(p)
        for i, m in enumerate(toks):
            if est_specifique(m, position_debut_phrase=(i == 0)):
                specifiques += 1
    densite = specifiques / total
    scores["densité"] = min(30, round(30 * densite / DENSITE_MIN))
    if densite < DENSITE_MIN:
        problemes.append(
            f"Densité de mots spécifiques : {densite:.0%} (min {DENSITE_MIN:.0%}). "
            f"→ Remplacer les généralités par des chiffres, noms, exemples concrets."
        )

    # --- Critère 2 : mots vagues (max 10%) — 25 pts
    vagues_trouves = [m for m in mots if m.lower() in MOTS_VAGUES]
    ratio_vague = len(vagues_trouves) / total
    if ratio_vague <= VAGUE_MAX:
        scores["vague"] = 25
    else:
        scores["vague"] = max(0, round(25 * (1 - (ratio_vague - VAGUE_MAX) / VAGUE_MAX)))
        top = sorted(set(v.lower() for v in vagues_trouves))[:8]
        problemes.append(
            f"Mots vagues : {ratio_vague:.0%} (max {VAGUE_MAX:.0%}). Trouvés : {', '.join(top)}. "
            f"→ Chaque mot vague doit être remplacé par une donnée ou supprimé."
        )

    # --- Critère 3 : longueur moyenne des phrases (cible 9 mots) — 25 pts
    if phrases:
        longueurs = [len(tokenize(p)) for p in phrases]
        moyenne = sum(longueurs) / len(longueurs)
        ecart = abs(moyenne - PHRASE_CIBLE)
        scores["phrases"] = max(0, round(25 * (1 - ecart / PHRASE_CIBLE)))
        if ecart > 3:
            direction = "raccourcir" if moyenne > PHRASE_CIBLE else "étoffer"
            longues = [p[:60] + "…" for p, l in zip(phrases, longueurs) if l > 20][:3]
            msg = (f"Longueur moyenne des phrases : {moyenne:.1f} mots (cible {PHRASE_CIBLE}). "
                   f"→ {direction.capitalize()} les phrases.")
            if longues:
                msg += " Phrases trop longues : " + " | ".join(longues)
            problemes.append(msg)
    else:
        scores["phrases"] = 0
        problemes.append("Aucune phrase détectée.")

    # --- Critère 4 : placeholders — 20 pts
    trouves = []
    for pattern, label in [(p[0], p[1]) for p in PLACEHOLDERS]:
        if re.search(pattern, texte, re.IGNORECASE):
            trouves.append(label)
    if not trouves:
        scores["placeholders"] = 20
    else:
        scores["placeholders"] = 0
        problemes.append(
            f"Placeholders détectés : {', '.join(trouves)}. "
            f"→ Compléter avant toute publication (bloquant)."
        )

    score_total = sum(scores.values())
    return score_total, scores, problemes


def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as f:
            texte = f.read()
    else:
        texte = sys.stdin.read()

    if not texte.strip():
        print("Texte vide — rien à évaluer.")
        sys.exit(1)

    score, details, problemes = analyser(texte)

    print("=" * 52)
    print("QUALITY GATE")
    print("=" * 52)
    for k, v in details.items():
        barre = {"densité": 30, "vague": 25, "phrases": 25, "placeholders": 20}[k]
        print(f"  {k:<14} {v:>3}/{barre}")
    print("-" * 52)
    print(f"  SCORE TOTAL    {score:>3}/100   (seuil : {SEUIL_PUBLICATION})")
    print("=" * 52)

    if problemes:
        print("\nProblèmes à corriger :")
        for i, p in enumerate(problemes, 1):
            print(f"  {i}. {p}")

    if score < SEUIL_PUBLICATION:
        print(f"\n❌ PUBLICATION BLOQUÉE (score {score} < {SEUIL_PUBLICATION})")
        sys.exit(1)
    print("\n✅ Gate franchi — publication autorisée.")
    sys.exit(0)


if __name__ == "__main__":
    main()
